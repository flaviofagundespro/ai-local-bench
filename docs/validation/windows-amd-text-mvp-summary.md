# Windows AMD Text MVP Summary

Status: Ready
Date: 2026-06-07
Hardware: AMD Ryzen 9 7900X + AMD Radeon RX 6750 XT 12GB

## What Is Already Validated

- `Ollama + qwen3.5:latest` baseline on Windows
- `llama.cpp + Vulkan` smoke validation on Windows
- `llama.cpp + Vulkan` formal harness run on Windows
- structured JSONL, CSV, Markdown, raw logs, and environment snapshot outputs
- best-effort structured `vram_peak_mb` capture for the Windows Vulkan `llama.cpp` path

## Best Current Text Path

- Runner: `llama.cpp`
- Backend: `vulkan`
- Suite: `llamacpp-qwen2.5-coder-14b-windows-amd-vulkan`
- Result: `6/6` successful in the latest formal run

## Latest Formal Artifact Set

- JSONL:
  `results/20260607T003017Z-llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-llamacpp/raw/llamacpp-qwen2.5-coder-14b-windows-amd-vulkan.jsonl`
- Markdown summary:
  `results/20260607T003017Z-llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-llamacpp/reports/llamacpp-qwen2.5-coder-14b-windows-amd-vulkan.md`
- Consolidated CSV:
  `results/ai-local-bench-results.csv`

## Practical Conclusion

For this workstation, Windows text benchmarking is already credible and operational. `llama.cpp + Vulkan` is the current reference path for local GPU-backed text inference in the project.

## Remaining Gaps

- dedicated GGUF artifact choice for long-term reproducibility
- richer GPU metrics such as temperature and power
- Windows image validation remains separate and not part of the text MVP claim
