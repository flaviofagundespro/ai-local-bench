# Windows Scripts

This directory contains the Windows-first validation flow for the MVP.

## Scripts

- `run_windows_text_validation.ps1`
  Runs the current Windows text battery:
  - `ollama-qwen3.5-windows-amd`
  - `llamacpp-qwen2.5-coder-14b-windows-amd-vulkan`

- `run_windows_image_validation.ps1`
  Generates resolved ComfyUI suite files from the Windows image templates and runs:
  - SD 1.5 standard
  - SDXL standard
  - VRAM stress

- `run_windows_mvp_validation.ps1`
  Orchestrates a full Windows MVP validation pass:
  - system detection snapshot
  - text battery
  - optional image battery

## Typical Usage

Text-only Windows validation:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\windows\run_windows_mvp_validation.ps1
```

Text + image Windows validation:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\windows\run_windows_mvp_validation.ps1 `
  -RunImage `
  -ImageBackend vulkan `
  -Sd15Checkpoint v1-5-pruned-emaonly.safetensors `
  -SdxlCheckpoint sd_xl_base_1.0.safetensors
```

## Notes

- Image validation still depends on a running `ComfyUI` service.
- The generated image suite files are written under `benchmarks/image/generated/`.
- GPU runtime metrics remain best-effort in `v0.1`.
