from __future__ import annotations

from pathlib import Path

import pytest

from ai_local_bench.suite_validation import normalize_suite_paths, validate_suite_definition


def test_validate_llamacpp_suite() -> None:
    suite = {
        "suite_name": "text-basic",
        "prompt_name": "text-basic",
        "backend": "cpu",
        "warmup_runs": 1,
        "measured_runs": 5,
        "runner_config": {"executable": "x", "model_path": "y"},
        "workload": {"prompt": "hello", "max_tokens": 16},
    }
    validate_suite_definition(suite, "llamacpp")


def test_validate_suite_missing_field() -> None:
    suite = {"suite_name": "bad"}
    with pytest.raises(ValueError):
        validate_suite_definition(suite, "llamacpp")


def test_normalize_suite_paths(tmp_path: Path) -> None:
    suite_path = tmp_path / "suite.json"
    suite = {
        "suite_name": "image",
        "prompt_name": "image",
        "backend": "rocm",
        "warmup_runs": 1,
        "measured_runs": 5,
        "runner_config": {"base_url": "http://127.0.0.1:8188", "workflow_path": "workflow.json", "checkpoint": "x"},
        "workload": {"prompt": "hello", "width": 1, "height": 1, "steps": 1, "cfg": 1, "sampler": "e", "scheduler": "n"},
    }
    normalized = normalize_suite_paths(suite, suite_path)
    assert normalized["runner_config"]["workflow_path"].startswith(str(tmp_path))
