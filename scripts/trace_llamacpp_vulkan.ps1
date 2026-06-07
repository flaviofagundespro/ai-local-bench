param(
    [Parameter(Mandatory = $true)]
    [string]$Executable,
    [Parameter(Mandatory = $true)]
    [string]$ModelPath,
    [Parameter(Mandatory = $true)]
    [string]$OutputDir,
    [string]$Prompt = "Reply with exactly: OK",
    [string]$Device = "Vulkan0",
    [int]$MaxTokens = 8,
    [int]$TimeoutSec = 300,
    [string[]]$ExtraArgs = @("--simple-io", "--no-warmup", "-ngl", "all", "--single-turn")
)

$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$stdoutPath = Join-Path $OutputDir "stdout.log"
$stderrPath = Join-Path $OutputDir "stderr.log"
$telemetryPath = Join-Path $OutputDir "telemetry.csv"
$summaryPath = Join-Path $OutputDir "summary.json"

$adapterSamples = (Get-Counter '\GPU Adapter Memory(*)\Dedicated Usage').CounterSamples
$activeAdapter = $adapterSamples | Sort-Object CookedValue -Descending | Select-Object -First 1
if (-not $activeAdapter) {
    throw "No GPU adapter counters were available."
}

$adapterInstance = $activeAdapter.InstanceName
$gpuCounterPath = '\GPU Engine(*)\Utilization Percentage'
$memoryCounterPath = "\GPU Adapter Memory($adapterInstance)\Dedicated Usage"

function Quote-Argument([string]$Value) {
    if ($Value -match '[\s"]') {
        '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
    } else {
        $Value
    }
}

$commandArgs = @(
    "-m", $ModelPath,
    "-p", $Prompt,
    "-n", "$MaxTokens",
    "--device", $Device
) + $ExtraArgs

$startedAt = Get-Date
$startInfo = New-Object System.Diagnostics.ProcessStartInfo
$startInfo.FileName = $Executable
$startInfo.WorkingDirectory = Split-Path -Parent $Executable
$startInfo.RedirectStandardOutput = $true
$startInfo.RedirectStandardError = $true
$startInfo.UseShellExecute = $false
$startInfo.CreateNoWindow = $true
$startInfo.Arguments = (($commandArgs | ForEach-Object { Quote-Argument $_ }) -join " ")

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $startInfo
if (-not $process.Start()) {
    throw "Failed to start llama.cpp process."
}

$rows = [System.Collections.Generic.List[object]]::new()
$peakGpu = 0.0
$peakDedicatedBytes = 0.0
$peakProcessPrivateMb = 0.0

while (-not $process.HasExited) {
    $engineSamples = (Get-Counter $gpuCounterPath).CounterSamples |
        Where-Object { $_.InstanceName -like "*${adapterInstance}*" }
    $gpuSum = ($engineSamples | Measure-Object -Property CookedValue -Sum).Sum
    if ($null -eq $gpuSum) {
        $gpuSum = 0.0
    }

    $dedicatedSample = (Get-Counter $memoryCounterPath).CounterSamples | Select-Object -First 1
    $dedicatedBytes = if ($dedicatedSample) { [double]$dedicatedSample.CookedValue } else { 0.0 }

    try {
        $privateMb = [math]::Round($process.PrivateMemorySize64 / 1MB, 2)
    } catch {
        $privateMb = 0.0
    }

    if ($gpuSum -gt $peakGpu) {
        $peakGpu = $gpuSum
    }
    if ($dedicatedBytes -gt $peakDedicatedBytes) {
        $peakDedicatedBytes = $dedicatedBytes
    }
    if ($privateMb -gt $peakProcessPrivateMb) {
        $peakProcessPrivateMb = $privateMb
    }

    $rows.Add([pscustomobject]@{
        timestamp_utc = (Get-Date).ToUniversalTime().ToString("o")
        pid = $process.Id
        gpu_util_percent_sum = [math]::Round($gpuSum, 2)
        dedicated_usage_mb = [math]::Round($dedicatedBytes / 1MB, 2)
        process_private_mb = $privateMb
    }) | Out-Null

    $waited = $process.WaitForExit(200)
    if (-not $waited) {
        $elapsed = (Get-Date) - $startedAt
        if ($elapsed.TotalSeconds -ge $TimeoutSec) {
            $process.Kill()
            throw "llama.cpp timed out after ${TimeoutSec}s"
        }
    }
}

$process.WaitForExit()
$process.StandardOutput.ReadToEnd() | Set-Content -Path $stdoutPath -Encoding utf8
$process.StandardError.ReadToEnd() | Set-Content -Path $stderrPath -Encoding utf8
$rows | Export-Csv -NoTypeInformation -Encoding utf8 -Path $telemetryPath

$summary = [pscustomobject]@{
    executable = $Executable
    model_path = $ModelPath
    started_at = $startedAt.ToUniversalTime().ToString("o")
    finished_at = (Get-Date).ToUniversalTime().ToString("o")
    exit_code = $process.ExitCode
    adapter_instance = $adapterInstance
    peak_gpu_util_percent_sum = [math]::Round($peakGpu, 2)
    peak_dedicated_usage_mb = [math]::Round($peakDedicatedBytes / 1MB, 2)
    peak_process_private_mb = [math]::Round($peakProcessPrivateMb, 2)
    args = $commandArgs
}

$summary | ConvertTo-Json -Depth 4 | Set-Content -Path $summaryPath -Encoding utf8

Write-Output "summary_path=$summaryPath"
Write-Output "telemetry_path=$telemetryPath"
Write-Output "stdout_path=$stdoutPath"
Write-Output "stderr_path=$stderrPath"
Write-Output "exit_code=$($process.ExitCode)"
