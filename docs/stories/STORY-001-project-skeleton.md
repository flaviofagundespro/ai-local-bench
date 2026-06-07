# STORY-001 - Project Skeleton

Status: Completed
Completed on: 2026-06-06

## Context

The project needs a clean, public-ready structure before benchmark code is implemented. The skeleton should support a Python CLI, benchmark definitions, scripts for Windows/Linux, documentation, and tests.

## Scope

Create the initial repository structure and minimal package metadata.

## Deliverables

- `pyproject.toml`
- `src/ai_local_bench/`
- `tests/`
- `benchmarks/`
- `scripts/windows/`
- `scripts/linux/`
- initial CLI entrypoint with `detect`, `run`, and `summarize` placeholders
- basic smoke test for CLI import/help

## Acceptance Criteria

- Project can be installed in editable mode.
- CLI help command runs on Windows and Linux.
- Tests run without requiring GPU, model downloads, or external AI services.
- README still states that benchmark execution is not implemented until the runner stories land.

## Test Notes

Use a dry-run test only. No model or backend should be required for this story.

## Documentation Updates

- Update `README.md` with local development setup.
- Add a short architecture note if package layout differs from the PDR.

## Implementation Notes

- Implemented a minimal Python package with `argparse` CLI placeholders for `detect`, `run`, and `summarize`.
- Added `pyproject.toml` with editable install support and a console script entrypoint.
- Added dry-run smoke tests that do not require models, GPUs, or external services.
- Verified with editable install, `pytest`, and `python -m ai_local_bench.cli --help`.
