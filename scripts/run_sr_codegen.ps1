param(
  [string]$Config = "config/project.yaml",
  [switch]$DryRun
)

$args = @("-m", "arxml_codegen.cli", "--config", $Config)
if ($DryRun) {
  $args += "--dry-run"
}

python @args
