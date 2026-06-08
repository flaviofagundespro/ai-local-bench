from __future__ import annotations

import hashlib
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from ai_local_bench.runtime_metrics import (
    MemorySampler,
    make_process_memory_reader,
    make_windows_gpu_dedicated_memory_reader,
)
from ai_local_bench.schemas import BenchmarkResult


def run_llamacpp_server_suite(
    suite: dict,
    system_info: dict[str, object],
    output_dir: Path,
) -> list[BenchmarkResult]:
    config = suite["runner_config"]
    executable = Path(config["executable"])
    model_path = Path(config["model_path"])
    output_logs_dir = output_dir / "logs"
    output_logs_dir.mkdir(parents=True, exist_ok=True)
    server_log_path = output_logs_dir / f"{suite['suite_name']}-server.log"

    if not executable.exists() or not model_path.exists():
        return _missing_dependency_results(suite, system_info, output_dir, executable, model_path)

    base_url = config.get("base_url", "http://127.0.0.1:8080")
    host = config.get("host", "127.0.0.1")
    port = int(config.get("port", 8080))
    server_command = build_llamacpp_server_command(suite, executable, model_path)

    with server_log_path.open("w", encoding="utf-8") as server_log:
        process = subprocess.Popen(
            server_command,
            stdout=server_log,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            wait_for_server_ready(base_url, timeout=int(config.get("server_start_timeout_sec", 120)))
            return run_server_requests(suite, system_info, output_dir, process.pid, base_url, model_path)
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)


def run_server_requests(
    suite: dict,
    system_info: dict[str, object],
    output_dir: Path,
    server_pid: int,
    base_url: str,
    model_path: Path,
) -> list[BenchmarkResult]:
    results = []
    repetitions = int(suite.get("measured_runs", 5))
    warmups = int(suite.get("warmup_runs", 1))
    runs = [True] * warmups + [False] * repetitions

    for run_index, is_warmup in enumerate(runs, start=1):
        results.append(
            run_single_server_request(
                suite=suite,
                system_info=system_info,
                output_dir=output_dir,
                server_pid=server_pid,
                base_url=base_url,
                model_path=model_path,
                run_index=run_index,
                is_warmup=is_warmup,
            )
        )

        idle_seconds = suite["runner_config"].get("idle_after_run_sec")
        if idle_seconds and run_index != len(runs):
            time.sleep(float(idle_seconds))

    return results


def run_single_server_request(
    suite: dict,
    system_info: dict[str, object],
    output_dir: Path,
    server_pid: int,
    base_url: str,
    model_path: Path,
    run_index: int,
    is_warmup: bool,
) -> BenchmarkResult:
    output_logs_dir = output_dir / "logs"
    output_logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_logs_dir / f"{suite['suite_name']}-run-{run_index}.json"

    result = _base_result(
        suite=suite,
        system_info=system_info,
        model_path=model_path,
        run_index=run_index,
        is_warmup=is_warmup,
        raw_log_path=str(log_path),
    )

    vram_reader = None
    if str(system_info.get("os_name", "")).lower() == "windows" and str(suite.get("backend", "")).lower() == "vulkan":
        vram_reader = make_windows_gpu_dedicated_memory_reader()
    sampler = MemorySampler(make_process_memory_reader(server_pid), vram_reader=vram_reader)
    sampler.start()

    start = time.perf_counter()
    try:
        payload = build_server_payload(suite)
        response = http_json(
            f"{base_url.rstrip('/')}/completion",
            payload=payload,
            timeout=int(suite["runner_config"].get("timeout_sec", 300)),
        )
        elapsed = time.perf_counter() - start
        metrics = sampler.stop()
        log_path.write_text(json.dumps(response, indent=2), encoding="utf-8")

        result.total_time_sec = f"{elapsed:.4f}"
        result.tokens_per_sec = parse_server_tokens_per_sec(response)
        result.items_per_sec = f"{1 / elapsed:.6f}" if elapsed > 0 else ""
        result.ram_peak_mb = metrics.ram_peak_mb
        result.vram_peak_mb = metrics.vram_peak_mb
        result.success = "true" if validate_response_content(suite, response) else "false"
        result.error_type = "" if result.success == "true" else "validation_error"
        result.notes = summarize_server_notes(suite, response)
        return result
    except (urllib.error.URLError, OSError) as exc:
        elapsed = time.perf_counter() - start
        metrics = sampler.stop()
        result.total_time_sec = f"{elapsed:.4f}"
        result.ram_peak_mb = metrics.ram_peak_mb
        result.vram_peak_mb = metrics.vram_peak_mb
        result.success = "false"
        result.error_type = "connection_error"
        result.notes = str(getattr(exc, "reason", exc))
        log_path.write_text(result.notes, encoding="utf-8")
        return result
    except TimeoutError as exc:
        elapsed = time.perf_counter() - start
        metrics = sampler.stop()
        result.total_time_sec = f"{elapsed:.4f}"
        result.ram_peak_mb = metrics.ram_peak_mb
        result.vram_peak_mb = metrics.vram_peak_mb
        result.success = "false"
        result.error_type = "timeout"
        result.notes = str(exc)
        log_path.write_text(result.notes, encoding="utf-8")
        return result


