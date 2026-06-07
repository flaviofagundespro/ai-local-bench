# STORY-009 - Runtime Metrics Sampling

Status: Completed
Completed on: 2026-06-06

## Context

The result schema includes RAM, VRAM, GPU temperature, and GPU power fields, but runners currently do not sample those metrics during execution.

## Scope

Add best-effort runtime metrics sampling around runner execution.

## Deliverables

- cross-platform process RAM sampling
- Windows GPU metrics collector where available
- Linux GPU metrics collector where available
- peak metric aggregation per run
- clear empty-field behavior when a metric is unavailable

## Acceptance Criteria

- RAM peak is recorded for runner child processes where possible.
- GPU metrics failures do not fail benchmark execution.
- Unsupported metrics remain empty and are mentioned in notes or environment metadata.
- Tests cover metric aggregation with mocked samples.

## Test Notes

Keep dependencies minimal. If `psutil` is introduced, add it explicitly to `pyproject.toml` and document why.

## Documentation Updates

- Update `docs/result-schema.md` with best-effort metric semantics.
- Add platform-specific metric limitations.

## Implementation Notes

- Added best-effort RAM peak sampling in `src/ai_local_bench/runtime_metrics.py`.
- `llama.cpp` samples child-process RAM during execution.
- Ollama and ComfyUI can sample named service processes when configured.
- VRAM, GPU temperature, and GPU power remain intentionally empty until dedicated collectors are added.
