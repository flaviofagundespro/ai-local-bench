# STORY-006 - Suite Definition Validation

Status: Completed
Completed on: 2026-06-06

## Context

Benchmark suites are currently plain JSON files loaded directly by the CLI. Before real public usage, invalid suites should fail early with clear messages instead of failing inside runner code.

## Scope

Add validation for text and image suite definitions.

## Deliverables

- suite schema validation module
- validation for required top-level fields
- validation for runner-specific config fields
- clear CLI error messages for invalid suites
- tests for valid and invalid suite files

## Acceptance Criteria

- `ai-local-bench run` validates the suite before invoking a runner.
- Missing required fields produce a readable error.
- Unknown runner/suite combinations are rejected before execution.
- Existing sample suites pass validation.
- Tests do not require external binaries, models, GPUs, or services.

## Test Notes

Use synthetic JSON fixtures. Avoid adding a heavyweight schema dependency unless it clearly improves maintainability.

## Documentation Updates

- Add `docs/suite-definitions.md`.
- Document required fields for `llama.cpp` and ComfyUI suites.

## Implementation Notes

- Added suite validation in `src/ai_local_bench/suite_validation.py`.
- Added required-field validation for `llama.cpp`, `ComfyUI`, and `Ollama` suites.
- Added relative-path normalization for suite-local workflow and model paths.
- Added tests for valid and invalid suite definitions.
