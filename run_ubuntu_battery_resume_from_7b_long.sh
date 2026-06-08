#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

export ROCM_PATH=/opt/rocm-6.1.1
export HIP_PATH=/opt/rocm-6.1.1
export PATH=/opt/rocm-6.1.1/bin:/opt/rocm-6.1.1/llvm/bin:$PATH
export LD_LIBRARY_PATH="$PWD/.build-rocm-hipcc/bin:/opt/rocm-6.1.1/lib:/opt/rocm-6.1.1/lib64:${LD_LIBRARY_PATH:-}"
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"

echo "=== Resume: Fresh / Cold from 7B long-context ==="
python3 -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-qwen2.5-7b-ubuntu-amd-rocm-long-context.json --runner llamacpp
python3 -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-latency.json --runner llamacpp
python3 -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-throughput.json --runner llamacpp
python3 -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-long-context.json --runner llamacpp

echo "=== Resume: Warm / Resident ==="
python3 -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-server-qwen2.5-coder-14b-ubuntu-amd-rocm-warm-latency.json --runner llamacpp_server
python3 -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-server-qwen2.5-coder-14b-ubuntu-amd-rocm-warm-throughput.json --runner llamacpp_server
python3 -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-server-qwen2.5-coder-14b-ubuntu-amd-rocm-warm-after-idle-5m.json --runner llamacpp_server

echo "=== Resume Done ==="
