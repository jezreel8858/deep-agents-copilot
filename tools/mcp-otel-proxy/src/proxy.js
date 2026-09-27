/**
 * PX-01, PX-02, PX-09:
 * Proxy stdio transparente e bidirecional para processos de servidor MCP
 */
const { spawn } = require('child_process');
const readline = require('readline');
const { OTelMcpTracer } = require('./tracer');

function runProxy(options) {
  const { serverName, command, args } = options;
  const disabled = process.env.MCP_OTEL_DISABLED === 'true';

  const child = spawn(command, args, {
    stdio: ['pipe', 'pipe', 'inherit'],
    shell: false
  });

  if (disabled) {
    process.stdin.pipe(child.stdin);
    child.stdout.pipe(process.stdout);
    child.on('exit', (code, signal) => {
      process.exit(code !== null ? code : 1);
    });
    return;
  }

  const tracer = new OTelMcpTracer({ serverName });

  // 1. STDIN: Parent (Copilot IDE) -> Proxy -> Child (MCP Server)
  const rlStdin = readline.createInterface({
    input: process.stdin,
    crlfDelay: Infinity,
    terminal: false
  });

  rlStdin.on('line', (line) => {
    // Repassa imediatamente os bytes intocados ao processo filho (PX-01)
    child.stdin.write(line + '\n');

    // Parse assíncrono/fail-open para interceptação de telemetria
    try {
      if (line.trim().length > 0) {
        const json = JSON.parse(line);
        tracer.onRequest(json);
      }
    } catch (e) {
      // Linha não JSON ou parse error: ignorar sem falhar
    }
  });

  // 2. STDOUT: Child (MCP Server) -> Proxy -> Parent (Copilot IDE)
  const rlStdout = readline.createInterface({
    input: child.stdout,
    crlfDelay: Infinity,
    terminal: false
  });

  rlStdout.on('line', (line) => {
    // Repassa imediatamente os bytes intocados ao pai (PX-01, PX-02)
    process.stdout.write(line + '\n');

    try {
      if (line.trim().length > 0) {
        const json = JSON.parse(line);
        tracer.onResponse(json, Buffer.byteLength(line));
      }
    } catch (e) {
      // Ignorar sem falhar
    }
  });

  // 3. Ciclo de vida (PX-09)
  child.on('error', (err) => {
    process.stderr.write(`[mcp-otel-proxy] Erro ao iniciar subprocesso: ${err.message}\n`);
    process.exit(1);
  });

  child.on('exit', (code, signal) => {
    process.exit(code !== null ? code : 1);
  });

  process.on('SIGINT', () => { child.kill('SIGINT'); });
  process.on('SIGTERM', () => { child.kill('SIGTERM'); });
}

module.exports = { runProxy };
