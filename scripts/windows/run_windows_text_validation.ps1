param(
    [string]$OutputDir = "results",
    [bool]$RunOllamaBaseline = $true,
    [bool]$RunLlamaCppVulkan = $true,
    [string]$LlamaSuite = "llamacpp-qwen2.5-coder-14b-windows-amd-vulkan",
    [string]$OllamaSuite = "ollama-qwen3.5-windows-amd"
)

$ErrorActionPreference = "Stop"

function Invoke-BenchmarkSuite {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SuiteName,
        [Parameter(Mandatory = $true)]
        [string]$RunnerName
    )

    Write-Host "Running suite '$SuiteName' with runner '$RunnerName'..."
    python -m ai_local_bench.cli run --suite $SuiteName --runner $RunnerName --output-dir $OutputDir
    if ($LASTEXITCODE -ne 0) {
        throw "Suite failed: $SuiteName ($RunnerName)"
    }
}

if ($RunOllamaBaseline) {
    Invoke-BenchmarkSuite -SuiteName $OllamaSuite -RunnerName "ollama"
}

if ($RunLlamaCppVulkan) {
    Invoke-BenchmarkSuite -SuiteName $LlamaSuite -RunnerName "llamacpp"
}
