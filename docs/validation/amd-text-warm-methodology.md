# AMD Text Warm Methodology

Status: Draft

## Scope

This document defines the resident warm benchmark path for AMD text inference with `llama.cpp`.

## Benchmark Classes

- `fresh-process`: a new process starts for each run
- `resident-warm`: a persistent server keeps the model loaded
- `resident-after-idle`: the model stays loaded and a request is issued after a fixed idle interval

## Validation Prompts

Warm latency prompts should be short and deterministic.

Current validated examples:

- `What is 2+2? Output only the digit.` expected `4`
- `What is the HTTP status code for Not Found? Output only the 3 digits.` expected `404`

Warm throughput prompts should be longer and realistic.

Current example:

- `Summarize Newton's three laws of motion in exactly five short bullet points.`

## Interpretation

- Fresh-process captures operational cold start behavior.
- Resident-warm captures steady-state request behavior.
- Resident-after-idle captures cache retention and wake-up behavior.
