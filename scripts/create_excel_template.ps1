param(
  [string]$OutputPath = "D:\work\SOA\code\data\input\arxml_input_template.xlsx"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$python = "python"
if (Test-Path (Join-Path $repoRoot ".venv\Scripts\python.exe")) {
  $python = Join-Path $repoRoot ".venv\Scripts\python.exe"
}

$env:PYTHONPATH = Join-Path $repoRoot "src"
& $python -m arxml_codegen.cli --create-template $OutputPath
