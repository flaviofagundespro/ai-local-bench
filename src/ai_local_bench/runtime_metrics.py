from __future__ import annotations

import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Callable

import psutil


MemoryReader = Callable[[], int | None]


@dataclass
class PeakMetrics:
    ram_peak_mb: str = ""
    vram_peak_mb: str = ""
    gpu_temp_c: str = ""
    gpu_power_w: str = ""


class MemorySampler:
    def __init__(
        self,
        reader: MemoryReader,
        interval_sec: float = 0.1,
        vram_reader: MemoryReader | None = None,
    ) -> None:
        self._reader = reader
        self._vram_reader = vram_reader
        self._interval_sec = interval_sec
        self._peak_bytes = 0
        self._peak_vram_bytes = 0
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> PeakMetrics:
        self._stop_event.set()
        self._thread.join(timeout=1)
        peak_mb = int(self._peak_bytes / (1024 * 1024)) if self._peak_bytes else 0
        peak_vram_mb = int(self._peak_vram_bytes / (1024 * 1024)) if self._peak_vram_bytes else 0
        return PeakMetrics(
            ram_peak_mb=str(peak_mb) if peak_mb else "",
            vram_peak_mb=str(peak_vram_mb) if peak_vram_mb else "",
        )

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                sample = self._reader()
            except (psutil.Error, OSError, PermissionError):
                sample = None
            if sample and sample > self._peak_bytes:
                self._peak_bytes = sample
            if self._vram_reader:
                try:
                    vram_sample = self._vram_reader()
                except (psutil.Error, OSError, PermissionError, subprocess.SubprocessError):
                    vram_sample = None
                if vram_sample and vram_sample > self._peak_vram_bytes:
                    self._peak_vram_bytes = vram_sample
            time.sleep(self._interval_sec)


def make_process_memory_reader(pid: int) -> MemoryReader:
    try:
        process = psutil.Process(pid)
    except (psutil.Error, OSError):
        return lambda: None

    def reader() -> int | None:
        if not process.is_running():
            return None
        return int(process.memory_info().rss)

    return reader


def make_process_name_memory_reader(process_name: str) -> MemoryReader:
    lowered = process_name.lower()

    def reader() -> int | None:
        total = 0
        for process in psutil.process_iter(["name"]):
            name = (process.info.get("name") or "").lower()
            if lowered in name:
                try:
                    total += int(process.memory_info().rss)
                except (psutil.Error, OSError, PermissionError):
                    continue
        return total or None

    return reader


def make_windows_gpu_dedicated_memory_reader() -> MemoryReader:
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        (
            "(Get-Counter '\\GPU Adapter Memory(*)\\Dedicated Usage').CounterSamples | "
            "Select-Object -ExpandProperty CookedValue | "
            "Measure-Object -Maximum | "
            "Select-Object -ExpandProperty Maximum"
        ),
    ]

    def reader() -> int | None:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        stdout = (completed.stdout or "").strip()
        if not stdout:
            return None
        normalized = stdout.replace(",", ".")
        return int(float(normalized))

    return reader
