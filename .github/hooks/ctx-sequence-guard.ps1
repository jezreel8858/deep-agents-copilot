# ctx-sequence-guard.ps1
#
# Circuit Breaker MECANICO (R-046 / R-059 / R-060 / Smell 2.26 - Anti MCP Tool Chaining Sequencial).
# Hook PreToolUse UNICO (telemetria original do context-mode + guard mesclados em um so comando,
# para evitar depender de suporte a multiplas entradas de hook por evento no host).
#
# Fail-open por design: qualquer falha interna sempre permite a chamada.
#
# NOTA (R-048 cwd bootstrap): este script e invocado por um bootstrap inline em context-mode.json
# que resolve o caminho real do projeto via campo "cwd" do payload JSON (o host as vezes nao honra
# o "cwd" declarado na config de hook, executando o processo a partir da pasta de instalacao do IDE).
# O bootstrap repassa o conteudo do stdin original como PARAMETRO posicional (-StdinOverride),
# porque pipeline ($in | & $p) nao preenche [Console]::In em processo ja iniciado (stdin ja consumido
# pelo proprio bootstrap ao ler o payload para extrair o "cwd").

param(
    [Parameter(Position = 0)]
    [string]$StdinOverride = $null
)

$ErrorActionPreference = 'Stop'

function Write-Allow {
    Write-Output '{"permissionDecision":"allow"}'
    exit 0
}

try {
    if ($StdinOverride) {
        $stdin = $StdinOverride
    } else {
        $stdin = [Console]::In.ReadToEnd()
    }
    if ($null -eq $stdin) { $stdin = '' }

    $stateDir = Join-Path $PSScriptRoot '.state'
    New-Item -ItemType Directory -Force -Path $stateDir -ErrorAction SilentlyContinue | Out-Null
    $stateFile = Join-Path $stateDir 'ctx-sequence-guard.json'
    $debugLog = Join-Path $stateDir 'ctx-sequence-guard.debug.log'

    try {
        $preview = $stdin.Substring(0, [Math]::Min(200, $stdin.Length)) -replace "`r|`n", ' '
        $line = "[{0}] invoked pid={1} stdin_len={2} preview={3}" -f (Get-Date).ToUniversalTime().ToString('o'), $PID, $stdin.Length, $preview
        Add-Content -Path $debugLog -Value $line -ErrorAction SilentlyContinue
    } catch {}

    if (Get-Command context-mode -ErrorAction SilentlyContinue) {
        try {
            $env:IDEA_INITIAL_DIRECTORY = $PWD.Path
            $stdin | context-mode hook jetbrains-copilot pretooluse *> $null
        } catch {}
    }

    if ([string]::IsNullOrWhiteSpace($stdin)) {
        Write-Allow
    }

    $payload = $stdin | ConvertFrom-Json -ErrorAction Stop

    $toolName = $null
    if ($payload.PSObject.Properties.Name -contains 'toolName') { $toolName = $payload.toolName }
    elseif ($payload.PSObject.Properties.Name -contains 'tool_name') { $toolName = $payload.tool_name }

    if ([string]::IsNullOrWhiteSpace($toolName)) {
        Write-Allow
    }

    $isCtxExecute = $toolName -match '^ctx_execute(_file)?$'

    if (-not $isCtxExecute) {
        Remove-Item -Path $stateFile -Force -ErrorAction SilentlyContinue
        Write-Allow
    }

    $counter = 0
    if (Test-Path $stateFile) {
        try {
            $state = Get-Content $stateFile -Raw -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop
            if ($state.PSObject.Properties.Name -contains 'counter') { $counter = [int]$state.counter }
        } catch {
            $counter = 0
        }
    }

    $counter += 1
    try {
        (@{ counter = $counter } | ConvertTo-Json -Compress) | Set-Content -Path $stateFile -Encoding UTF8 -ErrorAction Stop
    } catch {}

    if ($counter -ge 2) {
        $reason = 'Circuit Breaker R-046/R-059/R-060 (context-mode SKILL.md secao 4.1): 2+ chamadas consecutivas de ctx_execute/ctx_execute_file SEM ctx_batch_execute interposto. Isto e feedback automatizado corrigivel (equivalente a erro de lint) - NAO pare, NAO peca permissao ao usuario e NAO repita a mesma chamada isolada. Reconsolide TODOS os alvos pendentes desta tarefa em UMA unica chamada ctx_batch_execute(commands:[...], queries:[...]) e prossiga imediatamente.'
        $out = @{ permissionDecision = 'deny'; permissionDecisionReason = $reason } | ConvertTo-Json -Compress
        Write-Output $out
        exit 0
    }

    Write-Allow
}
catch {
    Write-Output '{"permissionDecision":"allow"}'
    exit 0
}

