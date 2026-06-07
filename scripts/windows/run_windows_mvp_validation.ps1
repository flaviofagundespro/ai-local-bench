param(
    [string]$OutputDir = "results",
    [bool]$RunText = $true,
    [bool]$RunImage = $false,
    [string]$ImageBackend = "vulkan",
    [string]$Sd15Checkpoint = "",
    [string]$SdxlCheckpoint = "",
    [string]$ComfyUiBaseUrl = "http://127.0.0.1:8188"
)

$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$detectPath = Join-Path $OutputDir "windows-system-detect.json"
python -m ai_local_bench.cli detect --format json | Set-Content -Path $detectPath -Encoding utf8
if ($LASTEXITCODE -ne 0) {
    throw "System detection failed."
}

if ($RunText) {
    & "$PSScriptRoot\run_windows_text_validation.ps1" -OutputDir $OutputDir
}

if ($RunImage) {
    if ([string]::IsNullOrWhiteSpace($Sd15Checkpoint) -or [string]::IsNullOrWhiteSpace($SdxlCheckpoint)) {
        throw "Sd15Checkpoint and SdxlCheckpoint are required when -RunImage is enabled."
    }
    & "$PSScriptRoot\run_windows_image_validation.ps1" `
        -Backend $ImageBackend `
        -Sd15Checkpoint $Sd15Checkpoint `
        -SdxlCheckpoint $SdxlCheckpoint `
        -ComfyUiBaseUrl $ComfyUiBaseUrl `
        -OutputDir $OutputDir
}

Write-Host "Windows MVP validation flow completed."
