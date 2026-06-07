# Suite Definitions

AI Local Bench uses JSON suite definitions to describe reproducible benchmark runs.

## Design Rules

- Suites are runner-specific.
- Required fields are validated before runner execution.
- Relative paths are resolved from the suite file location.
- Invalid suites fail early with a readable error.

## Common Top-Level Fields

- `suite_name`
- `prompt_name`
- `backend`
- `seed`
- `warmup_runs`
- `measured_runs`
- `runner_config`
- `workload`

## llama.cpp Suite Requirements

`runner_config`:

- `executable`
- `model_path`

`workload`:

- `prompt`
- `max_tokens`

Optional:

- `temperature`
- `ctx_size`
- `extra_args`

## ComfyUI Suite Requirements

`runner_config`:

- `base_url`
- `workflow_path`
- `checkpoint`

`workload`:

- `prompt`
- `width`
- `height`
- `steps`
- `cfg`
- `sampler`
- `scheduler`

Optional:

- `batch_size`
- `service_process_name`

## Ollama Suite Requirements

`runner_config`:

- `base_url`
- `model`

`workload`:

- `prompt`

Optional:

- `timeout_sec`
- `service_process_name`
- `options`
