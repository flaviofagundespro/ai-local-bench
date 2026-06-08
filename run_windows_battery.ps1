$ErrorActionPreference = "Stop"
Set-Location "C:\Projetos\ai-local-bench"

Write-Host "=== Fresh / Cold ==="
python -m ai_local_bench.cli run --suite-file benchmarks\text\llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-latency.json --runner llamacpp
python -m ai_local_bench.cli run --suite-file benchmarks\text\llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-throughput.json --runner llamacpp
python -m ai_local_bench.cli run --suite-file benchmarks\text\llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-long-context.json --runner llamacpp

Write-Host "=== Warm / Resident ==="
python -m ai_local_bench.cli run --suite-file benchmarks\text\llamacpp-server-qwen2.5-coder-14b-windows-amd-vulkan-warm-latency.json --runner llamacpp_server
python -m ai_local_bench.cli run --suite-file benchmarks\text\llamacpp-server-qwen2.5-coder-14b-windows-amd-vulkan-warm-throughput.json --runner llamacpp_server
python -m ai_local_bench.cli run --suite-file benchmarks\text\llamacpp-server-qwen2.5-coder-14b-windows-amd-vulkan-warm-after-idle-5m.json --runner llamacpp_server

Write-Host "=== Done ==="
