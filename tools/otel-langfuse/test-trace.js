#!/usr/bin/env node
const http = require('http');

const tracePayload = {
  resourceSpans: [
    {
      resource: {
        attributes: [
          { key: "service.name", value: { stringValue: "deep-agents-copilot" } },
          { key: "telemetry.sdk.name", value: { stringValue: "test-client" } }
        ]
      },
      scopeSpans: [
        {
          scope: { name: "test-scope", version: "1.0.0" },
          spans: [
            {
              traceId: "5b8aa5a2d2c872e8321cf37308d69df2",
              spanId: "051581bf3cb55c13",
              name: "invoke_agent: test-connectivity",
              kind: 1,
              startTimeUnixNano: String(Date.now() * 1000000),
              endTimeUnixNano: String((Date.now() + 250) * 1000000),
              attributes: [
                { key: "gen_ai.operation.name", value: { stringValue: "invoke_agent" } },
                { key: "gen_ai.agent.name", value: { stringValue: "agent-router" } },
                { key: "gen_ai.system", value: { stringValue: "github-copilot" } }
              ],
              status: { code: 1 }
            }
          ]
        }
      ]
    }
  ]
};

const data = JSON.stringify(tracePayload);

const options = {
  hostname: 'localhost',
  port: 4318,
  path: '/v1/traces',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(data)
  }
};

console.log('📡 Enviando span de teste para http://localhost:4318/v1/traces ...');

const req = http.request(options, (res) => {
  let responseData = '';
  res.on('data', (chunk) => { responseData += chunk; });
  res.on('end', () => {
    if (res.statusCode >= 200 && res.statusCode < 300) {
      console.log('✅ Sucesso! Status HTTP: ' + res.statusCode);
      console.log('OTel Collector recebeu o span e despachou para o Langfuse.');
      console.log('Acesse http://localhost:3000 para visualizar o trace.');
    } else {
      console.error('⚠️ OTel Collector respondeu com HTTP ' + res.statusCode + ': ' + responseData);
    }
  });
});

req.on('error', (err) => {
  console.error('❌ Falha ao conectar em http://localhost:4318/v1/traces:');
  console.error(err.message);
});

req.write(data);
req.end();
