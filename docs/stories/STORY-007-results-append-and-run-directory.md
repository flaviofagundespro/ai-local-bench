# STORY-007 - Results Directory and Append Behavior

Status: Completed
Completed on: 2026-06-06

## Context

The current CLI writes predictable output paths under `results/`. For real benchmark runs, each invocation needs an isolated run directory while still supporting an appendable consolidated CSV.

## Scope

Create deterministic run output organization.

## Deliverables

- per-run directory naming using timestamp, suite, and runner
- environment snapshot written with every run
- raw JSONL written under the run directory
- logs and images grouped under the run directory
- optional consolidated CSV append behavior

## Acceptance Criteria

- Running the same suite twice does not overwrite raw run artifacts.
- The CLI prints the run directory path.
- Environment metadata is written as JSON.
- Consolidated CSV can append measured results across runs.
- Warmup rows remain distinguishable in all outputs.

## Test Notes

Use temporary directories and missing-path runner results.

## Documentation Updates

- Update README output structure.
- Document artifact retention expectations.

## Implementation Notes

- Added per-run output directories named by timestamp, suite, and runner.
- Added environment snapshot writing for each run.
- Raw JSONL, logs, reports, and images now live under the run directory.
- Consolidated CSV now appends instead of overwriting.
