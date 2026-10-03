---
name: interactive-wizard-patterns
description: >-
  Padrões para criação de scripts interativos e wizards passo a passo para operações que exigem intervenção humana (HITL), configuração de infraestrutura, credenciais, segredos de CI e migrações manuais de cutover. Use quando a automação 100% não for viável por restrições de permissão ou segurança. Não use para etapas totalmente automatizáveis.
tier: 2
category: process
triggers:
  - "wizard"
  - "setup interativo"
  - "passo a passo manual"
  - "inicialização guiada"
  - "scaffolding"
  - "HITL interativo"
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
source_docs:
  - .github/skills/terminal-governance/SKILL.md
---

# Interactive Wizard Patterns

> Base de conhecimento especializada na **criação de scripts interativos e assistentes passo a passo (wizards)** para conduzir desenvolvedores ou operadores por procedimentos manuais, sensíveis ou que requerem intervenção humana (HITL - Human-in-the-Loop).

---

## 0) Problema Resolvido & Princípios Fundamentais

Muitas operações de infraestrutura, credenciamento em provedores terceiros (AWS, Stripe, Auth0, GitHub Secrets) e migrações irreversíveis não podem ser executadas de forma 100% autônoma por um agente devido a restrições de segurança, ausência de credenciais de admin ou necessidade de aprovação humana explícita.

Ao mesmo tempo, guias textuais em READMEs longos são frequentemente executados com erros de digitação, etapas esquecidas ou confusão de variáveis de ambiente.

Um **wizard interativo** é um script executável (Bash ou PowerShell) que guia o operador passo a passo: abre as URLs necessárias no navegador, fornece instruções visuais exatas de navegação, captura os valores informados de forma segura e idempotente, atualiza os arquivos de configuração locais (`.env`) ou segredos remotos via CLI oficial (`gh secret`, `aws`) e exibe o progresso de cada estágio.

### Princípios Universais

1. **HITL Focado**: Usar wizards exclusivamente para passos que demandam decisão humana, login em interfaces gráficas ou posse de chaves mestras. Passos 100% automatizáveis devem ser rodados diretamente por scripts autônomos.
2. **Contexto Antes da Ação**: O script deve ler o repositório antes de interagir (inspecionando `.env.example`, workflows de CI e arquivos de configuração) para saber exatamente quais variáveis precisa produzir.
3. **UX Limpa e Focada**: Cada estágio limpa a tela e apresenta apenas a tarefa atual, indicando claramente `Estágio X de Y` e abrindo o link do painel automaticamente.
4. **Captura Segura de Segredos**: Segredos (tokens, senhas, chaves privadas) devem ser lidos com mascaramento no terminal (`read -s` / `Read-Host -AsSecureString`), nunca ecoados em texto claro.
5. **Idempotência**: O wizard deve atualizar arquivos de variáveis (`.env`) sem duplicar chaves ou corromper linhas pré-existentes.
6. **Portabilidade e Validação Estática**: Todo script de wizard deve passar em checagens estáticas (`bash -n`) antes de ser entregue.

---

## 1) Quando Usar vs Quando Não Usar

### Quando Usar
- Configuração inicial de ambiente local que exige obtenção de chaves de API em dashboards terceiros.
- Provisionamento de segredos de repositório no GitHub Actions via `gh secret set`.
- Procedimentos manuais de migração, cutover de banco de dados ou chaveamento de DNS.
- Fluxos de scaffolding interativo onde o operador escolhe configurações customizadas.

### Quando Não Usar
- Tarefas que a esteira de CI/CD ou um agente de IA pode executar sozinho sem interação humana.
- Automações de rotina de build, teste e lint (usar comandos padronizados de CLI).
- Coleta de dados simples que cabem em uma pergunta direta no chat do Copilot.

---

## 2) Arquitetura de Wizard Shell / Bash

Um wizard robusto é estruturado em estágios sequenciais com auxílio de uma biblioteca utilitária padronizada:

```
┌───────────────────────────────────────────────────────────��─┐
│ 1. Mapeamento de Estágios & Variáveis (Read Repo Context)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Loop de Estágios:                                        │
│    ├─ Limpar tela & exibir [Estágio X/N: Título]            │
│    ├─ Abrir URL no navegador (open / xdg-open / wslview)    │
│    ├─ Exibir instruções precisas de clique e cópia          │
│    ├─ Capturar entrada (ask / ask_secret)                   │
│    └─ Persistir saída idempotente (.env / gh secret)        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Resumo Conclusivo & Checklist de Verificação             │
└─────────────────────────────────────────────────────────────┘
```

