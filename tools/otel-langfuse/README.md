# Observabilidade de Agents: OpenTelemetry Collector Proxy + Langfuse Cloud

Infraestrutura de observabilidade e tracing distribuído em tempo real para os agentes do **GitHub Copilot** e **Claude Code**, utilizando **Langfuse Cloud** (SaaS gerenciado) em conformidade com as convenções [OTel GenAI Semantic Conventions v1.41+](../../.github/skills/agent-observability-otel/SKILL.md).

> [!WARNING]
> **Limitação Conhecida (Known Issue - IntelliJ IDEA)**:
> A exportação nativa de telemetria OTel pelo plugin do **GitHub Copilot no IntelliJ IDEA** ainda **não emite os traces esperados** para o coletor local (`http://127.0.0.1:4318`), tratando-se de uma limitação do plugin da IDE.
> 
> Em contrapartida, o pipeline de infraestrutura — composto pelo **OTel Collector Proxy Local**, autenticação OTLP e despacho para o **Langfuse Cloud** — está **comprovadamente testado e 100% operacional** via testes sintéticos (`test-trace.js` e `test_trace.py`).

---

## 🎯 Por que Langfuse Cloud? (Zero Footprint Local)

A arquitetura adota **Langfuse Cloud** (plano gratuito generoso de até **50.000 traces/mês**) em substituição ao stack Docker local:
- 🚀 **Zero CPU e RAM local**: Elimina a necessidade de contêineres pesados como PostgreSQL, ClickHouse, MinIO e Redis rodando localmente.
- 🛡️ **Foco em Governança**: Mantém a máquina de desenvolvimento leve, ágil e focada na execução dos agentes e testes.
- 🌐 **Dashboard Gerenciado e Evals**: Interface web pronta e mantida em alta disponibilidade em [cloud.langfuse.com](https://cloud.langfuse.com).

---

## 🏛️ Arquitetura de Telemetria

```mermaid
flowchart LR
    IDE["IDE Host (VS Code / JetBrains)\nCopilot / Claude Code"] -- "OTLP HTTP (:4318)" --> Collector["OTel Collector Proxy Local\n(Normalização + Redact de Segredos)"]
    Collector -- "HTTPS (:443)\nOTLP + Basic Auth" --> LangfuseCloud["Langfuse Cloud (SaaS)\nhttps://cloud.langfuse.com"]
    Collector -. "traces.json / metrics.json" .-> LocalLog[("Auditoria Local (Opcional)")]
```

Existem duas formas de conexão suportadas:
1. **Via OTel Collector Proxy Local (Recomendado)**: O coletor roda como processo leve em background, mascarando segredos locais e normalizando Semconv v1.41+ antes do envio seguro para a nuvem.
2. **Direto da IDE/MCP para Langfuse Cloud**: A IDE despacha OTLP HTTP diretamente para o endpoint SaaS com header Basic Auth, sem necessidade de coletor local intermediário.

---

## 🚀 Configuração Rápida em 3 Passos

### 1. Criar Projeto no Langfuse Cloud
1. Acesse **[cloud.langfuse.com](https://cloud.langfuse.com)** (ou `us.cloud.langfuse.com` para região US) e faça login gratuito.
2. Crie um projeto chamado, por exemplo, `deep-agents-copilot`.
3. Navegue até **Settings → API Keys** e gere um novo par de chaves:
   - **Public Key**: `pk-lf-...`
   - **Secret Key**: `sk-lf-...`
4. Crie o token Basic Auth em Base64 combinando `public_key:secret_key`:
   - **Linux/macOS / Git Bash**:
     ```bash
     echo -n "pk-lf-xxx:sk-lf-yyy" | base64
     ```
   - **PowerShell (Windows)**:
     ```powershell
     [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("pk-lf-xxx:sk-lf-yyy"))
     ```

### 2. Configurar o Arquivo `.env`
Copie o exemplo e insira seu token:
```bash
cp .env.example .env
```
Preencha a variável `LANGFUSE_OTLP_AUTH` com a string Base64 gerada.

### 3. Executar o Coletor Leve (Proxy OTel)
Você pode rodar apenas o coletor OTel Contrib oficial sem nenhum banco local:

**Via Docker (Apenas o coletor leve, ~45MB RAM, 0% CPU):**
- **Git Bash (Windows)**:
  ```bash
  MSYS_NO_PATHCONV=1 docker run -d \
    --name otel-proxy \
    --restart unless-stopped \
    -p 4318:4318 -p 4317:4317 \
    -e LANGFUSE_OTLP_AUTH="<seu_token_base64>" \
    -v "d:/workspace/deep-agents-copilot/tools/otel-langfuse/otel-collector-config.yaml:/etc/otelcol-contrib/config.yaml:ro" \
    otel/opentelemetry-collector-contrib:latest \
    --config=/etc/otelcol-contrib/config.yaml
  ```
- **Linux / macOS**:
  ```bash
  docker run -d \
    --name otel-proxy \
    --restart unless-stopped \
    -p 4318:4318 -p 4317:4317 \
    -e LANGFUSE_OTLP_AUTH="<seu_token_base64>" \
    -v "$(pwd)/otel-collector-config.yaml":/etc/otelcol-contrib/config.yaml:ro \
    otel/opentelemetry-collector-contrib:latest \
    --config=/etc/otelcol-contrib/config.yaml
  ```

---

## ⚙️ Configuração da IDE (IntelliJ IDEA e VS Code)

### IntelliJ IDEA (JetBrains) — *Limitação Conhecida*

> **Aviso:** A funcionalidade de exportação no plugin JetBrains do GitHub Copilot encontra-se inativa/não funcional nas versões atuais (não gera tráfego de rede OTLP no endpoint local). Os parâmetros abaixo são mantidos como referência para homologação futura:

Em **Settings → Tools → GitHub Copilot → Chat → Open Telemetry**:
| Campo na IDE | Valor | Observação |
|---|---|---|
| **Enable Open Telemetry export** | `[x]` (Habilitado) | Habilita a emissão |
| **Exporter type** | `otlp-http` | Protocolo HTTP |
| **OTLP protocol** | `http/json` | Suportado pelo coletor |
| **OTLP endpoint** | `http://127.0.0.1:4318` | Aponta para o proxy local |
| **Capture prompt/response content** | `[x]` (Habilitado) | Registra conteúdo de prompts/respostas |
| **Service name** | `deep-agents-copilot` | Nome do serviço no Langfuse |
| **Resource attributes** | *(vazio)* | O proxy injeta as credenciais |

*Requer restart da IDE para entrar em vigor.*

### VS Code
No arquivo `settings.json` do VS Code:
```json
{
  "github.copilot.chat.otel.enabled": true,
  "github.copilot.chat.otel.exporterType": "otlp-http",
  "github.copilot.chat.otel.otlpEndpoint": "http://127.0.0.1:4318",
  "github.copilot.chat.otel.protocol": "http/json",
  "github.copilot.chat.otel.serviceName": "deep-agents-copilot",
  "github.copilot.chat.otel.captureContent": true
}
```

---

## 🔍 Como Validar a Conexão

Execute o script de trace sintético via Node.js:
```bash
node test-trace.js
```

Saída esperada:
```text
📡 Enviando spans de teste (invoke_agent + execute_tool MCP) para http://localhost:4318/v1/traces ...
✅ Sucesso! Status HTTP: 200
OTel Collector recebeu os spans e despachou para o Langfuse Cloud.
Acesse https://cloud.langfuse.com para visualizar o trace no dashboard.
```

Abra o dashboard no **[cloud.langfuse.com](https://cloud.langfuse.com)** e confira o trace com spans `invoke_agent` e `execute_tool` com Semconv v1.41+ higienizados.
