# STORY-002 - System Detection

Status: Completed
Completed on: 2026-06-06

## Context

Every benchmark result must include environment metadata. The first functional slice should detect the operating system, CPU, memory, Python runtime, and best-effort GPU information.

## Scope

Implement `ai-local-bench detect`.

## Deliverables

- cross-platform system collector
- Windows GPU collector
- Linux GPU collector
- JSON output mode
- human-readable output mode
- test fixtures for collector parsing where practical

## Acceptance Criteria

- `ai-local-bench detect` runs without model downloads.
- Output includes OS name/version, CPU, RAM, Python version, and detected GPU fields when available.
- Missing GPU data is recorded as empty or unknown, not treated as a crash.
- Command exits non-zero only for real execution failures.

## Test Notes

Tests should mock platform-specific command output where possible.

## Documentation Updates

- Document which metrics are best-effort on Windows and Linux.

## Implementation Notes

- Implemented cross-platform system collection in `src/ai_local_bench/collectors/`.
- Added human-readable and JSON output modes to `ai-local-bench detect`.
- Windows GPU metadata uses `Get-CimInstance Win32_VideoController`.
- Linux GPU metadata uses `lspci -nn`.
- Missing GPU data is treated as best-effort and does not fail command execution.
