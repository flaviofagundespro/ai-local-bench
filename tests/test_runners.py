from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from ai_local_bench.runners.comfyui import run_comfyui_suite, substitute_workflow_values
from ai_local_bench.runners.llamacpp import build_llamacpp_command, parse_token_rate, run_llamacpp_suite
from ai_local_bench.runtime_metrics import PeakMetrics


SYSTEM_INFO = {
    "os_name": "Windows",
    "os_version": "11",
    "cpu_name": "CPU",
    "gpus": [{"name": "GPU", "vendor": "AMD", "driver_version": "1.0"}],
}


def test_build_llamacpp_command() -> None:
    suite = {
        "runner_config": {"extra_args": ["--threads", "8"]},
        "workload": {"prompt": "hello", "max_tokens": 12, "temperature": 0.1, "ctx_size": 2048},
    }
    command = build_llamacpp_command(suite, Path("llama-cli"), Path("model.gguf"))
    assert command[0] == "llama-cli"
    assert "--threads" in command


def test_parse_token_rate() -> None:
    assert parse_token_rate("eval rate: 88.90 tokens/s") == "88.90"
    assert parse_token_rate("[ Prompt: 162.7 t/s | Generation: 34.3 t/s ]") == "34.3"


def test_run_llamacpp_suite_missing_model(tmp_path: Path) -> None:
    fake_executable = tmp_path / "llama-cli"
    fake_executable.write_text("binary", encoding="utf-8")
    suite = {
        "suite_name": "text-basic",
        "prompt_name": "text-basic",
        "backend": "cpu",
        "seed": "0",
        "warmup_runs": 1,
        "measured_runs": 1,
        "runner_config": {
            "executable": str(fake_executable),
            "model_path": str(tmp_path / "missing.gguf"),
            "timeout_sec": 1,
            "extra_args": [],
        },
        "workload": {"prompt": "hello", "max_tokens": 16},
    }
    results = run_llamacpp_suite(suite, SYSTEM_INFO, tmp_path)
    assert len(results) == 2
    assert all(result.error_type == "missing_model" for result in results)


def test_run_llamacpp_suite_success(tmp_path: Path) -> None:
    fake_executable = tmp_path / "llama-cli"
    fake_model = tmp_path / "model.gguf"
    fake_executable.write_text("binary", encoding="utf-8")
    fake_model.write_text("model", encoding="utf-8")
    suite = {
        "suite_name": "text-basic",
        "prompt_name": "text-basic",
        "backend": "cpu",
        "seed": "0",
        "warmup_runs": 1,
        "measured_runs": 1,
        "runner_config": {
            "executable": str(fake_executable),
            "model_path": str(fake_model),
            "timeout_sec": 1,
            "extra_args": [],
        },
        "workload": {"prompt": "hello", "max_tokens": 16},
    }
    with patch("subprocess.Popen") as mocked_popen:
        mocked_process = mocked_popen.return_value
        mocked_process.pid = 1234
        mocked_process.communicate.return_value = ("eval rate: 77.70 tokens/s", "")
        mocked_process.returncode = 0
        results = run_llamacpp_suite(suite, SYSTEM_INFO, tmp_path)

    assert all(result.success == "true" for result in results)
    assert results[0].tokens_per_sec == "77.70"


