from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from ai_local_bench.cli import build_parser, main


def test_parser_builds() -> None:
    parser = build_parser()
    assert parser.prog == "ai-local-bench"


def test_main_without_args_returns_success(capsys) -> None:
    exit_code = main([])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "usage:" in captured.out


def test_detect_placeholder(capsys) -> None:
    exit_code = main(["detect"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "os_name:" in captured.out


def test_run_placeholder(capsys) -> None:
    suite_path = Path("tests/tmp-suite.json")
    suite_data = {
        "suite_name": "text-basic",
        "prompt_name": "text-basic",
        "backend": "cpu",
        "seed": "0",
        "warmup_runs": 1,
        "measured_runs": 1,
        "runner_config": {
            "executable": "missing/llama-cli",
            "model_path": "missing/model.gguf",
            "timeout_sec": 1,
            "extra_args": [],
        },
        "workload": {"prompt": "hello", "max_tokens": 16},
    }
    suite_path.write_text(json.dumps(suite_data), encoding="utf-8")
    try:
        exit_code = main(
            [
                "run",
                "--suite",
                "text-basic",
                "--runner",
                "llamacpp",
                "--suite-file",
                str(suite_path),
            ]
        )
    finally:
        suite_path.unlink(missing_ok=True)
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "results=2" in captured.out
    assert "run_dir=results" in captured.out


def test_summarize_placeholder(capsys) -> None:
    with patch("ai_local_bench.cli.write_summary_markdown") as mocked_write, patch(
        "ai_local_bench.reporting.jsonl_writer.load_results_jsonl", return_value=[]
    ):
        exit_code = main(
            [
                "summarize",
                "--input",
                "results/raw/sample.jsonl",
                "--output",
                "results/reports/summary.md",
            ]
        )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "output=results" in captured.out
    mocked_write.assert_called_once()


def test_detect_json_output(capsys) -> None:
    exit_code = main(["detect", "--format", "json"])
    captured = capsys.readouterr()
    assert exit_code == 0
    parsed = json.loads(captured.out)
    assert "os_name" in parsed
