# STORY-008 - Ollama Runner

Status: Completed
Completed on: 2026-06-06

## Context

Ollama is one of the most common local LLM entrypoints. Supporting it makes the project useful for users who do not want to manage `llama.cpp` binaries directly.

## Scope

Implement a runner that calls an existing Ollama server through its local HTTP API.

## Deliverables

- Ollama API client
- suite definition for Ollama text workload
- warmup and measured repetitions
- timing capture
- token throughput parsing from Ollama response fields when available
- structured failure for missing server, missing model, timeout, and API error

## Acceptance Criteria

- Runner can execute against `http://127.0.0.1:11434`.
- Missing Ollama server produces a structured failed result.
- Successful mocked responses produce JSONL, CSV, and Markdown outputs.
- Model name and backend metadata are recorded.
- Tests mock HTTP responses and do not require Ollama installed.

## Test Notes

Use Python standard library HTTP mocking or monkeypatch `urllib.request.urlopen`.

## Documentation Updates

- Add Ollama setup notes for Windows and Linux.
- Document that model pulls are user-managed in v0.1.

## Implementation Notes

- Implemented the Ollama runner in `src/ai_local_bench/runners/ollama.py`.
- Added structured handling for missing server, timeout, and API-side failures.
- Added an example suite definition in `benchmarks/text/ollama-basic.json`.
- Verified successful mocked execution in automated tests.
- Verified structured connection-failure output in the current Windows environment when the local Ollama service is not accepting connections.
