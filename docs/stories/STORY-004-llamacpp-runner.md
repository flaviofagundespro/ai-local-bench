# STORY-004 - llama.cpp Runner

Status: Completed
Completed on: 2026-06-06

## Context

`llama.cpp` is a practical first text runner because it supports multiple backends and can run on Windows and Linux.

## Scope

Implement a runner that executes an existing `llama.cpp` binary against a user-provided model.

## Deliverables

- runner configuration
- command construction
- raw log capture
- timing capture
- token speed parsing where available
- failure recording

## Acceptance Criteria

- Runner can execute a configured `llama.cpp` command.
- Missing binary or model produces a structured failed result.
- Backend metadata is recorded from user configuration.
- At least one text workload can run warmup plus measured repetitions.

## Test Notes

Use command mocking for automated tests. Real model execution should be manual or integration-only.

## Documentation Updates

- Add setup notes for Windows and Linux.
- Document that models are user-provided in v0.1.

## Implementation Notes

- Implemented `llama.cpp` command construction and execution in `src/ai_local_bench/runners/llamacpp.py`.
- Added SHA-256 hashing for user-provided model files.
- Added structured failed results for missing binary, missing model, timeout, and non-zero exit status.
- Added token-rate parsing from backend output when available.
- Verified warmup plus measured repetition handling through tests.
