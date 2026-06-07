from __future__ import annotations

import json
from pathlib import Path

from ai_local_bench.schemas import BenchmarkResult


def write_results_jsonl(path: Path, results: list[BenchmarkResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(result.to_dict(), sort_keys=True) + "\n")


def load_results_jsonl(path: Path) -> list[BenchmarkResult]:
    results = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            results.append(BenchmarkResult(**json.loads(line)))
    return results
