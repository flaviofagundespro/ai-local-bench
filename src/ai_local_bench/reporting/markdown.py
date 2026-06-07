from __future__ import annotations

from pathlib import Path

from ai_local_bench.schemas import BenchmarkResult


def render_summary_markdown(results: list[BenchmarkResult]) -> str:
    total_runs = len(results)
    success_count = sum(result.success.lower() == "true" for result in results)
    failed = total_runs - success_count

    lines = [
        "# AI Local Bench Summary",
        "",
        f"- Total runs: {total_runs}",
        f"- Successful runs: {success_count}",
        f"- Failed runs: {failed}",
        "",
        "| Workload | Runner | Backend | Success | Total Time (s) | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(
            "| {workload} | {runner} | {backend} | {success} | {time} | {notes} |".format(
                workload=result.workload_name,
                runner=result.runner,
                backend=result.backend,
                success=result.success,
                time=result.total_time_sec,
                notes=result.notes.replace("\n", " "),
            )
        )
    lines.append("")
    return "\n".join(lines)


def write_summary_markdown(path: Path, results: list[BenchmarkResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_summary_markdown(results), encoding="utf-8")
