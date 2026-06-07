from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from ai_local_bench.runners.ollama import parse_ollama_tokens_per_sec, run_ollama_suite


SYSTEM_INFO = {
    "os_name": "Windows",
    "os_version": "11",
    "cpu_name": "CPU",
    "gpus": [{"name": "GPU", "vendor": "AMD", "driver_version": "1.0"}],
}


def test_parse_ollama_tokens_per_sec() -> None:
    response = {"eval_count": 100, "eval_duration": 2_000_000_000}
    assert parse_ollama_tokens_per_sec(response) == "50.0000"


def test_run_ollama_suite_success(tmp_path: Path) -> None:
    suite = {
        "suite_name": "ollama-basic",
        "prompt_name": "ollama-basic",
        "backend": "cpu",
        "seed": "0",
        "warmup_runs": 1,
        "measured_runs": 1,
        "runner_config": {
            "base_url": "http://127.0.0.1:11434",
            "model": "tinyllama",
            "service_process_name": "",
        },
        "workload": {"prompt": "hello"},
    }

    def fake_urlopen(request, timeout=0):
        response = MagicMock()
        response.read.return_value = json.dumps(
            {"response": "ok", "eval_count": 100, "eval_duration": 2_000_000_000}
        ).encode("utf-8")
        response.__enter__.return_value = response
        response.__exit__.return_value = False
        return response

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        results = run_ollama_suite(suite, SYSTEM_INFO, tmp_path)

    assert all(result.success == "true" for result in results)
    assert results[0].tokens_per_sec == "50.0000"


def test_run_ollama_suite_connection_failure(tmp_path: Path) -> None:
    suite = {
        "suite_name": "ollama-basic",
        "prompt_name": "ollama-basic",
        "backend": "cpu",
        "seed": "0",
        "warmup_runs": 1,
        "measured_runs": 1,
        "runner_config": {
            "base_url": "http://127.0.0.1:11434",
            "model": "tinyllama",
            "service_process_name": "",
        },
        "workload": {"prompt": "hello"},
    }

    with patch("urllib.request.urlopen", side_effect=OSError("down")):
        results = run_ollama_suite(suite, SYSTEM_INFO, tmp_path)

    assert all(result.success == "false" for result in results)
