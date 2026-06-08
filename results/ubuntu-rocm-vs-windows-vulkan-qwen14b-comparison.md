# Windows vs Linux - Qwen2.5 Coder 14B

Date: 2026-06-08
GPU: AMD Radeon RX 6750 XT
Windows backend: Vulkan, battery executed after boot
Linux backend: ROCm 6.1.1, llama.cpp built with HIP for `gfx1030`, clean-boot battery executed after boot

This comparison uses only equivalent Qwen2.5 Coder 14B llama.cpp workloads. Ollama/Gemma reference runs are excluded because they use a different model and runner.

## Clean Comparison

| Scenario 14B | Windows Vulkan sec | Linux ROCm sec | Linux speedup by elapsed time | Windows tok/s | Linux tok/s | Linux/Windows tok/s |
|---|---:|---:|---:|---:|---:|---:|
| fresh latency | 12.46 | 1.22 | 10.22x | 90.79 | 61.62 | 0.68x |
| fresh throughput | 20.01 | 6.38 | 3.14x | 157.32 | 182.86 | 1.16x |
| fresh long-context | 15.28 | 3.38 | 4.52x | 368.29 | 408.11 | 1.11x |
| warm throughput | 4.72 | 5.39 | 0.88x | 34.27 | 29.90 | 0.87x |

## Interpretation

- Fresh/cold: Linux ROCm was much faster by elapsed time, mainly because model load and initialization were faster in these runs.
- Fresh throughput and long-context: Linux ROCm also produced higher token throughput, about 11-16% over Windows Vulkan.
- Fresh latency: Windows showed higher eval tok/s on the short generation segment, but total elapsed time was much worse due to load/init overhead.
- Warm/resident: Windows Vulkan was slightly faster when the model was already resident in `llama-server`.
- Linux warm latency and after-idle recorded performance metrics but failed content validation (`validation_error`). These runs are usable for performance timing, not for output-quality validation.

## Selected Result Directories

Windows Vulkan:

- `results/20260608T164211Z-llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-latency-llamacpp`
- `results/20260608T164402Z-llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-throughput-llamacpp`
- `results/20260608T164638Z-llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-long-context-llamacpp`
- `results/20260608T164938Z-llamacpp-server-qwen2.5-coder-14b-windows-amd-vulkan-warm-throughput-llamacpp_server`

Linux ROCm:

- `results/20260608T212721Z-llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-latency-llamacpp`
- `results/20260608T212803Z-llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-throughput-llamacpp`
- `results/20260608T212907Z-llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-long-context-llamacpp`
- `results/20260608T213012Z-llamacpp-server-qwen2.5-coder-14b-ubuntu-amd-rocm-warm-throughput-llamacpp_server`
