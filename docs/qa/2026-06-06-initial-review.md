# QA Review - 2026-06-06

Status: Initial pass

## Findings

1. Real hardware validation has not been executed yet.
   The code and mocks are in place, but maintainer-validated benchmark artifacts do not exist yet.

2. GPU runtime metrics are best-effort and currently conservative.
   RAM peak sampling exists, but VRAM, GPU temperature, and GPU power are still empty unless future collectors are added.

3. Service-backed runners depend on external process naming assumptions.
   Best-effort RAM sampling for Ollama and ComfyUI uses process-name matching and may miss renamed or containerized processes.

## Residual Risk

- Public users may interpret "supported by design" as "maintainer validated" unless README language stays strict.
- Cross-platform path handling should be watched closely once real Linux validation begins.

## Test Status

- Automated tests passing at review time.
- Manual benchmark validation pending.
