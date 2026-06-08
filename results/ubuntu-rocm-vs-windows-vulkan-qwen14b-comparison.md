# Ubuntu ROCm vs Windows Vulkan - Qwen2.5 Coder 14B

Comparacao limpa usando apenas os diretórios finais validos/equivalentes no CSV `results/ai-local-bench-results.csv`.

| cenario 14B | Windows Vulkan sec | Ubuntu ROCm sec | Ubuntu mais rapido | Windows tok/s | Ubuntu tok/s | tok/s Ubuntu/Windows | validade |
|---|---:|---:|---:|---:|---:|---:|---|
| fresh latency | 12.46 | 1.34 | 9.27x | 90.79 | 61.48 | 0.68x | W 5/5; U 5/5 |
| fresh throughput | 20.01 | 7.38 | 2.71x | 157.32 | 177.08 | 1.13x | W 5/5; U 5/5 |
| fresh long-context | 15.28 | 4.38 | 3.49x | 368.29 | 404.90 | 1.10x | W 5/5; U 5/5 |
| warm latency | 0.13 | 0.14 | 0.99x | 45.35 | 40.40 | 0.89x | W 5/5; U 0/5 validation_error |
| warm throughput | 4.72 | 5.40 | 0.87x | 34.27 | 29.83 | 0.87x | W 5/5; U 5/5 |
| warm after-idle 5m | 0.13 | 0.13 | 0.95x | 45.47 | 40.35 | 0.89x | W 1/1; U 0/1 validation_error |

## Interpretação curta

- Fresh/cold: Ubuntu ROCm venceu claramente no tempo total, principalmente porque carrega/inicializa bem mais rapido nesses runs.
- Throughput/long-context fresh: Ubuntu ROCm tambem venceu em tokens/s, cerca de 10-13% acima do Windows Vulkan.
- Latency fresh: Windows mostrou mais tokens/s no trecho de eval, mas o tempo total foi muito pior por overhead de carregamento/inicializacao.
- Warm/resident: Windows Vulkan ficou ligeiramente melhor em tokens/s e tempo no servidor residente.
- Os cenarios warm latency e warm after-idle do Ubuntu mediram performance, mas falharam validacao de conteudo (`validation_error`). Para comparacao de velocidade, os numeros existem; para comparacao de acuracia/saida, esses prompts precisam ajuste.

## Diretórios usados

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
