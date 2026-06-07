from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from ai_local_bench.runtime_metrics import MemorySampler, make_process_name_memory_reader
from ai_local_bench.schemas import BenchmarkResult


def run_comfyui_suite(
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
            run_single_comfyui_run(
                suite=suite,
                system_info=system_info,
                output_dir=output_dir,
                run_index=run_index,
                is_warmup=is_warmup,
            )
        )
    return results


def run_single_comfyui_run(
    suite: dict,
    system_info: dict[str, object],
    output_dir: Path,
    run_index: int,
    is_warmup: bool,
) -> BenchmarkResult:
    workflow_path = Path(suite["runner_config"]["workflow_path"])
    output_logs_dir = output_dir / "logs"
    output_images_dir = output_dir / "images"
    output_logs_dir.mkdir(parents=True, exist_ok=True)
    output_images_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_logs_dir / f"{suite['suite_name']}-run-{run_index}.json"

    result = _base_result(
        suite=suite,
        system_info=system_info,
        run_index=run_index,
        is_warmup=is_warmup,
        raw_log_path=str(log_path),
    )

    if not workflow_path.exists():
        result.success = "false"
        result.error_type = "missing_workflow"
        result.notes = f"Workflow not found: {workflow_path}"
        log_path.write_text(result.notes, encoding="utf-8")
        return result

    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    workflow = substitute_workflow_values(workflow, suite)
    base_url = suite["runner_config"]["base_url"].rstrip("/")
    sampler = None
    service_process_name = suite["runner_config"].get("service_process_name")
    if service_process_name:
        sampler = MemorySampler(make_process_name_memory_reader(service_process_name))
        sampler.start()

    start = time.perf_counter()
    try:
        prompt_response = http_json(
            f"{base_url}/prompt",
            method="POST",
            payload={"prompt": workflow},
            timeout=int(suite["runner_config"].get("timeout_sec", 300)),
        )
        prompt_id = prompt_response["prompt_id"]
        history = poll_history(
            base_url=base_url,
            prompt_id=prompt_id,
            timeout_sec=int(suite["runner_config"].get("poll_timeout_sec", 300)),
            poll_interval=float(suite["runner_config"].get("poll_interval_sec", 1.0)),
        )
        elapsed = time.perf_counter() - start
        metrics = sampler.stop() if sampler else None
        log_payload = {
            "prompt_response": prompt_response,
            "history": history,
        }
        log_path.write_text(json.dumps(log_payload, indent=2), encoding="utf-8")

        image_paths = collect_output_images(
            base_url=base_url,
            history=history,
            output_dir=output_images_dir,
            prefix=f"{suite['suite_name']}-run-{run_index}",
        )

        result.total_time_sec = f"{elapsed:.4f}"
        result.items_per_sec = f"{1 / elapsed:.6f}" if elapsed > 0 else ""
        if metrics:
            result.ram_peak_mb = metrics.ram_peak_mb
        result.output_path = ";".join(str(path) for path in image_paths)
        result.success = "true"
        result.notes = "completed"
        return result
    except (KeyError, urllib.error.URLError, TimeoutError, RuntimeError) as exc:
        elapsed = time.perf_counter() - start
        metrics = sampler.stop() if sampler else None
        result.total_time_sec = f"{elapsed:.4f}"
        if metrics:
            result.ram_peak_mb = metrics.ram_peak_mb
        result.success = "false"
        result.error_type = exc.__class__.__name__.lower()
        result.notes = str(exc)
        log_path.write_text(result.notes, encoding="utf-8")
        return result


def substitute_workflow_values(workflow: dict, suite: dict) -> dict:
    runner_config = suite.get("runner_config", {})
    substitutions = {
        "${prompt}": str(suite["workload"]["prompt"]),
        "${seed}": str(suite.get("seed", "")),
        "${steps}": str(suite["workload"].get("steps", "")),
        "${cfg}": str(suite["workload"].get("cfg", "")),
        "${sampler}": str(suite["workload"].get("sampler", "")),
        "${scheduler}": str(suite["workload"].get("scheduler", "")),
        "${width}": str(suite["workload"].get("width", "")),
        "${height}": str(suite["workload"].get("height", "")),
        "${checkpoint}": str(runner_config.get("checkpoint", "")),
    }

    def transform(value: object) -> object:
        if isinstance(value, dict):
            return {key: transform(inner) for key, inner in value.items()}
        if isinstance(value, list):
            return [transform(item) for item in value]
        if isinstance(value, str):
            stripped = value.strip()
            if stripped in substitutions:
                replacement = substitutions[stripped]
                if replacement.isdigit():
                    return int(replacement)
                try:
                    return float(replacement)
                except ValueError:
                    return replacement
            return value
        return value

    return transform(workflow)


def http_json(url: str, method: str = "GET", payload: dict | None = None, timeout: int = 30) -> dict:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def poll_history(base_url: str, prompt_id: str, timeout_sec: int, poll_interval: float) -> dict:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        history = http_json(f"{base_url}/history/{prompt_id}")
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(poll_interval)
    raise TimeoutError(f"ComfyUI history polling timed out for prompt_id={prompt_id}")


def collect_output_images(base_url: str, history: dict, output_dir: Path, prefix: str) -> list[Path]:
    saved_paths = []
    outputs = history.get("outputs", {})
    image_index = 0
    for node_output in outputs.values():
        for image in node_output.get("images", []):
            query = urllib.parse.urlencode(
                {
                    "filename": image.get("filename", ""),
                    "subfolder": image.get("subfolder", ""),
                    "type": image.get("type", "output"),
                }
            )
            url = f"{base_url}/view?{query}"
            request = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(request, timeout=30) as response:
                image_index += 1
                suffix = Path(image.get("filename", f"image-{image_index}.png")).suffix or ".png"
                destination = output_dir / f"{prefix}-{image_index}{suffix}"
                destination.write_bytes(response.read())
                saved_paths.append(destination)
    return saved_paths


def _base_result(
    suite: dict,
    system_info: dict[str, object],
    run_index: int,
    is_warmup: bool,
    raw_log_path: str,
) -> BenchmarkResult:
    first_gpu = (system_info.get("gpus") or [{}])[0]
    workload = suite["workload"]
    return BenchmarkResult.create(
        os_name=str(system_info.get("os_name", "")),
        os_version=str(system_info.get("os_version", "")),
        cpu_name=str(system_info.get("cpu_name", "")),
        gpu_name=str(first_gpu.get("name", "")),
        gpu_vendor=str(first_gpu.get("vendor", "")),
        gpu_driver=str(first_gpu.get("driver_version", "")),
        backend=str(suite.get("backend", "")),
        frontend="ComfyUI",
        runner="comfyui",
        model_name=str(suite["runner_config"].get("checkpoint", "")),
        model_hash="",
        workload_name=str(suite.get("suite_name", "")),
        prompt_name=str(suite.get("prompt_name", suite.get("suite_name", ""))),
        seed=str(suite.get("seed", "")),
        width=str(workload.get("width", "")),
        height=str(workload.get("height", "")),
        steps=str(workload.get("steps", "")),
        cfg=str(workload.get("cfg", "")),
        sampler=str(workload.get("sampler", "")),
        scheduler=str(workload.get("scheduler", "")),
        batch_size=str(workload.get("batch_size", 1)),
        run_index=str(run_index),
        warmup=str(is_warmup).lower(),
        success="false",
        error_type="",
        notes="",
        raw_log_path=raw_log_path,
    )
