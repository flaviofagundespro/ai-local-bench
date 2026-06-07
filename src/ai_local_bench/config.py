from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    project_root: Path
    benchmarks_dir: Path
    scripts_dir: Path
    tests_dir: Path
    docs_dir: Path


def get_project_paths(project_root: Path | None = None) -> ProjectPaths:
    root = project_root or Path(__file__).resolve().parents[2]
    return ProjectPaths(
        project_root=root,
        benchmarks_dir=root / "benchmarks",
        scripts_dir=root / "scripts",
        tests_dir=root / "tests",
        docs_dir=root / "docs",
    )
