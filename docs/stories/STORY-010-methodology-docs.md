# STORY-010 - Benchmark Methodology Documentation

Status: Completed
Completed on: 2026-06-06

## Context

The project should be public and reproducible. Users need to understand what is comparable, what is best-effort, and what invalidates a result.

## Scope

Write the benchmark methodology documentation.

## Deliverables

- `docs/methodology.md`
- text workload reproducibility rules
- image workload reproducibility rules
- warmup and measured-run policy
- backend fallback policy
- result interpretation guidance

## Acceptance Criteria

- The methodology explains why failed runs are preserved.
- The methodology explains when results are comparable.
- The methodology explicitly separates standard tests from stress tests.
- The methodology states that automatic parameter changes must be recorded.
- README links to the methodology.

## Test Notes

Documentation-only story. No runtime tests required.

## Documentation Updates

- Add README link.
- Cross-link from PDR if helpful.

## Implementation Notes

- Added `docs/methodology.md`.
- Linked methodology, result schema, and suite definitions from the README.
- Documented standard-vs-stress distinction, failed-run preservation, and fallback recording rules.
