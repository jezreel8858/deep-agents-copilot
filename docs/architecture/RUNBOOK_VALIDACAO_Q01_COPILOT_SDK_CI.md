---
title: "Runbook Operacional — Validação de Autenticação e Billing do Copilot SDK em CI (Q-01)"
type: runbook
status: active
owner: governance-team
subtask: 26
gate_alvo: "Gate PoC -> Piloto (subtask 27)"
date: 2025-05-18
---

# Runbook Operacional — Validação de Autenticação e Billing do Copilot SDK em CI (Q-01)

## 1. Objetivo

Confirmar empiricamente qual modelo de autenticação e tarifação (billing/quota) funciona para a execução headless do `governance-runner` via GitHub Actions real, eliminando a incerteza de faturamento e permissões da questão arquitetural Q-01 antes de autorizar a transição de fase no Gate PoC $\to$ Piloto (subtask 27).

---

## 2. Pré-requisitos

Antes de iniciar qualquer procedimento, valide o checklist mandatório abaixo:

- [ ] Acesso administrativo (`admin` ou `owner`) ao repositório GitHub e à organização proprietária.
- [ ] Licença ativa de GitHub Copilot Business ou Enterprise na organização (para Opção A ou B) OU conta ativa com créditos em provedor de IA suportado (OpenAI, Azure OpenAI ou Anthropic, para Opção C).
- [ ] Branch de teste isolada criada a partir da branch base atual (ex.: `test/poc-q01-copilot-auth`), evitando commits diretos em branches protegidas (`main` ou `develop`).
- [ ] Acesso ao painel de faturamento da organização (`Settings` $\to$ `Billing and plans` $\to$ `Copilot`) para inspeção de consumo pós-teste.

---

## 3. Opção A — GITHUB_TOKEN com Política de Organização (Caminho Recomendado)

Esta é a opção com menor custo operacional e de governança de segredos, pois utiliza o token efêmero nativo emitido pelo GitHub Actions para o workflow.

### 3.1. Ativação da Política na Organização (Admin da Organização)

1. Acesse a organização no GitHub: `https://github.com/organizations/<sua-org>/settings/copilot/policies`.
2. Localize a seção **Copilot in the CLI / Automations**.
3. Habilite a opção **"Allow use of Copilot CLI billed to the organization"** (ou política equivalente para automações e Actions).
4. Salve as alterações.

### 3.2. Ajuste no Workflow (`.github/workflows/governance-agent-audit.yml`)

Edite o arquivo do workflow na branch de teste para adicionar a permissão de escrita de requisições Copilot e mapear o token nativo:

```yaml
# Trecho de permissões no topo do arquivo (ajuste necessário):
permissions:
  contents: read
  pull-requests: write
  checks: write
  copilot-requests: write # <-- ADICIONAR ESTA LINHA
```

Na etapa de execução do `governance-runner`, altere o mapeamento da variável de ambiente:

| Configuração | Padrão Atual (com Secret) | Variante Opção A (`GITHUB_TOKEN`) |
| :--- | :--- | :--- |
| **Fonte do Token** | `secrets.COPILOT_SDK_TOKEN` | `github.token` / `secrets.GITHUB_TOKEN` |
| **Declaração `env`** | `COPILOT_SDK_TOKEN: ${{ secrets.COPILOT_SDK_TOKEN }}` | `COPILOT_SDK_TOKEN: ${{ github.token }}` |

### 3.3. Execução e Validação

1. Na branch `test/poc-q01-copilot-auth`, realize uma modificação pontual em qualquer agente sob `.github/agents/` (ex.: adicione um comentário ou newline).
2. Abra um Pull Request contra a branch principal (não marcar como Draft).
3. Monitore a execução do job `Governance · Agent Audit` na aba **Actions**.
4. Verifique nos logs e no Job Summary:
   - Sucesso da etapa `Executar auditoria de governança (agent-audit)`.
   - Ausência de status HTTP 401 (*Unauthorized*) ou 403 (*Forbidden*).

