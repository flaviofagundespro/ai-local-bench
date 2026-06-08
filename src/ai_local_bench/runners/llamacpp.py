from __future__ import annotations

import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

from ai_local_bench.runtime_metrics import (
    MemorySampler,
    make_process_memory_reader,
    make_windows_gpu_dedicated_memory_reader,
)
from ai_local_bench.schemas import BenchmarkResult


TOKEN_RATE_PATTERNS = [
    re.compile(r"eval rate:\s*([0-9.]+)\s*tokens/s", re.IGNORECASE),
    re.compile(r"eval time\s*=.*?([0-9.]+)\s*tokens per second", re.IGNORECASE),
    re.compile(r"tok/s[:=]\s*([0-9.]+)", re.IGNORECASE),
    re.compile(r"Generation:\s*([0-9.]+)\s*t/s", re.IGNORECASE),
]


def run_llamacpp_suite(
    suite: dict,
    system_info: dict[str, object],
    output_dir: Path,
) -> list[BenchmarkResult]:
    results = []
    config = suite["runner_config"]
    executable = Path(config["executable"])
    model_path = Path(config["model_path"])

    repetitions = int(suite.get("measured_runs", 5))
    warmups = int(suite.get("warmup_runs", 1))
    runs = [True] * warmups + [False] * repetitions

    for run_index, is_warmup in enumerate(runs, start=1):
        results.append(
            run_single_llamacpp_run(
                suite=suite,
                system_info=system_info,
                output_dir=output_dir,
                executable=executable,
                model_path=model_path,
                run_index=run_index,
                is_warmup=is_warmup,
            )
        )
    return results


def run_single_llamacpp_run(
    suite: dict,
    system_info: dict[str, object],
    output_dir: Path,
    executable: Path,
    model_path: Path,
    run_index: int,
    is_warmup: bool,
) -> BenchmarkResult:
    output_logs_dir = output_dir / "logs"
    output_logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_logs_dir / f"{suite['suite_name']}-run-{run_index}.log"

    result = _base_result(
        suite=suite,
        system_info=system_info,
        model_path=model_path,
        run_index=run_index,
        is_warmup=is_warmup,
        raw_log_path=str(log_path),
    )

    if not executable.exists():
        result.success = "false"
        result.error_type = "missing_executable"
        result.notes = f"Executable not found: {executable}"
        log_path.write_text(result.notes, encoding="utf-8")
        return result

    if not model_path.exists():
        result.success = "false"
        result.error_type = "missing_model"
        result.notes = f"Model not found: {model_path}"
        log_path.write_text(result.notes, encoding="utf-8")
        return result

    command = build_llamacpp_command(suite, executable, model_path)
    start = time.perf_counter()
    sampler = None
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        vram_reader = None
        if str(system_info.get("os_name", "")).lower() == "windows" and str(suite.get("backend", "")).lower() == "vulkan":
            vram_reader = make_windows_gpu_dedicated_memory_reader()
        sampler = MemorySampler(make_process_memory_reader(process.pid), vram_reader=vram_reader)
        sampler.start()
        stdout, stderr = process.communicate(timeout=int(suite["runner_config"].get("timeout_sec", 300)))
        elapsed = time.perf_counter() - start
        metrics = sampler.stop()
        log_path.write_text(_join_logs(command, stdout, stderr), encoding="utf-8")

        result.total_time_sec = f"{elapsed:.4f}"
        result.tokens_per_sec = parse_token_rate(stdout + "\n" + stderr)
        result.ram_peak_mb = metrics.ram_peak_mb
        result.vram_peak_mb = metrics.vram_peak_mb
        result.success = "true" if process.returncode == 0 else "false"
        result.error_type = "" if process.returncode == 0 else f"exit_code_{process.returncode}"
        result.notes = "completed" if process.returncode == 0 else "llama.cpp exited with non-zero status"
        return result
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - start
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if sampler:
            metrics = sampler.stop()
            result.ram_peak_mb = metrics.ram_peak_mb
            result.vram_peak_mb = metrics.vram_peak_mb
        process.kill()
        log_path.write_text(_join_logs(command, stdout, stderr), encoding="utf-8")
        result.total_time_sec = f"{elapsed:.4f}"
        result.success = "false"
        result.error_type = "timeout"
        result.notes = "llama.cpp execution timed out"
        return result


def build_llamacpp_command(suite: dict, executable: Path, model_path: Path) -> list[str]:
    workload = suite["workload"]
    config = suite["runner_config"]
    command = [
        str(executable),
        "-m",
        str(model_path),
        "-p",
        workload["prompt"],
        "-n",
        str(workload.get("max_tokens", 64)),
    ]
    executable_name = executable.name.lower()
    if executable_name in {"llama-cli", "llama-cli.exe", "llama-completion", "llama-completion.exe"}:
        extra_args = list(config.get("extra_args", []))
        if "-no-cnv" not in command and "-no-cnv" not in extra_args:
            command.append("-no-cnv")
        if "--no-warmup" not in command and "--no-warmup" not in extra_args:
            command.append("--no-warmup")
    if workload.get("temperature") is not None:
        command.extend(["--temp", str(workload["temperature"])])
    if workload.get("ctx_size") is not None:
        command.extend(["-c", str(workload["ctx_size"])])
    command.extend(config.get("extra_args", []))
    return command


def parse_token_rate(text: str) -> str:
    for pattern in TOKEN_RATE_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1)
    return ""


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
        frontend="llama.cpp",
        runner="llamacpp",
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


def _join_logs(command: list[str], stdout: str, stderr: str) -> str:
    payload = {
        "command": command,
        "stdout": stdout,
        "stderr": stderr,
    }
    return json.dumps(payload, indent=2)


def hash_file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
