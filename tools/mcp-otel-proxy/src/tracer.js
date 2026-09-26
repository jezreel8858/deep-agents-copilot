/**
 * PX-03, PX-04, PX-06, PX-07, PX-11:
 * Emissor de telemetria OTLP fail-open para OpenTelemetry Collector / Langfuse
 */
const http = require('http');
const crypto = require('crypto');
const { truncateAndRedact } = require('./redact');

function randomHex(bytes) {
  return crypto.randomBytes(bytes).toString('hex');
}

class OTelMcpTracer {
  constructor(options = {}) {
    this.serverName = options.serverName || 'mcp-server';
    this.otlpEndpoint = options.endpoint || process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318';
    this.serviceName = options.serviceName || process.env.OTEL_SERVICE_NAME || 'mcp-otel-proxy';
    this.captureContent = (process.env.MCP_OTEL_CAPTURE_CONTENT === 'true') || options.captureContent || false;
    this.maxAttrBytes = parseInt(process.env.MCP_OTEL_MAX_ATTR_BYTES, 10) || 16384;
    this.toolTimeoutMs = parseInt(process.env.MCP_OTEL_TOOL_TIMEOUT_MS, 10) || 120000;
    
    // Map de requisições pendentes por ID
    this.pending = new Map();
    this.url = new URL(this.otlpEndpoint.endsWith('/v1/traces') ? this.otlpEndpoint : `${this.otlpEndpoint.replace(/\/+$/, '')}/v1/traces`);
  }

  onRequest(json) {
    if (!json || typeof json !== 'object') return;
    const { id, method, params } = json;
    if (id === undefined || id === null) return; // notificação

    const nowNano = BigInt(Date.now()) * 1000000n;
    
    // Extrai traceparent do _meta se presente
    let parentSpanId = null;
    let traceId = null;
    if (params && params._meta && params._meta.traceparent) {
      const parts = String(params._meta.traceparent).split('-');
      if (parts.length === 4) {
        traceId = parts[1];
        parentSpanId = parts[2];
      }
    }
    if (!traceId) {
      traceId = randomHex(16);
    }

    const spanId = randomHex(8);
    const toolName = method === 'tools/call' && params && params.name ? params.name : null;

    this.pending.set(id, {
      traceId,
      spanId,
      parentSpanId,
      startTimeNano: nowNano,
      method,
      toolName,
      params
    });
  }

  onResponse(json, rawByteLength = 0) {
    if (!json || typeof json !== 'object') return;
    const { id, result, error } = json;
    if (id === undefined || id === null) return;

    const req = this.pending.get(id);
    if (!req) return;
    this.pending.delete(id);

    const endTimeNano = BigInt(Date.now()) * 1000000n;
    this.exportSpan(req, result, error, endTimeNano, rawByteLength);
  }

  exportSpan(req, result, error, endTimeNano, rawByteLength) {
    try {
      const isError = Boolean(error || (result && result.isError));
      let statusCode = isError ? 2 : 1; // 1: Ok, 2: Error
      let statusMessage = isError ? (error ? error.message : 'tool_error') : 'success';

      const attributes = [
        { key: "gen_ai.operation.name", value: { stringValue: "execute_tool" } },
        { key: "gen_ai.provider.name", value: { stringValue: "github-copilot" } },
        { key: "gen_ai.tool.type", value: { stringValue: "mcp" } },
        { key: "mcp.server.name", value: { stringValue: this.serverName } },
        { key: "mcp.method.name", value: { stringValue: req.method } },
        { key: "tool.execution.status", value: { stringValue: statusMessage } },
        { key: "mcp.result.bytes", value: { intValue: String(rawByteLength) } }
      ];

      if (req.toolName) {
        attributes.push({ key: "gen_ai.tool.name", value: { stringValue: `${this.serverName}/${req.toolName}` } });
      }

      if (this.captureContent && req.params) {
        const argsStr = truncateAndRedact(req.params.arguments || req.params, this.maxAttrBytes);
        attributes.push({ key: "gen_ai.tool.call.arguments", value: { stringValue: argsStr } });
      }

      if (this.captureContent && result) {
        const resStr = truncateAndRedact(result, this.maxAttrBytes);
        attributes.push({ key: "gen_ai.tool.call.result", value: { stringValue: resStr } });
      }

      if (error) {
        attributes.push({ key: "error.code", value: { intValue: String(error.code || -1) } });
        attributes.push({ key: "error.message", value: { stringValue: error.message || 'Unknown error' } });
      }

      const span = {
        traceId: req.traceId,
        spanId: req.spanId,
        name: req.toolName ? `execute_tool: ${this.serverName}/${req.toolName}` : `mcp:${this.serverName}/${req.method}`,
        kind: 1, // INTERNAL
        startTimeUnixNano: req.startTimeNano.toString(),
        endTimeUnixNano: endTimeNano.toString(),
        attributes,
        status: { code: statusCode, message: statusMessage }
      };

      if (req.parentSpanId) {
        span.parentSpanId = req.parentSpanId;
      }

      const payload = {
        resourceSpans: [
          {
            resource: {
              attributes: [
                { key: "service.name", value: { stringValue: this.serviceName } },
                { key: "service.namespace", value: { stringValue: "deep-agents" } },
                { key: "mcp.server", value: { stringValue: this.serverName } }
              ]
            },
            scopeSpans: [
              {
                scope: { name: "mcp-otel-proxy", version: "1.0.0" },
                spans: [span]
              }
            ]
          }
        ]
      };

      this.dispatch(payload);
    } catch (e) {
      // Fail-open: nunca interromper proxy por falha de telemetria
    }
  }

  dispatch(payload) {
    try {
      const data = JSON.stringify(payload);
      const req = http.request({
        hostname: this.url.hostname,
        port: this.url.port || 80,
        path: this.url.pathname,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(data)
        },
        timeout: 2000
      });

      req.on('error', () => { /* fail-open silencioso */ });
      req.on('timeout', () => { req.destroy(); });
      req.write(data);
      req.end();
    } catch (err) {
      // fail-open
    }
  }
}

module.exports = { OTelMcpTracer };
