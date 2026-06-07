# MVP Checklist

Status date: 2026-06-07
Scope of this checklist: current `v0.1` state of `ai-local-bench`

## Ready Now

- [x] Python CLI exists with `detect`, `run`, and `summarize`
- [x] Structured outputs exist: JSONL, CSV, Markdown, raw logs, environment snapshot
- [x] Failed runs are recorded instead of discarded
- [x] Warmup plus repeated measured runs are supported
- [x] `llama.cpp` runner exists and works
- [x] `Ollama` runner exists and works
- [x] `ComfyUI` runner exists at code level
- [x] Suite validation exists
- [x] Windows hardware detection exists
- [x] Windows AMD text baseline via `Ollama` exists
- [x] Windows AMD text validation via `llama.cpp + Vulkan` exists
- [x] Windows AMD text benchmark artifacts are published in `results/`
- [x] `tokens_per_sec` is parsed for current `llama.cpp` output
- [x] `vram_peak_mb` is now recorded for the Windows `llama.cpp + Vulkan` path
- [x] Automated tests are passing
- [x] Windows text MVP can be defended technically as a completed slice

## Built But Not Fully Validated

- [x] Windows image benchmark battery templates exist
- [x] Windows orchestration scripts for text and image runs exist
- [x] Windows image validation document exists
- [ ] Windows image benchmark runs have been maintainer-validated end to end
- [ ] `ComfyUI` on Windows AMD is running successfully in the validated benchmark path

## Not Ready Yet

- [ ] Linux AMD image validation is complete
- [ ] Windows image generation on AMD is validated in the benchmark harness
- [ ] `gpu_temp_c` is captured in structured outputs
- [ ] `gpu_power_w` is captured in structured outputs
- [ ] A dedicated public GGUF artifact is selected for long-term reproducibility
- [ ] Full cross-platform MVP claim is justified for both text and image workloads

## Honest MVP Conclusion

- [x] The project is ready as a **Windows text benchmarking MVP on AMD hardware**
- [ ] The project is ready as a **full original MVP for text + image across Windows and Linux**

## Immediate Next Decision

Choose one explicitly:

- Focus the release narrative on the Windows text MVP and mark image validation as pending
- Continue implementation until Windows/Linux image validation is also complete
