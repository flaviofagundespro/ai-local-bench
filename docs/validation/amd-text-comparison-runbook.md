# AMD Text Comparison Runbook

Status: Draft execution runbook

## Goal

Provide a practical execution checklist for the AMD text comparison battery on the maintainer workstation.

## Pre-Run Checklist

- Close GPU-heavy desktop applications.
- Confirm the target model files are present.
- Confirm the intended `llama.cpp` executable is present.
- Confirm the same GGUF artifact is available for both Windows and Ubuntu runs.
- Record the exact quantization and file hash.
- Avoid changing drivers, clocks, or power settings between comparable runs.

## Primary Comparison Order

Recommended primary order:

1. `qwen2.5-3b`
2. `qwen2.5-7b`
3. `qwen2.5-coder-14b`

For each model, run:

1. latency
2. throughput
3. long-context

This is the primary GPU-vs-GPU comparison battery.
CPU-only runs are optional and should be treated as a separate curiosity set, not part of the main comparison.

For the first pass, execute the full Windows Vulkan side before the Ubuntu ROCm side.

## Template Preparation

Before each run, replace `CHANGE_ME` values in the selected suite file:

- `runner_config.executable`
- `runner_config.model_path`

On Windows, the executable is expected to look like `llama-completion.exe`.
On Ubuntu, the executable is expected to look like `llama-cli`.

## Example Commands

Windows example:

```powershell
ai-local-bench run --suite-file benchmarks/text/llamacpp-qwen2.5-7b-windows-amd-vulkan-throughput.json --runner llamacpp
```

Ubuntu example:

```bash
ai-local-bench run --suite-file benchmarks/text/llamacpp-qwen2.5-7b-ubuntu-amd-rocm-throughput.json --runner llamacpp
```

Secondary reference example:

```powershell
ai-local-bench run --suite-file benchmarks/text/ollama-gemma4-12b-windows-amd-reference-throughput.json --runner ollama
```

## Recommended Artifact Review

After each run, review:

- raw JSONL
- Markdown summary
- environment snapshot
- appended CSV row set

Check especially for:

- unexpected backend label
- failed runs
- missing model path issues
- fallback notes
- suspiciously low throughput or resource usage

## Publishable Reporting Guidance

When publishing a comparison report:

- separate the primary `qwen2.5` family from the secondary `gemma4:12b` reference
- describe `Windows + Vulkan` versus `Ubuntu + ROCm` as a stack comparison
- avoid backend-general claims beyond the tested workstation and setup
- include artifact paths and model hashes


## Resident Warm Benchmark Order

Recommended warm-server order:

1. warm latency
2. warm throughput
3. warm after idle

Use the `llamacpp_server` runner so the benchmark is autonomous and starts its own local `llama-server` process.


## Execution Note

Warm benchmark suites require a valid `runner_config.model_path`. The Windows `qwen2.5-coder-14b` warm suites are now prefilled for the maintainer workstation path, while Ubuntu templates still require local path updates.
