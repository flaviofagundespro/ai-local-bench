# Ubuntu AMD llama.cpp Automation Notes

Status: Draft maintainer note
Date: 2026-06-08

## Goal

Document the Ubuntu Linux side of the AMD `llama.cpp` automation path for both fresh-process and resident warm benchmarking.

## Expected Linux Pattern

For resident warm benchmarking on Ubuntu, use `llama-server` with the same GGUF artifact used on Windows whenever possible.

## Warm Benchmark Notes

- Keep the model resident in GPU memory during the benchmark process.
- Use short deterministic prompts for warm latency checks.
- Use a longer structured prompt for warm throughput checks.
- Measure post-idle behavior separately from immediate follow-up requests.

## Command Shape

Typical Linux server startup shape:

```bash
./llama-server -m /path/to/model.gguf -c 4096 -ngl 99 --host 127.0.0.1 --port 8080 --no-warmup
```

## Follow-Up

The Ubuntu path should publish the same benchmark classes as Windows:

- fresh-process
- resident-warm
- resident-after-idle
