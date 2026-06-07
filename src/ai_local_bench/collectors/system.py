from __future__ import annotations

import os
import platform
import sys
from datetime import datetime, timezone

from ai_local_bench.collectors.linux import collect_linux_gpu_info
from ai_local_bench.collectors.windows import collect_windows_gpu_info


def collect_system_info() -> dict[str, object]:
    os_name = platform.system()
    gpus: list[dict[str, str]]
    if os_name == "Windows":
        gpus = collect_windows_gpu_info()
    elif os_name == "Linux":
        gpus = collect_linux_gpu_info()
    else:
        gpus = []

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "os_name": os_name,
        "os_version": platform.version(),
        "os_release": platform.release(),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "cpu_name": _detect_cpu_name(),
        "cpu_architecture": platform.machine(),
        "cpu_count_logical": os.cpu_count() or 0,
        "ram_total_mb": _detect_ram_total_mb(),
        "gpus": gpus,
    }


def _detect_cpu_name() -> str:
    processor = platform.processor().strip()
    if processor:
        return processor

    if platform.system() == "Linux":
        cpuinfo_path = "/proc/cpuinfo"
        if os.path.exists(cpuinfo_path):
            with open(cpuinfo_path, "r", encoding="utf-8") as handle:
                for line in handle:
                    if line.lower().startswith("model name"):
                        return line.split(":", 1)[1].strip()
    return platform.uname().processor or platform.uname().machine or "Unknown"


def _detect_ram_total_mb() -> int:
    if platform.system() == "Windows":
        import ctypes

        class MemoryStatusEx(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(MemoryStatusEx)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
        return int(status.ullTotalPhys // (1024 * 1024))

    meminfo_path = "/proc/meminfo"
    if os.path.exists(meminfo_path):
        with open(meminfo_path, "r", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("MemTotal:"):
                    parts = line.split()
                    return int(int(parts[1]) / 1024)
    return 0
