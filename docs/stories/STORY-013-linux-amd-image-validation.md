# STORY-013 - Linux AMD Image Validation

Status: Pending manual execution

## Context

Image generation is the main workload where AMD users often experience backend and OS differences. The first image validation should focus on Linux plus ComfyUI on the RX 6750 XT.

## Scope

Run a real ComfyUI image benchmark on Linux using the maintainer AMD workstation.

## Deliverables

- documented Linux setup path
- documented ComfyUI launch command
- documented model download source and hash when possible
- SD 1.5 512x512 benchmark result
- raw JSONL
- CSV
- generated images
- Markdown summary
- validation report under `docs/validation/`

## Acceptance Criteria

- Benchmark runs at least one warmup and five measured runs.
- Workflow uses fixed prompt, seed, sampler, scheduler, steps, resolution, and batch size.
- Generated image paths are recorded.
- Failures, OOMs, or backend fallbacks are preserved.
- Report states exact backend: ROCm, Vulkan, CPU, or other.

## Test Notes

This is a manual/integration story. Automated tests should continue using mocked ComfyUI responses.

## Documentation Updates

- Add first maintainer-validated image report.
- Update README support status.

## Current State

- Linux execution was not available in the current session.
- ComfyUI benchmark infrastructure is implemented and covered by mocked tests.
- Real maintainer validation on Linux still requires a running Linux environment plus ComfyUI and a selected checkpoint.
