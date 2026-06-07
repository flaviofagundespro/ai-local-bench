# Benchmark Methodology

AI Local Bench measures real local inference runs. It is not designed around synthetic-only scores.

## Principles

- Use the same machine for comparable runs.
- Preserve failed runs instead of discarding them.
- Record automatic fallbacks explicitly.
- Separate standard tests from stress tests.
- Treat unsupported metrics as empty, not fabricated.

## Text Workload Reproducibility

Comparable text runs should keep these fixed:

- model identifier or model file
- quantization
- prompt
- generation limit
- context length
- runner
- backend
- runner options

## Image Workload Reproducibility

Comparable image runs should keep these fixed:

- model
- workflow
- prompt
- seed
- width and height
- sampler
- scheduler
- steps
- batch size
- VAE setting when relevant

## Warmup Policy

Standard suites should use:

- at least one warmup run
- at least five measured runs

Warmup rows remain in outputs so users can audit behavior instead of trusting hidden filtering.

## Standard vs Stress Tests

Standard tests are meant for comparisons across backends or systems.

Stress tests are meant to find limits such as OOM points, instability, or backend failure thresholds. They must not be presented as directly comparable to standard benchmark presets.

## Fallback Policy

If a benchmark changes behavior at runtime, that change must be recorded in:

- raw logs
- result notes
- Markdown report when relevant

Examples:

- CPU fallback
- resolution reduction
- service restart
- backend change
- model change

## Failed Runs

Failed runs remain part of the benchmark record because stability is part of the result.

## Metrics Limits

- RAM metrics are best-effort.
- GPU metrics may be unavailable depending on platform, driver, and backend.
- Empty fields indicate unavailable metrics, not zero usage.
