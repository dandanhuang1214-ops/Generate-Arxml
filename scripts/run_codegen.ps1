param(
  [string]$Config = "config/project.yaml",
  [switch]$DryRun,
  [string]$CreateTemplate = ""
)

$python = "python"
if (Test-Path ".\.venv\Scripts\python.exe") {
  $python = ".\.venv\Scripts\python.exe"
} elseif (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw "Python is unavailable. Install Python 3.12 and rebuild .venv before running code generation."
}

& $python -c "import arxml_codegen, lxml, openpyxl, yaml" 2>$null
if ($LASTEXITCODE -ne 0) {
  throw "Python environment is incomplete. Run: .\.venv\Scripts\python.exe -m pip install -e '.[dev]'"
}

$env:PYTHONPATH = "src"

$args = @("-m", "arxml_codegen.cli", "--config", $Config)
if ($DryRun) {
  $args += "--dry-run"
}
if ($CreateTemplate) {
  $args += @("--create-template", $CreateTemplate)
}

& $python @args