### Funções Utilitárias Canônicas

- `stage "Título"`: Limpa o terminal, incrementa o contador e desenha o cabeçalho do estágio atual.
- `open_url "https://..."`: Detecta o ambiente operacional (macOS, Linux, WSL, Windows Git Bash) e abre a URL no navegador padrão.
- `ask "Prompt" VAR_NAME`: Lê entrada de texto convencional do usuário.
- `ask_secret "Prompt" VAR_NAME`: Lê entrada confidencial com input mascarado sem eco de caracteres.
- `write_env "KEY" "VALUE" [file]`: Adiciona ou atualiza idempotentemente a chave em um arquivo de variáveis.
- `confirm "Pergunta de confirmação"`: Bloqueia o avanço até que o usuário digite `y` ou `s` explicitamente antes de ações irreversíveis.

---

## 3) Artefatos Esperados

1. **Script Executável Padronizado**:
   - Salvo em `scripts/setup-<nome>.sh` ou `.scratch/wizards/`.
   - Permissão de execução configurada (`chmod +x`).
   - Cabeçalho `#!/usr/bin/env bash` com `set -euo pipefail`.
2. **Documentaç��o de Estágios**:
   - Mapeamento prévio dos estágios, variáveis produzidas e destinos de persistência.
3. **Template de Execução Rápida**:
   - Instruções sucintas no README ou issue informando como invocar o script.

---

## 4) Integração com CI/CD e Validação Estática

Antes de entregar ou executar o wizard:

1. **Validação de Sintaxe**:
   - Executar `bash -n <script.sh>` para garantir integridade sintática.
   - Executar `shellcheck <script.sh>` quando disponível para evitar armadilhas de quoting e expansão de variáveis.
2. **Conferência de Segredos de CI**:
   - Para cada comando `gh secret set NOME`, verificar se `secrets.NOME` é referenciado de fato nos arquivos em `.github/workflows/`.
   - Evitar criar segredos órfãos que a automação não consome.
3. **Idempotência de Execução**:
   - Rodar o wizard duas vezes seguidas deve resultar no mesmo estado final, sem duplicar linhas no `.env`.

---

## 5) Anti-Padrões

| Anti-Padrão | Descrição | Como Evitar |
|---|---|---|
| **Wizard Genérico sem Contexto** | Script que pergunta URLs e nomes de chaves sem pesquisar previamente os arquivos do projeto. | Inspecionar `.env.example` e workflows antes de criar o script; preencher padrões automaticamente. |
| **Eco de Segredos no Terminal** | Ler senhas com `read` comum, expondo tokens no histórico ou no scroll do terminal. | Usar compulsoriamente leitura silenciosa (`read -s`) para credenciais e chaves. |
| **Ações Irreversíveis sem Trava** | Disparar exclusões ou migrações destrutivas sem confirmação manual explícita. | Inserir função `confirm` com mensagem em vermelho e resumo das consequências antes da execução. |
| **Script Travando em CI Não-Interativo** | Tentar rodar o wizard dentro de um job de GitHub Actions onde não há TTY nem operador humano. | Isolar o wizard para uso local ou exigir flag não-interativa com valores pré-alimentados. |

---

## 6) Checklist Verificável de Wizard Interativo

- [ ] Todas as dependências externas e URLs foram mapeadas e testadas.
- [ ] O script utiliza `set -euo pipefail` e passa em `bash -n`.
- [ ] Entradas de senhas e tokens utilizam captura mascarada (`ask_secret`).
- [ ] A escrita em arquivos `.env` é estritamente idempotente.
- [ ] As variáveis de segredo batem exatamente com as referências dos workflows de CI.
- [ ] O script inclui permissão de execução (`chmod +x`).

---

## 7) Referências

- Pocock, Matt. *Wizard Skill Pattern*. `mattpocock/skills/tree/main/skills/engineering/wizard`
- GNU Bash Reference Manual.
- GitHub CLI Manual (`gh secret`, `gh variable`).
