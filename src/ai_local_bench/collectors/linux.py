from __future__ import annotations

import subprocess


def collect_linux_gpu_info() -> list[dict[str, str]]:
    try:
        completed = subprocess.run(
            ["lspci", "-nn"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return []

    gpus = []
    for line in completed.stdout.splitlines():
        lowered = line.lower()
        if "vga compatible controller" not in lowered and "3d controller" not in lowered:
            continue
        gpus.append(
            {
                "name": line.strip(),
                "driver_version": "",
                "memory_mb": "",
                "vendor": _infer_vendor(line),
            }
        )
    return gpus


def _infer_vendor(name: str) -> str:
    lowered = name.lower()
    if "nvidia" in lowered:
        return "NVIDIA"
    if "amd" in lowered or "advanced micro devices" in lowered or "radeon" in lowered:
        return "AMD"
    if "intel" in lowered:
        return "Intel"
    if "apple" in lowered:
        return "Apple"
    return "Unknown"
