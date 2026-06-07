from __future__ import annotations

from unittest.mock import patch

from ai_local_bench.collectors.linux import collect_linux_gpu_info
from ai_local_bench.collectors.system import collect_system_info
from ai_local_bench.collectors.windows import collect_windows_gpu_info


def test_collect_windows_gpu_info_parses_json() -> None:
    stdout = '[{"Name":"AMD Radeon RX 6750 XT","DriverVersion":"32.0.12000","AdapterRAM":12884901888}]'
    with patch("subprocess.run") as mocked_run:
        mocked_run.return_value.stdout = stdout
        mocked_run.return_value.returncode = 0
        gpus = collect_windows_gpu_info()

    assert gpus[0]["vendor"] == "AMD"
    assert gpus[0]["memory_mb"] == "12288"


def test_collect_linux_gpu_info_parses_lspci() -> None:
    stdout = "03:00.0 VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Navi 22 [Radeon RX 6750 XT]"
    with patch("subprocess.run") as mocked_run:
        mocked_run.return_value.stdout = stdout
        mocked_run.return_value.returncode = 0
        gpus = collect_linux_gpu_info()

    assert gpus[0]["vendor"] == "AMD"


def test_collect_system_info_returns_expected_keys() -> None:
    with patch("ai_local_bench.collectors.system.collect_windows_gpu_info", return_value=[]), patch(
        "ai_local_bench.collectors.system.collect_linux_gpu_info", return_value=[]
    ):
        data = collect_system_info()

    assert "os_name" in data
    assert "cpu_name" in data
    assert "ram_total_mb" in data
    assert "gpus" in data
