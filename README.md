# AI Local Bench

Reproducible cross-platform benchmarks for local AI inference on consumer hardware.

AI Local Bench is hardware-vendor neutral by design. Its first maintainer-validated target is consumer AMD hardware, starting with AMD Radeon RX 6750 XT 12GB, because AMD local AI performance varies significantly across operating systems, drivers, and backends.

## Status

Active early implementation. See [PDR.md](PDR.md).

Current strongest validated slice:
- Windows text benchmarking on AMD RX 6750 XT using `llama.cpp + Vulkan`

## Planned Scope

- Windows and Linux
- Text generation benchmarks
- Image generation benchmarks
- `llama.cpp`
- `Ollama`
- `ComfyUI`
- CSV, JSONL, raw logs, and Markdown reports

## Current Implementation

- `detect` collects OS, CPU, RAM, Python, and best-effort GPU metadata.
- `run` supports JSON suite definitions for `llama.cpp`, `Ollama`, and `ComfyUI`.
- `summarize` renders a Markdown summary from JSONL result files.
- Each `run` creates an isolated run directory with raw results, logs, reports, and an environment snapshot.

Runner execution is intentionally conservative in `v0.1`:

- `llama.cpp` expects a user-provided binary and model path.
- `Ollama` expects a running local Ollama server and a user-managed model.
- `ComfyUI` expects a running server and a user-provided workflow JSON.
- Missing executables, models, workflows, or services are recorded as structured failed results.

## Support Model

- Supported by design: the tool can run the benchmark if the backend is available.
- Maintainer validated: maintainers ran the benchmark and published results.
- Community reported: users submitted results for a configuration.
- Experimental: the backend exists, but setup or metrics are not mature enough for a strong recommendation.

## Non-Goals for v0.1

- No graphical UI.
- No hosted leaderboard.
- No synthetic-only benchmark as the main result.
- No attempt to support every local AI frontend in the first release.

## Methodology

- [Methodology](docs/methodology.md)
- [Result Schema](docs/result-schema.md)
- [Suite Definitions](docs/suite-definitions.md)
- [AMD Text Backend Comparison Plan](docs/validation/amd-text-backend-comparison-plan.md)
- [AMD Text Comparison Runbook](docs/validation/amd-text-comparison-runbook.md)
- [Windows AMD llama.cpp Automation Notes](docs/validation/windows-amd-llamacpp-automation-notes.md)
- [Ubuntu AMD llama.cpp Automation Notes](docs/validation/ubuntu-amd-llamacpp-automation-notes.md)
- [AMD Text Warm Methodology](docs/validation/amd-text-warm-methodology.md)

## License

MIT. See [LICENSE](LICENSE).

## Local Development

Python 3.10+ is required.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
pytest
ai-local-bench --help
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev]
pytest
ai-local-bench --help
```

## Repository Layout

```text
src/ai_local_bench/  Python package and CLI
benchmarks/          Benchmark suite definitions
scripts/windows/     Windows helper scripts
scripts/linux/       Linux helper scripts
tests/               Dry-run and smoke tests
docs/stories/        Implementation stories
docs/validation/     Maintainer validation reports
docs/qa/             QA review reports
```

## Detection Notes

System detection is best-effort by design.

- Windows GPU metadata is collected through `Get-CimInstance Win32_VideoController`.
- Linux GPU metadata is collected through `lspci -nn`.
- Missing GPU metadata is reported as empty or unknown instead of failing the command.

## Runner Notes

`llama.cpp`:

- Models are user-provided in `v0.1`.
- The runner records missing binary or model paths as failed results.
- Token speed is parsed from backend output when available.

`ComfyUI`:

- Workflows are stored as native JSON.
- Placeholder values such as prompt, seed, steps, width, and height are substituted before submission.
- The runner polls `/history/{prompt_id}` and downloads output images through `/view`.

`Ollama`:

- Models are user-managed in `v0.1`.
- The runner calls the local HTTP API and records structured failures for missing server, missing model, timeout, or API error.
- Token throughput is derived from response fields when available.

## Limitations

- Maintainer validation now includes a formal Windows `llama.cpp + Vulkan` text run on the RX 6750 XT, plus an earlier Windows `Ollama + qwen3.5` baseline. The current MVP is strongest on Windows text workloads; the largest remaining validation gap is still image generation on AMD.
- GPU runtime metrics are best-effort; VRAM, temperature, and power may remain empty.
- The first deep validation target is AMD Radeon RX 6750 XT 12GB, but the project is hardware-vendor neutral by design.

## Recommended AMD Text Comparison Battery

For future Windows versus Linux AMD text comparisons, the repository now includes three reusable `llama.cpp` suites:

- `benchmarks/text/llamacpp-text-latency.json`
- `benchmarks/text/llamacpp-text-throughput.json`
- `benchmarks/text/llamacpp-text-long-context.json`

These are intended to support publishable comparisons across the same workstation with consistent model, quantization, and workload settings.

The repository also includes concrete templates for the primary `qwen2.5` comparison family in `3B`, `7B`, and `14B`, plus a secondary `Ollama` reference template for `gemma4:12b`.






## Warm Benchmarking

The repository now includes autonomous `llama-server` benchmark templates for resident warm benchmarking on both Windows and Ubuntu.
