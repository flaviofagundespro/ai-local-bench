# AI Local Bench - Product Requirements Document

Status: Draft v0.1
Date: 2026-06-06
Owner: TBD

## 1. Summary

AI Local Bench is a reproducible, cross-platform benchmark suite for local AI inference on consumer hardware. It measures real text generation and image generation workloads across operating systems, hardware vendors, and backend technologies.

The project is hardware-vendor neutral by design. The first maintainer-validated target is consumer AMD hardware, specifically AMD Radeon RX 6750 XT 12GB, because AMD local AI setup and performance vary significantly across Windows, Linux, drivers, and backend stacks.

## 2. Problem

Local AI users often cannot answer basic practical questions with reliable data:

- Which backend should I use on my GPU?
- Is Linux meaningfully faster than Windows for my workload?
- Is ROCm, Vulkan, CUDA, DirectML, Metal, or CPU the right default?
- Does a setup complete real inference reliably, or only pass synthetic checks?
- How much RAM, VRAM, time, and power does each workload consume?

Existing benchmark projects are often focused on a single frontend, a single runtime, synthetic tests, or LLM-only workloads. Image generation is frequently excluded, and AMD consumer hardware is often under-documented.

## 3. Goals

- Provide a reproducible CLI benchmark for local text and image inference.
- Support Windows and Linux from the beginning.
- Treat GPU vendor, backend, OS, driver, and model as recorded metadata.
- Produce structured outputs suitable for GitHub issues, reports, and comparison tables.
- Make benchmark methodology explicit enough that results can be trusted and repeated.
- Validate the first full result set on AMD Radeon RX 6750 XT 12GB.

## 4. Non-Goals

- No hosted ranking service in v0.1.
- No graphical UI in v0.1.
- No attempt to support every AI frontend in the first release.
- No synthetic-only benchmark as the primary result.
- No hidden auto-tuning that changes workload parameters without recording it.
- No claim that unvalidated hardware is officially supported by maintainers.

## 5. Target Users

- Local AI users comparing backends on their own workstation.
- Developers choosing between Windows and Linux for AI inference.
- AMD, NVIDIA, Intel, Apple Silicon, and CPU-only users who want repeatable local results.
- Maintainers of local AI tools who need structured benchmark evidence.
- Hardware enthusiasts publishing transparent benchmark reports.

## 6. Positioning

AI Local Bench is hardware-vendor neutral, but its first validation target is consumer AMD hardware, where local AI setup and performance vary significantly across operating systems and backends.

Support language:

- Supported by design: the project can run the benchmark if the backend is available.
- Maintainer validated: maintainers ran the benchmark and published results.
- Community reported: a user submitted results for a given configuration.
- Experimental: the backend exists, but setup, stability, or metrics are not mature enough for a strong recommendation.

## 7. MVP Scope

Version: `v0.1`

Platforms:

- Windows 11
- Linux desktop distribution, initially Ubuntu or Ubuntu-compatible

Workload families:

- Text generation
- Image generation

Initial runners:

- `llama.cpp`
- `Ollama`
- `ComfyUI`

Initial backend metadata:

- CPU
- Vulkan
- ROCm
- DirectML
- CUDA
- Metal/MPS

The runner does not need to implement all backend setup paths in v0.1. It must record the selected backend, verify the executable or service, run the workload, collect metrics where available, and write structured results.

## 8. Workloads

### 8.1 Text Generation

Initial workload types:

- short prompt latency test
- sustained generation throughput test
- long context prompt processing test

Required text metrics:

- total time
- prompt tokens per second when available
- generation tokens per second when available
- time to first token when available
- output token count
- success flag
- error type
- raw backend output log

### 8.2 Image Generation

Initial workload types:

- SD 1.5 512x512
- SDXL 1024x1024 if backend and VRAM allow
- modern 12GB-friendly model preset, to be chosen and documented
- VRAM stress profile, explicitly marked as non-comparable to standard presets

Required image metrics:

- total time per image
- images per second
- iteration speed when backend exposes it
- output path
- model name and hash when available
- seed
- sampler
- scheduler
- steps
- width
- height
- batch size
- success flag
- error type
- raw backend output log

