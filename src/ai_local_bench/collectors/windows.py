from __future__ import annotations

import json
import subprocess


def collect_windows_gpu_info() -> list[dict[str, str]]:
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        (
            "Get-CimInstance Win32_VideoController | "
            "Select-Object Name,DriverVersion,AdapterRAM | ConvertTo-Json -Compress"
        ),
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return []

    stdout = completed.stdout.strip()
    if not stdout:
        return []

    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError:
        return []

    if isinstance(parsed, dict):
        parsed = [parsed]

    gpus = []
    for item in parsed:
        gpus.append(
            {
                "name": str(item.get("Name", "")),
                "driver_version": str(item.get("DriverVersion", "")),
                "memory_mb": _adapter_ram_to_mb(item.get("AdapterRAM")),
                "vendor": _infer_vendor(str(item.get("Name", ""))),
            }
        )
    return gpus


def _adapter_ram_to_mb(raw_value: object) -> str:
    try:
        return str(int(raw_value) // (1024 * 1024))
    except (TypeError, ValueError):
        return ""


def _infer_vendor(name: str) -> str:
    lowered = name.lower()
    if "nvidia" in lowered:
        return "NVIDIA"
    if "amd" in lowered or "radeon" in lowered:
        return "AMD"
    if "intel" in lowered:
        return "Intel"
    if "apple" in lowered:
        return "Apple"
    return "Unknown"
