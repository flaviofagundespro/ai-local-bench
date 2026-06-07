# Result Schema

AI Local Bench writes structured benchmark results in JSONL, CSV, and Markdown.

## Core Principles

- All benchmark records use the same top-level field set.
- Fields that do not apply to a given workload remain present and empty.
- Failed runs are recorded instead of discarded.
- Automatic fallback behavior must be written into `notes` and raw logs.

## Fields

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
- `output_path`
- `raw_log_path`

## Output Formats

### JSONL

Used as the raw structured record format. Each line is a single result object.

### CSV

Used for spreadsheets, GitHub attachments, and lightweight comparison workflows.

### Markdown

Used for human-readable summaries and benchmark reports.
