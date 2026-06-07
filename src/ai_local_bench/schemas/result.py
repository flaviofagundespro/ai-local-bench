from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from uuid import uuid4


RESULT_FIELD_NAMES = [
    "run_id",
    "timestamp_utc",
    "os_name",
    "os_version",
    "cpu_name",
    "gpu_name",
    "gpu_vendor",
    "gpu_driver",
    "backend",
    "frontend",
    "runner",
    "model_name",
    "model_hash",
    "workload_name",
    "prompt_name",
    "seed",
    "width",
    "height",
    "steps",
    "cfg",
    "sampler",
    "scheduler",
    "batch_size",
    "run_index",
    "warmup",
    "total_time_sec",
    "items_per_sec",
    "tokens_per_sec",
    "vram_peak_mb",
    "ram_peak_mb",
    "gpu_temp_c",
    "gpu_power_w",
    "success",
    "error_type",
    "notes",
    "output_path",
    "raw_log_path",
]


@dataclass
class BenchmarkResult:
    run_id: str
    timestamp_utc: str
    os_name: str = ""
    os_version: str = ""
    cpu_name: str = ""
    gpu_name: str = ""
    gpu_vendor: str = ""
    gpu_driver: str = ""
    backend: str = ""
    frontend: str = ""
    runner: str = ""
    model_name: str = ""
    model_hash: str = ""
    workload_name: str = ""
    prompt_name: str = ""
    seed: str = ""
    width: str = ""
    height: str = ""
    steps: str = ""
    cfg: str = ""
    sampler: str = ""
    scheduler: str = ""
    batch_size: str = ""
    run_index: str = ""
    warmup: str = ""
    total_time_sec: str = ""
    items_per_sec: str = ""
    tokens_per_sec: str = ""
    vram_peak_mb: str = ""
    ram_peak_mb: str = ""
    gpu_temp_c: str = ""
    gpu_power_w: str = ""
    success: str = ""
    error_type: str = ""
    notes: str = ""
    output_path: str = ""
    raw_log_path: str = ""

    @classmethod
    def create(cls, **kwargs: str) -> "BenchmarkResult":
        base = {
            "run_id": uuid4().hex,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        base.update(kwargs)
        return cls(**base)

    def to_dict(self) -> dict[str, str]:
        data = asdict(self)
        return {field: str(data.get(field, "")) if data.get(field, "") is not None else "" for field in RESULT_FIELD_NAMES}

