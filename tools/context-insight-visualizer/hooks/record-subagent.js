#!/usr/bin/env node
/**
 * record-subagent.js — Hook GitHub Copilot para Telemetria Nativa de Subagentes
 * ==============================================================================
 * Executado pelo GitHub Copilot no evento postToolUse (declarado em .github/hooks/subagent-telemetry.json).
 * Captura chamadas de 'run_subagent' e grava registro estruturado em JSONL no repositório.
 *
 * Características:
 * - 100% nativo e portável (qualquer desenvolvedor que clonar o repo já herda a telemetria).
 * - Zero dependências npm além do Node.js já em uso pela IDE.
 * - Execução ultrarrápida (< 5ms), síncrona e não-bloqueante.
 * - Trata variações camelCase (Copilot CLI) e snake_case (JetBrains/VS Code).
 * - Saída silenciosa para stdout (não interfere no fluxo do modelo).
 */

const fs = require('fs');
const path = require('path');

try {
  // Leitura síncrona de stdin com tratamento de encoding
  const raw = fs.readFileSync(0, 'utf8').trim();
  if (!raw) {
    process.exit(0);
  }

  const payload = JSON.parse(raw);

  // Normalização de nomes de ferramenta (suporta camelCase e snake_case)
  const toolName = payload.tool_name || payload.toolName || payload.name || '';
  if (toolName !== 'run_subagent' && toolName !== 'subagent') {
    process.exit(0);
  }

  const toolInput = payload.tool_input ?? payload.toolArgs ?? payload.arguments ?? payload.args ?? {};
  const agentName = (toolInput.agentName || toolInput.name || 'search').toLowerCase().trim();
  const description = String(toolInput.description || '').slice(0, 200);
  const task = String(toolInput.task || '').slice(0, 300);
  const sessionId = String(payload.session_id || payload.sessionId || 'default');

  let timestamp = new Date().toISOString();
  if (payload.timestamp) {
    try {
      timestamp = typeof payload.timestamp === 'number'
        ? new Date(payload.timestamp).toISOString()
        : new Date(String(payload.timestamp)).toISOString();
    } catch {
      timestamp = new Date().toISOString();
    }
  }

  const record = {
    timestamp,
    agent: agentName,
    description,
    task,
    sessionId,
  };

  // Garante que o diretório de logs exista
  const logsDir = path.resolve(__dirname, '..', 'logs');
  if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
  }

  const logFilePath = path.join(logsDir, 'subagent-telemetry.jsonl');
  fs.appendFileSync(logFilePath, JSON.stringify(record) + '\n', 'utf8');
} catch (err) {
  // Falhas no hook nunca devem interromper a execução do Copilot
}

process.exit(0);

