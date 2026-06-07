# STORY-003 - Result Schema and Writers

Status: Completed
Completed on: 2026-06-06

## Context

Before runners exist, the project needs a stable result schema and writers for JSONL, CSV, and Markdown summaries.

## Scope

Implement typed result records and output writers.

## Deliverables

- result schema model
- JSONL writer
- CSV writer
- Markdown summary writer
- sample synthetic result fixture

## Acceptance Criteria

- A synthetic result can be written to JSONL and CSV.
- CSV includes all required columns from the PDR.
- Empty fields are preserved instead of omitted.
- Markdown summary can be generated from sample results.

## Test Notes

No backend runner should be required.

## Documentation Updates

- Add `docs/result-schema.md`.

## Implementation Notes

- Added `BenchmarkResult` and a stable field list in `src/ai_local_bench/schemas/result.py`.
- Implemented JSONL, CSV, and Markdown summary writers.
- Added a synthetic sample fixture under `tests/fixtures/sample_results.json`.
- Verified that empty fields remain present in structured outputs.
