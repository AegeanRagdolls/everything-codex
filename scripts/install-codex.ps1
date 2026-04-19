param(
  [switch]$All,
  [switch]$Core,
  [switch]$DryRun,
  [switch]$Force,
  [switch]$NoConfig,
  [string]$CodexHome = "$HOME/.codex",
  [string]$SkillsHome = "$HOME/.agents/skills"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Mode = if ($All) { "all" } else { "core" }

function Invoke-Action {
  param([scriptblock]$Action, [string]$Text)
  if ($DryRun) { Write-Host "[dry-run] $Text" } else { & $Action }
}

function Install-SkillDir {
  param([string]$Src)
  $Name = Split-Path -Leaf $Src
  $Dest = Join-Path $SkillsHome $Name
  if ((Test-Path $Dest) -and -not $Force) {
    Write-Host "skip existing skill: $Name (use -Force to replace)"
    return
  }
  if (Test-Path $Dest) {
    Invoke-Action { Remove-Item -Recurse -Force $Dest } "Remove-Item -Recurse -Force $Dest"
  }
  Invoke-Action { New-Item -ItemType Directory -Force -Path $SkillsHome | Out-Null } "New-Item -ItemType Directory -Force -Path $SkillsHome"
  Invoke-Action { Copy-Item -Recurse -Force $Src $Dest } "Copy-Item -Recurse -Force $Src $Dest"
  Write-Host "installed skill: $Name"
}

function Install-Bucket {
  param([string]$Bucket)
  $BucketPath = Join-Path (Join-Path $Root "skills") $Bucket
  Get-ChildItem -Directory $BucketPath | ForEach-Object { Install-SkillDir $_.FullName }
}

Write-Host "Codex config home: $CodexHome"
Write-Host "Codex skills home: $SkillsHome"
Write-Host "Mode: $Mode"
Invoke-Action { New-Item -ItemType Directory -Force -Path $CodexHome | Out-Null; New-Item -ItemType Directory -Force -Path $SkillsHome | Out-Null } "Create Codex config and skill directories"

Install-Bucket ".curated"
if ($Mode -eq "all") { Install-Bucket ".experimental" }

if (-not $NoConfig) {
  $ConfigSrc = Join-Path (Join-Path $Root ".codex") "config.toml"
  $ConfigDest = Join-Path $CodexHome "config.toml"
  if (-not (Test-Path $ConfigDest)) {
    Invoke-Action { Copy-Item -Force $ConfigSrc $ConfigDest } "Copy-Item -Force $ConfigSrc $ConfigDest"
    Write-Host "installed Codex config.toml"
  } else {
    $RefDir = Join-Path $CodexHome "everything-codex-code"
    $RefDest = Join-Path $RefDir "config.toml"
    Invoke-Action { New-Item -ItemType Directory -Force -Path $RefDir | Out-Null; Copy-Item -Force $ConfigSrc $RefDest } "Copy reference config to $RefDest"
    Write-Host "existing config.toml preserved; reference copied to $RefDest"
  }
}

Write-Host "Done. Restart Codex to pick up newly installed skills."
