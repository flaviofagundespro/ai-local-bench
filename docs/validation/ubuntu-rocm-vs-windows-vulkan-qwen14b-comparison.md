# Ubuntu ROCm vs Windows Vulkan - Qwen2.5 Coder 14B

Date: 2026-06-08
GPU: AMD Radeon RX 6750 XT
Ubuntu backend: ROCm 6.1.1, llama.cpp built with HIP for `gfx1030`
Windows backend: Vulkan, existing Windows battery results

This comparison intentionally uses only equivalent Qwen2.5 Coder 14B llama.cpp workloads. Ollama/Gemma reference runs are excluded because they use a different model and runner.

## Clean Comparison

| Scenario 14B | Windows Vulkan sec | Ubuntu ROCm sec | Ubuntu speedup by elapsed time | Windows tok/s | Ubuntu tok/s | Ubuntu/Windows tok/s |
|---|---:|---:|---:|---:|---:|---:|
| fresh latency | 12.46 | 1.34 | 9.27x | 90.79 | 61.48 | 0.68x |
| fresh throughput | 20.01 | 7.38 | 2.71x | 157.32 | 177.08 | 1.13x |
| fresh long-context | 15.28 | 4.38 | 3.49x | 368.29 | 404.90 | 1.10x |
| warm latency | 0.13 | 0.14 | 0.99x | 45.35 | 40.40 | 0.89x |
| warm throughput | 4.72 | 5.40 | 0.87x | 34.27 | 29.83 | 0.87x |
| warm after-idle 5m | 0.13 | 0.13 | 0.95x | 45.47 | 40.35 | 0.89x |

## Proof Run After Closing Apps

A short Ubuntu-only proof run repeated the most relevant 14B scenarios after reducing desktop background load.

| Scenario | Previous Ubuntu sec | Proof sec | Delta sec | Previous tok/s | Proof tok/s | Delta tok/s |
|---|---:|---:|---:|---:|---:|---:|
| 14B fresh throughput | 7.38 | 9.74 | +31.9% | 177.08 | 176.46 | -0.4% |
| 14B fresh long-context | 4.38 | 5.80 | +32.5% | 404.90 | 405.05 | +0.0% |
| 14B warm throughput | 5.40 | 5.40 | +0.0% | 29.83 | 29.82 | -0.1% |

Interpretation: background desktop applications did not materially change generation throughput. Fresh elapsed time varied due to load/init/cache/IO overhead, but token generation throughput stayed stable.

## Interpretation

- Fresh/cold: Ubuntu ROCm was much faster by elapsed time, mainly because model load and initialization were much faster in these runs.
- Fresh throughput and long-context: Ubuntu ROCm also produced higher token throughput, about 10-13% over Windows Vulkan.
- Fresh latency: Windows showed higher eval tok/s on the very short generation segment, but total elapsed time was much worse due to load/init overhead.
- Warm/resident: Windows Vulkan was slightly faster when the model was already resident in `llama-server`.
- Ubuntu warm latency and after-idle recorded performance metrics but failed content validation (`validation_error`). These runs are usable for performance timing, not for output-quality validation.

## Selected Result Directories

Windows Vulkan:

- `results/20260608T164211Z-llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-latency-llamacpp`
- `results/20260608T164402Z-llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-throughput-llamacpp`
- `results/20260608T164638Z-llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-long-context-llamacpp`
- `results/20260608T164849Z-llamacpp-server-qwen2.5-coder-14b-windows-amd-vulkan-warm-latency-llamacpp_server`
- `results/20260608T164938Z-llamacpp-server-qwen2.5-coder-14b-windows-amd-vulkan-warm-throughput-llamacpp_server`
- `results/20260608T165056Z-llamacpp-server-qwen2.5-coder-14b-windows-amd-vulkan-warm-after-idle-5m-llamacpp_server`

Ubuntu ROCm:

- `results/20260608T204802Z-llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-latency-llamacpp`
- `results/20260608T204848Z-llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-throughput-llamacpp`
- `results/20260608T204955Z-llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-long-context-llamacpp`
- `results/20260608T205045Z-llamacpp-server-qwen2.5-coder-14b-ubuntu-amd-rocm-warm-latency-llamacpp_server`
- `results/20260608T205111Z-llamacpp-server-qwen2.5-coder-14b-ubuntu-amd-rocm-warm-throughput-llamacpp_server`
- `results/20260608T205207Z-llamacpp-server-qwen2.5-coder-14b-ubuntu-amd-rocm-warm-after-idle-5m-llamacpp_server`

Proof run:

- `results/20260608T210810Z-llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-throughput-llamacpp`
- `results/20260608T210932Z-llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-long-context-llamacpp`
- `results/20260608T211028Z-llamacpp-server-qwen2.5-coder-14b-ubuntu-amd-rocm-warm-throughput-llamacpp_server`
