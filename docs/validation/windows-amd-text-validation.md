# Windows AMD Text Validation

Status: Validation complete for the Windows text MVP path
Target hardware: AMD Ryzen 9 7900X + AMD Radeon RX 6750 XT 12GB

## Goal

Validate a real text benchmark run on the maintainer Windows workstation.

## Executed Runners

- `Ollama`
- `llama.cpp`

## Executed Benchmark

- Date: 2026-06-06
- Model: `qwen3.5:latest`
- Suite: `ollama-qwen3.5-windows-amd`
- Warmup runs: `1`
- Measured runs: `5`
- Result: `6/6` successful

## Vulkan Smoke Validation

- Date: 2026-06-06
- Model: `qwen2.5-coder:14b`
- Backend: `Vulkan0`
- Binary: `tools/llama.cpp/llama-completion.exe`
- Prompt: `Reply with exactly: OK`
- Output: `OK`
- Exit code: `0`

## Formal Vulkan Harness Run

- Date: 2026-06-06
- Suite: `llamacpp-qwen2.5-coder-14b-windows-amd-vulkan`
- Warmup runs: `1`
- Measured runs: `5`
- Result: `6/6` successful
- Backend recorded by harness: `vulkan`
- Model hash: `ac9bc7a69dab38da1c790838955f1293420b55ab555ef6b4615efa1c1507b1ed`

## Artifact Paths

- Raw JSONL:
  `results/20260606T140350Z-ollama-qwen3.5-windows-amd-ollama/raw/ollama-qwen3.5-windows-amd.jsonl`
- Markdown summary:
  `results/20260606T140350Z-ollama-qwen3.5-windows-amd-ollama/reports/ollama-qwen3.5-windows-amd.md`
- Environment snapshot:
  `results/20260606T140350Z-ollama-qwen3.5-windows-amd-ollama/environment.json`
- Consolidated CSV:
  `results/ai-local-bench-results.csv`
- Vulkan smoke summary:
  `results/vulkan-smoke-qwen2.5-coder-14b-final/summary.json`
- Vulkan smoke stdout:
  `results/vulkan-smoke-qwen2.5-coder-14b-final/stdout.log`
- Vulkan smoke telemetry:
  `results/vulkan-smoke-qwen2.5-coder-14b-final/telemetry.csv`
- Formal Vulkan JSONL:
  `results/20260606T151943Z-llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-llamacpp/raw/llamacpp-qwen2.5-coder-14b-windows-amd-vulkan.jsonl`
- Formal Vulkan summary:
  `results/20260606T151943Z-llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-llamacpp/reports/llamacpp-qwen2.5-coder-14b-windows-amd-vulkan.md`
- Updated formal Vulkan JSONL with structured VRAM:
  `results/20260607T003017Z-llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-llamacpp/raw/llamacpp-qwen2.5-coder-14b-windows-amd-vulkan.jsonl`
- Updated formal Vulkan summary:
  `results/20260607T003017Z-llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-llamacpp/reports/llamacpp-qwen2.5-coder-14b-windows-amd-vulkan.md`

## Observed Results

- Total time per run was highly stable at roughly `14.74s` to `14.89s`.
- Measured token throughput was roughly `6.78` to `6.85 tok/s`.
- Best-effort RAM peak was roughly `8.0 GB`.
- No failures occurred during the full benchmark run.

## Backend Interpretation

- GPU metadata was detected correctly for the host machine.
- The benchmark record currently uses backend `unknown` because the suite was not specialized to a confirmed execution path.
- Observed system behavior during the run suggested CPU-dominant execution:
  CPU usage was reported around `50-55%` and Windows Task Manager showed roughly `2-3%` GPU usage.
- This run should be treated as a valid Windows baseline for `Ollama + qwen3.5`, but not as proof of meaningful GPU acceleration on the RX 6750 XT.

## Vulkan Smoke Findings

- `llama.cpp` Vulkan detected the RX 6750 XT successfully as `Vulkan0`.
- A real run completed successfully with `qwen2.5-coder:14b` and returned the expected output `OK`.
- Best-effort Windows counter sampling captured a peak summed GPU-engine utilization of `52.86%`.
- Best-effort Windows counter sampling captured a peak dedicated GPU memory usage of `9678.93 MB`.
- This is strong evidence that the Windows Vulkan path is real and reaches meaningful GPU/VRAM usage on this machine.

## Formal Vulkan Harness Findings

- The formal harness run completed with `1` warmup and `5` measured runs, all successful.
- Measured total time stayed in a tight band of roughly `14.68s` to `15.06s`.
- Measured generation throughput stayed around `33.9` to `34.3 tok/s`.
- Best-effort RAM peak recorded by the harness was `9173 MB` on all runs.
- After the Windows telemetry integration, a repeat harness run also recorded `vram_peak_mb` directly in the standard JSONL/CSV output.
- In that updated run, `vram_peak_mb` stabilized at `10779 MB` across the recorded runs.
- `gpu_temp_c` and `gpu_power_w` still remain empty in structured results.

## Remaining Work

- Decide whether to keep the local Ollama blob path or move to a dedicated user-managed GGUF model for long-term reproducibility.
- Optionally add a dedicated text-comparison report that contrasts `Ollama` and `llama.cpp + Vulkan` for the same workstation.

## Blocking Requirements

None for this Windows text validation path.

## Execution Notes

`llama.cpp + Vulkan` was exercised successfully on the RX 6750 XT both as a smoke test and as a formal harness run. The Windows text path is now the strongest completed slice of the `v0.1` MVP.
