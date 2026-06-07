# Windows AMD Image Validation

Status: Test battery prepared; manual execution still pending
Target hardware: AMD Ryzen 9 7900X + AMD Radeon RX 6750 XT 12GB

## Goal

Validate the Windows image-generation path on the maintainer workstation before Linux image validation.

## Planned Battery

- `image-comfyui-sd15-windows-amd`
  - 512x512
  - 30 steps
  - batch 1
  - portrait realism prompt
- `image-comfyui-sdxl-windows-amd`
  - 1024x1024
  - 30 steps
  - batch 1
  - Sao Paulo night scene prompt
- `image-comfyui-vram-stress-windows-amd`
  - 1024x1024
  - 30 steps
  - batch 2
  - product-photo prompt

## Required Runtime Inputs

- running `ComfyUI` server
- selected backend, for example `vulkan` or `directml`
- SD 1.5 checkpoint name
- SDXL checkpoint name

## Execution Path

- Use [scripts/windows/run_windows_image_validation.ps1](/C:/Projetos/ai-local-bench/scripts/windows/run_windows_image_validation.ps1).
- The script materializes resolved suite files from the templates under `benchmarks/image/generated/`.
- Standard output artifacts go to `results/` through the main CLI.

## Expected Artifacts

- raw JSONL
- consolidated CSV
- Markdown summaries
- generated images
- environment snapshot
- raw ComfyUI prompt/history logs

## Current State

- The ComfyUI runner and workflow templating already exist.
- The Windows image validation battery is now defined and scriptable.
- A real maintainer-validated Windows image run is still pending.
