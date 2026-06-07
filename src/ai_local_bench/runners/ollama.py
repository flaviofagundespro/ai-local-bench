from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from ai_local_bench.runtime_metrics import MemorySampler, make_process_name_memory_reader
from ai_local_bench.schemas import BenchmarkResult


def run_ollama_suite(
    suite: dict,
    system_info: dict[str, object],
    output_dir: Path,
) -> list[BenchmarkResult]:
    results = []
    repetitions = int(suite.get("measured_runs", 5))
    warmups = int(suite.get("warmup_runs", 1))
    runs = [True] * warmups + [False] * repetitions

    for run_index, is_warmup in enumerate(runs, start=1):
        results.append(
            run_single_ollama_run(
                suite=suite,
                system_info=system_info,
                output_dir=output_dir,
                run_index=run_index,
                is_warmup=is_warmup,
            )
        )
    return results


def run_single_ollama_run(
    suite: dict,
    system_info: dict[str, object],
    output_dir: Path,
    run_index: int,
    is_warmup: bool,
) -> BenchmarkResult:
    output_logs_dir = output_dir / "logs"
    output_logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_logs_dir / f"{suite['suite_name']}-run-{run_index}.json"
    result = _base_result(suite, system_info, run_index, is_warmup, str(log_path))

    sampler = None
    service_process_name = suite["runner_config"].get("service_process_name", "ollama")
    if service_process_name:
        sampler = MemorySampler(make_process_name_memory_reader(service_process_name))
        sampler.start()

    start = time.perf_counter()
    try:
        payload = {
            "model": suite["runner_config"]["model"],
            "prompt": suite["workload"]["prompt"],
            "stream": False,
            "options": suite["runner_config"].get("options", {}),
        }
        response = http_json(
            f"{suite['runner_config']['base_url'].rstrip('/')}/api/generate",
            payload=payload,
            timeout=int(suite["runner_config"].get("timeout_sec", 300)),
        )
        elapsed = time.perf_counter() - start
        metrics = sampler.stop() if sampler else None

        log_path.write_text(json.dumps(response, indent=2), encoding="utf-8")
        result.total_time_sec = f"{elapsed:.4f}"
        result.tokens_per_sec = parse_ollama_tokens_per_sec(response)
        result.items_per_sec = f"{1 / elapsed:.6f}" if elapsed > 0 else ""
        if metrics:
            result.ram_peak_mb = metrics.ram_peak_mb
        result.success = "true"
        result.notes = "completed"
        return result
    except (urllib.error.URLError, OSError) as exc:
        elapsed = time.perf_counter() - start
        metrics = sampler.stop() if sampler else None
        result.total_time_sec = f"{elapsed:.4f}"
        if metrics:
            result.ram_peak_mb = metrics.ram_peak_mb
        result.success = "false"
        result.error_type = "connection_error"
        result.notes = str(getattr(exc, "reason", exc))
        log_path.write_text(result.notes, encoding="utf-8")
        return result
    except TimeoutError as exc:
        elapsed = time.perf_counter() - start
        metrics = sampler.stop() if sampler else None
        result.total_time_sec = f"{elapsed:.4f}"
        if metrics:
            result.ram_peak_mb = metrics.ram_peak_mb
        result.success = "false"
        result.error_type = "timeout"
        result.notes = str(exc)
        log_path.write_text(result.notes, encoding="utf-8")
        return result


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


def parse_ollama_tokens_per_sec(response: dict) -> str:
    eval_count = response.get("eval_count")
    eval_duration = response.get("eval_duration")
    if eval_count and eval_duration:
        seconds = float(eval_duration) / 1_000_000_000
        if seconds > 0:
            return f"{float(eval_count) / seconds:.4f}"
    return ""


def _base_result(
    suite: dict,
    system_info: dict[str, object],
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
        frontend="Ollama",
        runner="ollama",
        model_name=str(suite["runner_config"].get("model", "")),
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
