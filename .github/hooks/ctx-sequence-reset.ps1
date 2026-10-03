# ctx-sequence-reset.ps1
# Hook SessionStart UNICO (telemetria original do context-mode + reset do circuit breaker
# mesclados em um so comando).
$ErrorActionPreference = 'SilentlyContinue'

$stateDir = Join-Path $PSScriptRoot '.state'
New-Item -ItemType Directory -Force -Path $stateDir -ErrorAction SilentlyContinue | Out-Null

try {
    $line = "[{0}] session-reset invoked pid={1}" -f (Get-Date).ToUniversalTime().ToString('o'), $PID
    Add-Content -Path (Join-Path $stateDir 'ctx-sequence-guard.debug.log') -Value $line -ErrorAction SilentlyContinue
} catch {}

if (Get-Command context-mode -ErrorAction SilentlyContinue) {
    try {
        $env:IDEA_INITIAL_DIRECTORY = $PWD.Path
        context-mode hook jetbrains-copilot sessionstart *> $null
    } catch {}
}

Remove-Item -Path (Join-Path $stateDir 'ctx-sequence-guard.json') -Force -ErrorAction SilentlyContinue
exit 0