---

## 4. Opção B — PAT Fine-Grained Dedicado (`COPILOT_SDK_TOKEN`)

Opção necessária caso a organização restrinja o faturamento via `GITHUB_TOKEN` nativo ou opte por controle granular de quota via conta de serviço com assento (seat) Copilot explicitamente atribuído.

### 4.1. Conta e Licença

> **Atenção:** Não existe conta de serviço do tipo "machine user" gratuita para Copilot; a conta utilizada consome 1 assento (seat) comercial ativo da licença Business/Enterprise.

1. Identifique ou crie uma conta técnica de serviço no GitHub (ex.: `bot-governance-service`).
2. Garanta que a conta possui licença ativa de GitHub Copilot atribuída na organização.
3. Conceda permissão de leitura (`Read`) ao repositório alvo para a conta técnica.

### 4.2. Geração do Fine-Grained Personal Access Token (PAT)

1. Autenticado como a conta de serviço, navegue até: `Settings` $\to$ `Developer settings` $\to$ `Personal access tokens` $\to$ `Fine-grained tokens` $\to$ **Generate new token**.
2. Defina o nome: `gov-runner-copilot-sdk-ci`.
3. Defina a expiração conforme política corporativa (ex.: 90 dias).
4. Em **Repository access**, selecione **Only select repositories** e escolha o repositório do projeto.
5. Em **Permissions**:
   - Localize **Copilot Requests** (ou escopo de API correspondente na interface).
   - Defina o acesso como **Access: Read and Write** (ou `write`).
6. Gere e copie o token seguro.

### 4.3. Registro do Secret no Repositório

1. No repositório alvo, vá em: `Settings` $\to$ `Secrets and variables` $\to$ `Actions` $\to$ **New repository secret**.
2. Nome: `COPILOT_SDK_TOKEN`.
3. Valor: cole o PAT gerado no passo anterior.
4. Salve o secret.

### 4.4. Execução e Validação

1. O workflow `.github/workflows/governance-agent-audit.yml` já consome nativamente `secrets.COPILOT_SDK_TOKEN`, não requerendo alterações no bloco `env`.
2. Abra ou sincronize o PR de teste na branch `test/poc-q01-copilot-auth`.
3. Inspecione a execução na aba **Actions** e confirme ausência de falhas 401/403.

---

## 5. Opção C — BYOK (Bring Your Own Key — Sem Licença GitHub Copilot)

Caso a organização não disponha de licenças GitHub Copilot para CI ou prefira direcionar o custo das chamadas LLM diretamente a um provedor externo (OpenAI, Azure OpenAI ou Anthropic).

### 5.1. Obtenção das Credenciais no Provedor

1. Obtenha a API Key e Endpoint junto ao provedor de nuvem/IA aprovado.
2. Cadastre a chave nos secrets do repositório (ex.: `OPENAI_API_KEY` ou `AZURE_OPENAI_API_KEY`).

### 5.2. Verificação Obrigatória no Código do Adapter

> **Aviso Técnico (Grounded):** O arquivo `tools/headless-governance-runner/src/governance_runner/runner/sdk_adapter.py` implementa a criação de cliente na função `criar_cliente_sdk_real()`. Antes de executar esta opção em CI:
> 1. Inspecione a assinatura e o corpo de `criar_cliente_sdk_real()` no branch atual.
> 2. Confirme o nome exato das variáveis de ambiente e parâmetros esperados pelo cliente do SDK suportado no repositório.
> 3. Caso `criar_cliente_sdk_real()` levante `NotImplementedError`, a integração real do SDK para BYOK deverá ser completada conforme a documentação oficial `use-byok-models` e o FAQ de `github/copilot-sdk`.

### 5.3. Ajuste do Workflow para BYOK

Substitua a dependência de `COPILOT_SDK_TOKEN` pelas variáveis de ambiente do provedor:

