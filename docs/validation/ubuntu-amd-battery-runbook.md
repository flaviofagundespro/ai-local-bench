# Ubuntu AMD Battery Runbook

Status: Draft maintainer runbook
Date: 2026-06-08

## Goal

Provide a complete execution handoff for the Ubuntu Linux benchmark pass on the same AMD workstation used for the Windows validation.

## Scope

This runbook covers:

- fresh-process text benchmarking with `llama.cpp`
- resident warm text benchmarking with `llama-server`
- the `qwen2.5-coder-14b` comparison path for Ubuntu AMD

This is the GPU-primary battery.
CPU-only text benchmarking is optional and should be treated as a separate exploratory path.

## Benchmark Classes

The Ubuntu pass should preserve the same benchmark classes used on Windows:

- `fresh-process`
- `resident-warm`
- `resident-after-idle`

## Preconditions

Before running the Ubuntu battery:

- confirm the target GGUF model file exists locally
- confirm the same model artifact and quantization used on Windows are available on Ubuntu
- confirm the `llama.cpp` Linux binaries are present
- confirm the intended Linux GPU backend path is working
- confirm port `8080` is free before warm-server tests
- close GPU-heavy desktop applications
- avoid running a manual `llama-server` in parallel with the autonomous benchmark runner

## Files That Must Be Updated

Before execution, update the Ubuntu suite files to use the local Linux paths.

Fresh-process suites:

- `benchmarks/text/llamacpp-qwen2.5-3b-ubuntu-amd-rocm-latency.json`
- `benchmarks/text/llamacpp-qwen2.5-3b-ubuntu-amd-rocm-throughput.json`
- `benchmarks/text/llamacpp-qwen2.5-3b-ubuntu-amd-rocm-long-context.json`
- `benchmarks/text/llamacpp-qwen2.5-7b-ubuntu-amd-rocm-latency.json`
- `benchmarks/text/llamacpp-qwen2.5-7b-ubuntu-amd-rocm-throughput.json`
- `benchmarks/text/llamacpp-qwen2.5-7b-ubuntu-amd-rocm-long-context.json`
- `benchmarks/text/llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-latency.json`
- `benchmarks/text/llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-throughput.json`
- `benchmarks/text/llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-long-context.json`

Resident warm suites:

- `benchmarks/text/llamacpp-server-qwen2.5-coder-14b-ubuntu-amd-rocm-warm-latency.json`
- `benchmarks/text/llamacpp-server-qwen2.5-coder-14b-ubuntu-amd-rocm-warm-throughput.json`
- `benchmarks/text/llamacpp-server-qwen2.5-coder-14b-ubuntu-amd-rocm-warm-after-idle-5m.json`

Required fields to update:

- `runner_config.executable`
- `runner_config.model_path`

Check whether `runner_config.ngl` and any Linux-specific `server_args` need adjustment for the actual build.

## Smoke Test 1: Fresh Process

Run a one-shot `llama-cli` smoke test before the benchmark battery.

Recommended shape:

```bash
/path/to/llama-cli \
  -m /path/to/model.gguf \
  -p "Reply with exactly one word: OK" \
  -n 8 \
  --temp 0 \
  -c 4096 \
  -no-cnv \
  --no-warmup
```

Expected result:

- the process exits on its own
- the output contains `OK`
- the command does not remain in interactive mode

## Smoke Test 2: Resident Warm Server

Start a local server manually one time before trusting the autonomous warm runner.

Recommended shape:

```bash
/path/to/llama-server \
  -m /path/to/model.gguf \
  -c 4096 \
  -ngl 99 \
  --host 127.0.0.1 \
  --port 8080 \
  --no-warmup
```

Then issue a deterministic test request:

```bash
curl -s http://127.0.0.1:8080/completion \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"What is 2+2? Output only the digit.","n_predict":4,"temperature":0,"top_p":1,"top_k":1,"seed":123}'
```

Expected result:

- the response content is `4` after trimming whitespace
- the server remains resident
- a second identical request should show better cache reuse

## Prompt Policy

Use the same prompt classes validated on Windows.

Short deterministic prompts:

- `What is 2+2? Output only the digit.` expected `4`
- `What is the HTTP status code for Not Found? Output only the 3 digits.` expected `404`

Longer throughput prompt:

- `Summarize Newton's three laws of motion in exactly five short bullet points.`

## Execution Order

Run the Ubuntu battery in this order.

### Fresh / Cold

```bash
python -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-qwen2.5-3b-ubuntu-amd-rocm-latency.json --runner llamacpp
python -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-qwen2.5-3b-ubuntu-amd-rocm-throughput.json --runner llamacpp
python -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-qwen2.5-3b-ubuntu-amd-rocm-long-context.json --runner llamacpp
python -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-qwen2.5-7b-ubuntu-amd-rocm-latency.json --runner llamacpp
python -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-qwen2.5-7b-ubuntu-amd-rocm-throughput.json --runner llamacpp
python -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-qwen2.5-7b-ubuntu-amd-rocm-long-context.json --runner llamacpp
python -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-latency.json --runner llamacpp
python -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-throughput.json --runner llamacpp
python -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-long-context.json --runner llamacpp
```

### Warm / Resident

```bash
python -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-server-qwen2.5-coder-14b-ubuntu-amd-rocm-warm-latency.json --runner llamacpp_server
python -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-server-qwen2.5-coder-14b-ubuntu-amd-rocm-warm-throughput.json --runner llamacpp_server
python -m ai_local_bench.cli run --suite-file benchmarks/text/llamacpp-server-qwen2.5-coder-14b-ubuntu-amd-rocm-warm-after-idle-5m.json --runner llamacpp_server
```

## Scripted Execution

A helper script already exists:

- `run_ubuntu_battery.sh`

Recommended usage:

```bash
chmod +x run_ubuntu_battery.sh
./run_ubuntu_battery.sh | tee ubuntu-battery.log
```

## Interpretation Guidance

Fresh-process results should be interpreted as operational cold or fresh execution.

Resident warm results should be interpreted as:

- model-resident latency
- cache reuse behavior
- steady-state request performance

Resident-after-idle results should be interpreted separately from immediate warm follow-up requests.

## Artifacts To Review

After each run, review:

- JSONL raw results
- Markdown summary
- environment snapshot
- raw logs
- consolidated CSV rows

Check especially for:

- backend label correctness
- missing model path mistakes
- validation failures on deterministic prompts
- unexpectedly low cache reuse
- connection or startup failures on the warm server path

## Publishable Notes

When publishing the Ubuntu report:

- state the exact Linux distribution and version
- state the GPU driver and backend stack used
- state the exact `llama.cpp` build or source revision
- state the model artifact path, filename, and hash
- compare Ubuntu against Windows as a full-stack result
- avoid claiming generic ROCm superiority beyond the tested workstation and software stack
