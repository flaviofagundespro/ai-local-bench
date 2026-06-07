from __future__ import annotations

import csv
from pathlib import Path

from ai_local_bench.schemas import RESULT_FIELD_NAMES, BenchmarkResult


def write_results_csv(path: Path, results: list[BenchmarkResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELD_NAMES)
        writer.writeheader()
        for result in results:
            writer.writerow(result.to_dict())
