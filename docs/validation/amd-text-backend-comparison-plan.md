# AMD Text Backend Comparison Plan

Status: Draft comparison plan
Target hardware: AMD Radeon RX 6750 XT 12GB class workstation

## Goal

Establish a documented, repeatable comparison plan for AMD text benchmarking across backend and operating system combinations.

## Scope

This plan is intended for real `llama.cpp` text runs where the same model artifact and workload definitions can be reused across multiple execution paths.

Initial comparison target:

- Windows + `llama.cpp + Vulkan`
- Ubuntu Linux + `llama.cpp` path that represents the intended Linux AMD backend under test

If the Linux path uses ROCm while the Windows path uses Vulkan, the result must be interpreted as a full-stack comparison, not a backend-only claim.

## Primary Comparison Set

The primary comparison family is `qwen2.5` across three model sizes:

- `qwen2.5-3b`
- `qwen2.5-7b`
- `qwen2.5-coder-14b`

This structure supports a cleaner scaling analysis on the same model family.

## Secondary Reference Set

The repository also includes a secondary reference template for:

- `gemma4:12b` through `Ollama`

This reference path is useful as an additional operational data point, but it should not be mixed into the primary family scaling claim.

## Interpretation Rules

- Same hardware is required.
- Same model file is required.
- Same quantization is required.
- Same suite JSON is required except for explicit backend and executable path changes.
- Same warmup and measured run counts are required.
- Same prompt, context, and max token settings are required.

Results should be reported as:

- `Windows + Vulkan` versus `Ubuntu + ROCm` on the same workstation

Results should not be overstated as:

- `ROCm is faster than Vulkan` in general

because operating system, driver stack, and backend path all change at once.

## Recommended Text Battery

Three standard text suites should be used:

- `llamacpp-text-latency`
- `llamacpp-text-throughput`
- `llamacpp-text-long-context`

These suites cover:

- short deterministic response latency
- sustained generation throughput
- larger prompt processing and mixed generation behavior

## Concrete Comparison Suites

Primary `qwen2.5` templates:

- `benchmarks/text/llamacpp-qwen2.5-3b-windows-amd-vulkan-latency.json`
- `benchmarks/text/llamacpp-qwen2.5-3b-windows-amd-vulkan-throughput.json`
- `benchmarks/text/llamacpp-qwen2.5-3b-windows-amd-vulkan-long-context.json`
- `benchmarks/text/llamacpp-qwen2.5-3b-ubuntu-amd-rocm-latency.json`
- `benchmarks/text/llamacpp-qwen2.5-3b-ubuntu-amd-rocm-throughput.json`
- `benchmarks/text/llamacpp-qwen2.5-3b-ubuntu-amd-rocm-long-context.json`
- `benchmarks/text/llamacpp-qwen2.5-7b-windows-amd-vulkan-latency.json`
- `benchmarks/text/llamacpp-qwen2.5-7b-windows-amd-vulkan-throughput.json`
- `benchmarks/text/llamacpp-qwen2.5-7b-windows-amd-vulkan-long-context.json`
- `benchmarks/text/llamacpp-qwen2.5-7b-ubuntu-amd-rocm-latency.json`
- `benchmarks/text/llamacpp-qwen2.5-7b-ubuntu-amd-rocm-throughput.json`
- `benchmarks/text/llamacpp-qwen2.5-7b-ubuntu-amd-rocm-long-context.json`
- `benchmarks/text/llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-latency.json`
- `benchmarks/text/llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-throughput.json`
- `benchmarks/text/llamacpp-qwen2.5-coder-14b-windows-amd-vulkan-long-context.json`
- `benchmarks/text/llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-latency.json`
- `benchmarks/text/llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-throughput.json`
- `benchmarks/text/llamacpp-qwen2.5-coder-14b-ubuntu-amd-rocm-long-context.json`

Secondary reference template:

- `benchmarks/text/ollama-gemma4-12b-windows-amd-reference-throughput.json`

These are templates only. Replace `CHANGE_ME` paths before execution and keep the same GGUF artifact on both operating systems for the primary comparison set.

## Run Policy

For each environment:

- run `1` warmup pass
- run `5` measured passes at minimum
- prefer `10` measured passes for a publishable comparison if runtime is acceptable

If any run fails, keep the failed result in the output set and describe the failure in the validation report.

## Quality Interpretation

The current comparison battery is primarily a performance and stability battery.

It is designed to compare:

- total runtime
- token throughput
- VRAM and RAM behavior when available
- failure rate and fallback behavior

It is not yet a formal quality benchmark. Small output differences across backends may occur because of implementation and numeric-path differences, but the expected comparison focus is still speed, resource usage, and stability.

## Required Recording

Each comparison report should include:

- operating system and version
- driver information when available
- `llama.cpp` binary provenance or build description
- model filename and hash
- suite filenames
- backend label recorded by the suite
- summary of total time and token throughput
- VRAM and RAM notes if available
- explicit notes for any fallback or instability

## Publishable Conclusion Standard

A comparison is strong enough for a maintainer report when:

- all three text suites complete successfully on both paths
- the same model artifact is used on both paths
- artifact paths and hashes are recorded
- no hidden runtime fallback invalidates the comparison
- limitations are stated clearly in English