```yaml
        env:
          # Exemplo para OpenAI nativo:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GH_TOKEN: ${{ github.token }}
          OTEL_EXPORTER_OTLP_ENDPOINT: http://localhost:4318
          GOV_MAX_PREMIUM_REQUESTS: '15'
```

---

## 6. Critérios de Sucesso (Definition of Done — Subtask 26)

A subtask 26 é considerada concluída e aprovada quando todos os itens abaixo forem rigorosamente atendidos:

- [ ] **Execução sem falhas de autenticação**: Workflow `governance-agent-audit.yml` executa ponta a ponta sem erros HTTP 401, 403 ou `SDKAuthenticationError`.
- [ ] **Veredito neutro confirmado**: O relatório gerado pela auditoria (`RelatorioAuditoria`) emite `veredito="neutral"`, sem falhar o build e sem bloquear o merge do PR.
- [ ] **Teto orçamentário respeitado**: O total de requisições premium consumidas pelo runner não excede o limite estabelecido de `GOV_MAX_PREMIUM_REQUESTS=15`.
- [ ] **Verificação de quota/billing**: Inspeção manual realizada no painel de Billing confirmando a origem da tarifação (débito em pool corporativo ou em usuário individual).
- [ ] **Seção 7 preenchida**: Evidências, links e dados factuais registrados formalmente neste documento.

---

## 7. Registro do Resultado (Preenchimento pelo Executor Humano)

*Instruções: O responsável pela execução manual deve preencher os campos abaixo logo após a conclusão dos testes.*

| Item de Registro | Valor Observado |
| :--- | :--- |
| **Opção testada** | `[PREENCHER: Opção A / Opção B / Opção C]` |
| **Data da execução** | `[PREENCHER: AAAA-MM-DD]` |
| **Executor responsável** | `[PREENCHER: @usuario_github]` |
| **Link do Pull Request de teste** | `[PREENCHER: URL do PR]` |
| **Link da execução no Actions** | `[PREENCHER: URL do Run no GitHub Actions]` |
| **Status da autenticação** | `[PREENCHER: Sucesso (200) / Falha (401/403)]` |
| **Veredito do relatório gerado** | `[PREENCHER: neutral / outro]` |
| **Total de premium requests consumidos** | `[PREENCHER: número <= 15]` |
| **Origem do billing / Quota debitada** | `[PREENCHER: Pool da Organização / Conta Individual / Fatura Externa Provedor]` |
| **Decisão para Subtask 27 (Gate PoC $\to$ Piloto)** | `[PREENCHER: APROVADO para avanço / REPROVADO (justificar)]` |

### Observações Adicionais do Teste
`[PREENCHER: Detalhes sobre tempo de resposta, comportamento do OTel Collector ou particularidades da organização]`

---

## 8. Procedimento de Rollback

Caso ocorram falhas impeditivas, erros recorrentes de autorização ou consumo imprevisto de quota/créditos durante a validação:

1. **Remover Tokens e Segredos**:
   - Acesse `Settings` $\to$ `Secrets and variables` $\to$ `Actions` e remova o secret `COPILOT_SDK_TOKEN` (caso a Opção B tenha sido configurada).
   - Se gerou um PAT para a conta de serviço, acesse a conta e revogue o token imediatamente.
2. **Reverter Alterações no Workflow**:
   - Reverta quaisquer commits na branch de teste que adicionem `permissions: copilot-requests: write` ou variáveis experimentais no arquivo `.github/workflows/governance-agent-audit.yml`.
3. **Encerrar PR de Teste**:
   - Feche o Pull Request de teste sem realizar merge para a branch principal (`Close pull request`).
4. **Desativar Política na Organização (se necessário)**:
   - Se a Opção A foi ativada exclusivamente para este teste e deve ser revogada, retorne a `Settings` $\to$ `Copilot` $\to$ `Policies` na organização e desabilite o faturamento corporativo para automações.
