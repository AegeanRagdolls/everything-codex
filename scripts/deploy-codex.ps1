param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]] $DeployArgs
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $ScriptDir
python "$Root\scripts\deploy-codex.py" @DeployArgs