## 9. Metrics Schema

Every benchmark result must include:

- `run_id`
- `timestamp_utc`
- `os_name`
- `os_version`
- `cpu_name`
- `gpu_name`
- `gpu_vendor`
- `gpu_driver`
- `backend`
- `frontend`
- `runner`
- `model_name`
- `model_hash`
- `workload_name`
- `prompt_name`
- `seed`
- `width`
- `height`
- `steps`
- `cfg`
- `sampler`
- `scheduler`
- `batch_size`
- `run_index`
- `warmup`
- `total_time_sec`
- `items_per_sec`
- `tokens_per_sec`
- `vram_peak_mb`
- `ram_peak_mb`
- `gpu_temp_c`
- `gpu_power_w`
- `success`
- `error_type`
- `notes`

Fields that do not apply to a workload must be present and empty, not silently omitted.

## 10. Outputs

The CLI must write:

- raw JSONL result records
- consolidated CSV
- Markdown summary report
- raw backend logs
- generated images for image workloads
- environment snapshot

Default output structure:

```text
results/
  raw/
  logs/
  images/
  reports/
  ai-local-bench-results.csv
```

## 11. Reproducibility Rules

For comparable image tests, the following must remain fixed:

- same machine
- same model
- same prompt
- same seed
- same sampler
- same scheduler
- same step count
- same resolution
- same batch size
- same VAE where applicable
- same upscaler setting, usually none
- no LoRA, ControlNet, or extra post-processing unless the workload is explicitly marked separately

For comparable text tests:

- same model file or model identifier
- same quantization
- same prompt
- same context length
- same generation limit
- same sampling parameters
- same backend
- same command configuration

Each benchmark preset must support at least one warmup run and at least five measured runs.

## 12. Architecture

The project should be a Python CLI with small runner adapters.

Proposed structure:

```text
ai-local-bench/
  PDR.md
  README.md
  pyproject.toml
  src/
    ai_local_bench/
      cli.py
      config.py
      runners/
        llamacpp.py
        ollama.py
        comfyui.py
      collectors/
        system.py
        windows.py
        linux.py
      reporting/
        csv_writer.py
        markdown.py
      schemas/
        result.py
  benchmarks/
    text/
    image/
  scripts/
    windows/
    linux/
  docs/
    stories/
    methodology.md
    result-schema.md
```

## 13. CLI Commands

Target command shape:

```bash
ai-local-bench detect
ai-local-bench run --suite text-basic --runner llamacpp
ai-local-bench run --suite image-comfyui-basic --runner comfyui
ai-local-bench summarize --input results/raw --output results/reports/summary.md
```

## 14. Quality Bar

The benchmark must not silently change test parameters.

Any automatic fallback must be recorded in:

- result notes
- raw logs
- Markdown report

Examples:

- model changed
- backend changed
- resolution reduced
- batch size reduced
- CPU fallback occurred
- safety-related setting disabled
- service restarted

## 15. GitHub Readiness

Before the first public release:

- English README
- MIT or Apache-2.0 license selected
- documented benchmark methodology
- documented result schema
- at least one dry-run test that requires no model download
- issue templates for benchmark result submissions
- example AMD RX 6750 XT report
- clear limitations section

## 16. Acceptance Criteria for v0.1

- Project installs on Windows and Linux with documented steps.
- `detect` records OS, CPU, memory, and GPU metadata.
- At least one text runner works.
- At least one image runner works.
- Results are written to JSONL and CSV.
- Markdown summary report is generated from results.
- Warmup and repeated measured runs are supported.
- Failed runs are recorded instead of discarded.
- AMD RX 6750 XT Windows and Linux validation reports exist.

## 17. Open Decisions

- License: MIT or Apache-2.0.
- Package manager: standard `venv` + `pip`, `uv`, or both.
- First model set for public examples.
- Whether ComfyUI workflows are stored as native JSON or generated from compact workload definitions.
- Whether GPU power metrics are best-effort only in v0.1 or required for validated reports.
