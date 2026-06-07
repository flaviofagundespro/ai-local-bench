# STORY-005 - ComfyUI Runner

Status: Completed
Completed on: 2026-06-06

## Context

ComfyUI is the first image runner because it exposes reproducible workflow JSON and has broad local image generation adoption.

## Scope

Implement a runner that submits a workflow to an existing ComfyUI server and records timing, output images, and raw API responses.

## Deliverables

- ComfyUI API client
- workflow loader
- prompt/seed/workload substitution
- queue submission
- polling for completion
- generated image collection
- raw log/API response capture

## Acceptance Criteria

- Runner can submit a workflow to a configured ComfyUI endpoint.
- Failed connection produces a structured failed result.
- Output image paths are recorded.
- Warmup plus measured repetitions are supported.
- Workflow parameters are not silently changed.

## Test Notes

Use mocked HTTP responses for automated tests. Real ComfyUI execution should be integration-only.

## Documentation Updates

- Add ComfyUI setup notes.
- Add workflow reproducibility rules.

## Implementation Notes

- Implemented ComfyUI prompt submission, history polling, workflow substitution, and image download logic in `src/ai_local_bench/runners/comfyui.py`.
- Added native workflow JSON examples under `benchmarks/image/`.
- Added structured failed results for missing workflow, connection errors, and polling timeouts.
- Verified warmup plus measured repetition handling and mocked end-to-end success paths through tests.
