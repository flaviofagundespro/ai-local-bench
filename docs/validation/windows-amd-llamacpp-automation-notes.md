# Windows AMD llama.cpp Automation Notes

Status: Maintainer note
Date: 2026-06-08

## Discovery

On the maintainer Windows workstation, the bundled `llama.cpp` build `b9542-6b80c74f2` did not behave as a one-shot benchmark binary when invoked through `llama-cli.exe`.

The same build also enabled conversation mode automatically in `llama-completion.exe` unless conversation mode was explicitly disabled.

## Practical Impact

A benchmark run could appear to hang even after producing a valid answer because the process remained open in interactive mode.

This caused inflated total time and blocked the Python harness at `subprocess.communicate()`.

## Working Windows Command Pattern

The following pattern returned cleanly and printed usable timing data:

```powershell
& "tools\llama.cpp\llama-completion.exe" `
  -m "C:\Users\flavi\.ollama\models\blobs\sha256-ac9bc7a69dab38da1c790838955f1293420b55ab555ef6b4615efa1c1507b1ed" `
  -p "Reply with exactly one word: OK" `
  -n 8 `
  --temp 0 `
  -c 4096 `
  -no-cnv `
  --no-warmup
```

## Repository Updates

- Windows `llama.cpp` benchmark templates now use `llama-completion.exe`.
- Windows `llama.cpp` benchmark templates now add `-no-cnv` and `--no-warmup`.
- The runner now rejects `llama-cli` explicitly for this benchmark path.

## Follow-Up

A future improvement may replace `communicate()` with direct file-backed log streaming for additional robustness on Windows.