def build_llamacpp_server_command(suite: dict, executable: Path, model_path: Path) -> list[str]:
    config = suite["runner_config"]
    command = [
        str(executable),
        "-m",
        str(model_path),
        "-c",
        str(config.get("ctx_size", suite["workload"].get("ctx_size", 4096))),
        "--host",
        str(config.get("host", "127.0.0.1")),
        "--port",
        str(config.get("port", 8080)),
        "--no-warmup",
    ]
    ngl = config.get("ngl")
    if ngl is not None:
        command.extend(["-ngl", str(ngl)])
    command.extend(config.get("server_args", []))
    return command


def build_server_payload(suite: dict) -> dict:
    workload = suite["workload"]
    payload = {
        "prompt": workload["prompt"],
        "n_predict": int(workload.get("max_tokens", 64)),
        "temperature": float(workload.get("temperature", 0.0)),
        "top_p": float(workload.get("top_p", 1.0)),
        "stream": False,
    }
    if workload.get("top_k") is not None:
        payload["top_k"] = int(workload["top_k"])
    if workload.get("seed") is not None:
        payload["seed"] = int(workload["seed"])
    if workload.get("stop") is not None:
        payload["stop"] = workload["stop"]
    return payload


def wait_for_server_ready(base_url: str, timeout: int) -> None:
    deadline = time.perf_counter() + timeout
    last_error = "server did not become ready"
    while time.perf_counter() < deadline:
        try:
            request = urllib.request.Request(f"{base_url.rstrip('/')}/health", method="GET")
            with urllib.request.urlopen(request, timeout=2) as response:
                if response.status == 200:
                    return
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            time.sleep(0.5)
    raise TimeoutError(last_error)


def http_json(url: str, payload: dict, timeout: int) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise urllib.error.URLError(body) from exc


def parse_server_tokens_per_sec(response: dict) -> str:
    timings = response.get("timings", {})
    predicted = timings.get("predicted_per_second")
    if predicted:
        return f"{float(predicted):.4f}"
    return ""


def validate_response_content(suite: dict, response: dict) -> bool:
    expected = suite["workload"].get("expected_output")
    if not expected:
        return True
    content = str(response.get("content", "")).strip()
    return content == str(expected)


def summarize_server_notes(suite: dict, response: dict) -> str:
    content = str(response.get("content", "")).strip()
    timings = response.get("timings", {})
    cache_n = timings.get("cache_n", 0)
    expected = suite["workload"].get("expected_output")
    parts = [f"content={content!r}", f"cache_n={cache_n}"]
    if expected is not None:
        parts.append(f"expected={expected!r}")
    return "; ".join(parts)


def _missing_dependency_results(
    suite: dict,
    system_info: dict[str, object],
    output_dir: Path,
    executable: Path,
    model_path: Path,
) -> list[BenchmarkResult]:
    repetitions = int(suite.get("measured_runs", 5))
    warmups = int(suite.get("warmup_runs", 1))
    runs = [True] * warmups + [False] * repetitions
    results = []
    for run_index, is_warmup in enumerate(runs, start=1):
        log_path = output_dir / "logs" / f"{suite['suite_name']}-run-{run_index}.log"
        result = _base_result(
            suite=suite,
            system_info=system_info,
            model_path=model_path,
            run_index=run_index,
            is_warmup=is_warmup,
            raw_log_path=str(log_path),
        )
        if not executable.exists():
            result.error_type = "missing_executable"
            result.notes = f"Executable not found: {executable}"
        else:
            result.error_type = "missing_model"
            result.notes = f"Model not found: {model_path}"
        result.success = "false"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(result.notes, encoding="utf-8")
        results.append(result)
    return results


def _base_result(
    suite: dict,
    system_info: dict[str, object],
    model_path: Path,
    run_index: int,
    is_warmup: bool,
    raw_log_path: str,
) -> BenchmarkResult:
    first_gpu = (system_info.get("gpus") or [{}])[0]
    return BenchmarkResult.create(
        os_name=str(system_info.get("os_name", "")),
        os_version=str(system_info.get("os_version", "")),
        cpu_name=str(system_info.get("cpu_name", "")),
        gpu_name=str(first_gpu.get("name", "")),
        gpu_vendor=str(first_gpu.get("vendor", "")),
        gpu_driver=str(first_gpu.get("driver_version", "")),
        backend=str(suite.get("backend", "")),
        frontend="llama.cpp-server",
        runner="llamacpp_server",
        model_name=model_path.name,
        model_hash=hash_file_sha256(model_path) if model_path.exists() else "",
        workload_name=str(suite.get("suite_name", "")),
        prompt_name=str(suite.get("prompt_name", suite.get("suite_name", ""))),
        seed=str(suite.get("seed", "")),
        batch_size="1",
        run_index=str(run_index),
        warmup=str(is_warmup).lower(),
        success="false",
        error_type="",
        notes="",
        raw_log_path=raw_log_path,
    )


def hash_file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