def test_run_llamacpp_suite_windows_vulkan_records_vram(tmp_path: Path) -> None:
    fake_executable = tmp_path / "llama-cli"
    fake_model = tmp_path / "model.gguf"
    fake_executable.write_text("binary", encoding="utf-8")
    fake_model.write_text("model", encoding="utf-8")
    suite = {
        "suite_name": "text-basic",
        "prompt_name": "text-basic",
        "backend": "vulkan",
        "seed": "0",
        "warmup_runs": 1,
        "measured_runs": 1,
        "runner_config": {
            "executable": str(fake_executable),
            "model_path": str(fake_model),
            "timeout_sec": 1,
            "extra_args": [],
        },
        "workload": {"prompt": "hello", "max_tokens": 16},
    }

    fake_sampler = MagicMock()
    fake_sampler.stop.return_value = PeakMetrics(ram_peak_mb="10", vram_peak_mb="2048")

    with patch("subprocess.Popen") as mocked_popen, patch(
        "ai_local_bench.runners.llamacpp.MemorySampler",
        return_value=fake_sampler,
    ), patch(
        "ai_local_bench.runners.llamacpp.make_windows_gpu_dedicated_memory_reader",
        return_value=lambda: 2048 * 1024 * 1024,
    ):
        mocked_process = mocked_popen.return_value
        mocked_process.pid = 1234
        mocked_process.communicate.return_value = ("[ Prompt: 100.0 t/s | Generation: 40.0 t/s ]", "")
        mocked_process.returncode = 0
        results = run_llamacpp_suite(suite, SYSTEM_INFO, tmp_path)

    assert all(result.success == "true" for result in results)
    assert results[0].vram_peak_mb == "2048"


def test_substitute_workflow_values() -> None:
    workflow = {"node": {"prompt": "${prompt}", "steps": "${steps}"}}
    suite = {"seed": "1", "workload": {"prompt": "hello", "steps": 20}}
    updated = substitute_workflow_values(workflow, suite)
    assert updated["node"]["prompt"] == "hello"
    assert updated["node"]["steps"] == 20


def test_run_comfyui_suite_missing_workflow(tmp_path: Path) -> None:
    suite = {
        "suite_name": "image-comfyui-basic",
        "prompt_name": "image-comfyui-basic",
        "backend": "rocm",
        "seed": "1",
        "warmup_runs": 1,
        "measured_runs": 1,
        "runner_config": {
            "base_url": "http://127.0.0.1:8188",
            "workflow_path": str(tmp_path / "missing.json"),
            "checkpoint": "model.safetensors",
        },
        "workload": {"prompt": "hello", "width": 512, "height": 512, "steps": 20, "cfg": 7, "sampler": "euler", "scheduler": "normal"},
    }
    results = run_comfyui_suite(suite, SYSTEM_INFO, tmp_path)
    assert len(results) == 2
    assert all(result.error_type == "missing_workflow" for result in results)


def test_run_comfyui_suite_success(tmp_path: Path) -> None:
    workflow_path = tmp_path / "workflow.json"
    workflow_path.write_text(json.dumps({"test": "${prompt}"}), encoding="utf-8")
    suite = {
        "suite_name": "image-comfyui-basic",
        "prompt_name": "image-comfyui-basic",
        "backend": "rocm",
        "seed": "1",
        "warmup_runs": 1,
        "measured_runs": 1,
        "runner_config": {
            "base_url": "http://127.0.0.1:8188",
            "workflow_path": str(workflow_path),
            "checkpoint": "model.safetensors",
            "poll_timeout_sec": 1,
            "poll_interval_sec": 0.01,
        },
        "workload": {
            "prompt": "hello",
            "width": 512,
            "height": 512,
            "steps": 20,
            "cfg": 7,
            "sampler": "euler",
            "scheduler": "normal",
            "batch_size": 1,
        },
    }

    def fake_urlopen(request, timeout=0):
        url = request.full_url
        response = MagicMock()
        if url.endswith("/prompt"):
            response.read.return_value = json.dumps({"prompt_id": "abc"}).encode("utf-8")
        elif "/history/" in url:
            response.read.return_value = json.dumps(
                {
                    "abc": {
                        "outputs": {
                            "9": {
                                "images": [
                                    {"filename": "image.png", "subfolder": "", "type": "output"}
                                ]
                            }
                        }
                    }
                }
            ).encode("utf-8")
        else:
            response.read.return_value = b"PNGDATA"
        response.__enter__.return_value = response
        response.__exit__.return_value = False
        return response

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        results = run_comfyui_suite(suite, SYSTEM_INFO, tmp_path)

    assert all(result.success == "true" for result in results)
    assert "image-comfyui-basic-run-1-1.png" in results[0].output_path
