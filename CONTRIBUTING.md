# Contributing

AI Local Bench is designed around reproducibility and honest reporting.

## Principles

- Do not overclaim hardware, backend, or OS support.
- Keep benchmark parameter changes explicit and recorded.
- Preserve failed runs instead of discarding them.
- Prefer small stories and focused pull requests.

## Local Setup

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
pytest
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev]
pytest
```

## Result Submissions

Benchmark result submissions should include:

- raw JSONL
- consolidated CSV
- environment snapshot
- generated report Markdown
- notes about missing metrics, fallbacks, crashes, or service instability

## Scope Notes

- Hardware-vendor neutral by design
- First maintainer-validated target: AMD Radeon RX 6750 XT 12GB
- No hosted leaderboard in `v0.1`
