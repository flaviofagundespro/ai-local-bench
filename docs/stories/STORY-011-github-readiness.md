# STORY-011 - GitHub Readiness

Status: Completed
Completed on: 2026-06-06

## Context

Before making the repository public, it needs standard project hygiene and clear contribution boundaries.

## Scope

Prepare the repository for public GitHub publishing.

## Deliverables

- license decision and license file
- `.gitignore`
- `CONTRIBUTING.md`
- issue templates
- benchmark result submission template
- GitHub Actions CI for tests
- README limitations section

## Acceptance Criteria

- CI runs tests on at least Windows and Linux.
- README states current support status honestly.
- Result submissions request raw JSONL, CSV, environment snapshot, and notes.
- License is explicit.
- No generated benchmark results or local artifacts are tracked by default.

## Test Notes

Run tests locally after adding CI config. GitHub Actions execution happens after publishing.

## Documentation Updates

- Update README and contribution docs.

## Implementation Notes

- Added MIT `LICENSE`.
- Added `.gitignore`.
- Added `CONTRIBUTING.md`.
- Added GitHub issue templates and a CI workflow for Windows and Linux.
- Updated README support and limitations language for public use.
