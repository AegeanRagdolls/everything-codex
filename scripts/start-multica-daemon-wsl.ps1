param(
    [string]$Distro = "Ubuntu"
)

$ErrorActionPreference = "Stop"

function Convert-WindowsPathToWslPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $normalized = $Path -replace "\\", "/"
    if ($normalized -match "^([A-Za-z]):(.*)$") {
        $drive = $matches[1].ToLower()
        $rest = $matches[2]
        return "/mnt/$drive$rest"
    }

    throw "Unsupported Windows path: $Path"
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ensureScriptWindows = Join-Path $scriptDir "ensure-multica-daemon.sh"
if (-not (Test-Path $ensureScriptWindows)) {
    throw "Missing ensure script: $ensureScriptWindows"
}

$ensureScriptWsl = Convert-WindowsPathToWslPath -Path $ensureScriptWindows
$ensureScriptWslEscaped = $ensureScriptWsl -replace "'", "'\\''"

& wsl.exe -d $Distro -- /bin/bash -lc "'$ensureScriptWslEscaped'"
exit $LASTEXITCODE
