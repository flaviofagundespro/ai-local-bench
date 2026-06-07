from __future__ import annotations

import json
from pathlib import Path

from ai_local_bench.reporting import (
    render_summary_markdown,
    write_results_csv,
    write_results_jsonl,
)
from ai_local_bench.schemas import BenchmarkResult


def make_result() -> BenchmarkResult:
    return BenchmarkResult.create(
        os_name="Windows",
        runner="llamacpp",
        frontend="llama.cpp",
        backend="vulkan",
        workload_name="text-basic",
        success="true",
        total_time_sec="1.23",
        notes="sample",
    )


def test_write_jsonl_and_csv(tmp_path: Path) -> None:
    result = make_result()
    jsonl_path = tmp_path / "results.jsonl"
    csv_path = tmp_path / "results.csv"

    write_results_jsonl(jsonl_path, [result])
    write_results_csv(csv_path, [result])

    assert json.loads(jsonl_path.read_text(encoding="utf-8").splitlines()[0])["runner"] == "llamacpp"
    assert "run_id" in csv_path.read_text(encoding="utf-8")


def test_render_summary_markdown() -> None:
    markdown = render_summary_markdown([make_result()])
    assert "# AI Local Bench Summary" in markdown
    assert "text-basic" in markdown
