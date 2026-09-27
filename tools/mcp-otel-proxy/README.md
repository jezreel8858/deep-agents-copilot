# MCP OTel Proxy (tools/mcp-otel-proxy)

Proxy leve e transparente para servidores de ferramentas MCP (Model Context Protocol).
Intercepta requisições JSON-RPC `tools/call`, calcula latência real, status e emite spans OpenTelemetry GenAI v1.41+ para o OTel Collector local e Langfuse.

## Recursos
- **Zero Overhead & Fail-Open**: Nunca bloqueia ou derruba a sessão MCP em caso de erro de telemetria.
- **Transparência de Protocolo**: Stdin e stdout são repassados sem qualquer alteração de bytes.
- **Mascaramento de Segredos**: Higienização automática local de tokens Bearer, chaves GitHub, chaves AWS e credenciais Langfuse.
- **Suporte a Rollback**: Variável de ambiente `MCP_OTEL_DISABLED=true` desativa a telemetria instantaneamente.
