from __future__ import annotations

from pathlib import Path


def validate_suite_definition(suite: dict, runner_name: str) -> None:
    required_top_level = [
        "suite_name",
        "prompt_name",
        "backend",
        "warmup_runs",
        "measured_runs",
        "runner_config",
        "workload",
    ]
    for field in required_top_level:
        if field not in suite:
            raise ValueError(f"Suite is missing required field: {field}")

    if runner_name == "llamacpp":
        _require_fields(suite["runner_config"], ["executable", "model_path"], "runner_config")
        _require_fields(suite["workload"], ["prompt", "max_tokens"], "workload")
    elif runner_name == "llamacpp_server":
        _require_fields(suite["runner_config"], ["executable", "model_path"], "runner_config")
        _require_fields(suite["workload"], ["prompt", "max_tokens"], "workload")
    elif runner_name == "comfyui":
        _require_fields(suite["runner_config"], ["base_url", "workflow_path", "checkpoint"], "runner_config")
        _require_fields(
            suite["workload"],
            ["prompt", "width", "height", "steps", "cfg", "sampler", "scheduler"],
            "workload",
        )
    elif runner_name == "ollama":
        _require_fields(suite["runner_config"], ["base_url", "model"], "runner_config")
        _require_fields(suite["workload"], ["prompt"], "workload")
    else:
        raise ValueError(f"Unsupported runner: {runner_name}")


def normalize_suite_paths(suite: dict, suite_path: Path | None) -> dict:
    if suite_path is None:
        return suite

    suite = dict(suite)
    suite["runner_config"] = dict(suite["runner_config"])
    workflow_path = suite["runner_config"].get("workflow_path")
    model_path = suite["runner_config"].get("model_path")
    if workflow_path and not Path(workflow_path).is_absolute():
        suite["runner_config"]["workflow_path"] = str((suite_path.parent / workflow_path).resolve())
    if model_path and not Path(model_path).is_absolute():
        suite["runner_config"]["model_path"] = str((suite_path.parent / model_path).resolve())
    return suite


def _require_fields(payload: dict, fields: list[str], label: str) -> None:
    for field in fields:
        if field not in payload:
            raise ValueError(f"{label} is missing required field: {field}")
