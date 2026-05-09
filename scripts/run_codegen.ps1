param(
  [string]$Config = "config/project.yaml",
  [switch]$DryRun,
  [string]$CreateTemplate = ""
)

$python = "python"
if (Test-Path ".\.venv\Scripts\python.exe") {
  $python = ".\.venv\Scripts\python.exe"
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
