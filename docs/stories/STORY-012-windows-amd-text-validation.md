# STORY-012 - Windows AMD Text Validation

Status: Complete

## Context

The first maintainer validation target is AMD Radeon RX 6750 XT on Windows. Text generation should be validated before image generation because setup is usually lighter.

## Scope

Run a real `llama.cpp` text benchmark on Windows using the maintainer AMD workstation.

## Deliverables

- documented `llama.cpp` setup path
- documented model choice and checksum/hash
- real benchmark command
- raw JSONL
- CSV
- Markdown summary
- validation report under `docs/validation/`

## Acceptance Criteria

- Benchmark runs at least one warmup and five measured runs.
- Result records include OS, CPU, GPU, backend, runner, model, and hash.
- Any missing metric fields are explained.
- Report states whether backend is CPU, Vulkan, or another path.
- Results are not generalized beyond tested hardware.

## Test Notes

This is a manual/integration story. Automated tests are not expected to execute the real model.

## Documentation Updates

- Add first maintainer-validated text report.
- Update README support status.

## Current State

- `ollama.exe` is installed on the current Windows machine.
- A live `ollama` benchmark invocation produced structured connection-failure results because the local service was not accepting connections on `127.0.0.1:11434`.
- The Windows hardware snapshot was captured successfully through `ai-local-bench detect --format json`.
- A real `Ollama + qwen3.5:latest` benchmark was later executed successfully with `1` warmup and `5` measured runs.
- `llama.cpp` Vulkan binaries were later installed under `tools/llama.cpp`.
- A real `llama.cpp` smoke run with `qwen2.5-coder:14b` completed successfully on `Vulkan0` and returned the expected output `OK`.
- Best-effort Windows telemetry during that run showed peak dedicated GPU memory around `9.68 GB` and peak summed GPU-engine utilization around `52.86%`.
- A formal harness suite, `llamacpp-qwen2.5-coder-14b-windows-amd-vulkan`, also completed with `1` warmup and `5` measured runs, all successful.
- This story is complete for the Windows text-validation objective. Remaining follow-up work is about richer GPU metrics, not basic path validation.
