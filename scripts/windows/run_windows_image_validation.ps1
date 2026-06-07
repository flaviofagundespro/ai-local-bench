param(
    [Parameter(Mandatory = $true)]
    [string]$Backend,
    [Parameter(Mandatory = $true)]
    [string]$Sd15Checkpoint,
    [Parameter(Mandatory = $true)]
    [string]$SdxlCheckpoint,
    [string]$ComfyUiBaseUrl = "http://127.0.0.1:8188",
    [string]$OutputDir = "results",
    [bool]$RunStressSuite = $true
)

$ErrorActionPreference = "Stop"

function New-ResolvedSuiteFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$TemplatePath,
        [Parameter(Mandatory = $true)]
        [string]$Checkpoint,
        [Parameter(Mandatory = $true)]
        [string]$ResolvedName
    )

    $suite = Get-Content $TemplatePath | ConvertFrom-Json
    $suite.backend = $Backend
    $suite.runner_config.base_url = $ComfyUiBaseUrl
    $suite.runner_config.checkpoint = $Checkpoint

    $generatedDir = Join-Path "benchmarks\image\generated" ""
    New-Item -ItemType Directory -Force -Path $generatedDir | Out-Null
    $resolvedPath = Join-Path $generatedDir $ResolvedName
    $suite | ConvertTo-Json -Depth 10 | Set-Content -Path $resolvedPath -Encoding utf8
    return $resolvedPath
}

function Invoke-SuiteFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SuiteFile
    )

    Write-Host "Running suite file '$SuiteFile'..."
    python -m ai_local_bench.cli run --suite ignored --runner comfyui --suite-file $SuiteFile --output-dir $OutputDir
    if ($LASTEXITCODE -ne 0) {
        throw "Suite failed: $SuiteFile"
    }
}

$sd15Suite = New-ResolvedSuiteFile `
    -TemplatePath "benchmarks\image\image-comfyui-sd15-windows-amd-template.json" `
    -Checkpoint $Sd15Checkpoint `
    -ResolvedName "image-comfyui-sd15-windows-amd-$Backend.json"

$sdxlSuite = New-ResolvedSuiteFile `
    -TemplatePath "benchmarks\image\image-comfyui-sdxl-windows-amd-template.json" `
    -Checkpoint $SdxlCheckpoint `
    -ResolvedName "image-comfyui-sdxl-windows-amd-$Backend.json"

Invoke-SuiteFile -SuiteFile $sd15Suite
Invoke-SuiteFile -SuiteFile $sdxlSuite

if ($RunStressSuite) {
    $stressSuite = New-ResolvedSuiteFile `
        -TemplatePath "benchmarks\image\image-comfyui-vram-stress-windows-amd-template.json" `
        -Checkpoint $SdxlCheckpoint `
        -ResolvedName "image-comfyui-vram-stress-windows-amd-$Backend.json"
    Invoke-SuiteFile -SuiteFile $stressSuite
}
