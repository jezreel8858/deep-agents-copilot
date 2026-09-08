---
name: repository-hygiene-patterns
description: >-
  Diretrizes e matriz canônica para auditoria e garantia de higiene de
  repositório, documentação essencial (README, CONTRIBUTING, LICENSE),
  segurança de versionamento (.gitignore, prevenção de .env commitado) e
  práticas de engenharia CI/CD. Base de conhecimento do repo-hygiene-auditor.
tier: 2
category: process
triggers:
  - "higiene de repositório"
  - "repo hygiene"
  - "boas práticas de repositório"
  - "auditoria de documentação"
  - "checar readme"
  - "checar gitignore"
  - "verificar licença"
  - "contributing guide"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/repo-hygiene-auditor.agent.md
tools: []
---

# Repository Hygiene Patterns

## 1) Objetivo e Escopo

Esta skill estabelece os critérios e a matriz de maturidade para avaliação de higiene estrutural e boas práticas de engenharia em qualquer repositório de software, independente da stack tecnológica adotada (agnóstico).

## 2) Matriz de Maturidade de Higiene

| Nível | Dimensão | Critérios de Avaliação | Severidade de Ausência |
|---|---|---|---|
| **L1** | Documentação Essencial | `README.md` claro com instrução de setup, `LICENSE` válida, `CONTRIBUTING.md` básico | 🔴 Alta |
| **L2** | Higiene de Versionamento | `.gitignore` consistente, ausência de `.env` ou segredos rastreados no git | 🔴 Bloqueador |
| **L3** | Qualidade & Automação | Lockfile determinístico (`package-lock.json`, `poetry.lock`, etc.), pipeline de CI | 🟠 Média |
| **L4** | Consistência de Estilo | Configurações de linter/formatter (`.editorconfig`, eslint, prettier, black) | 🟡 Sugestão |

## 3) Itens Canônicos Auditados

1. **Documentação de Boas-Vindas e Operação**:
   - `README.md`: título, descrição, pré-requisitos, inicialização local e testes.
   - `CONTRIBUTING.md`: fluxo de branching, convenção de commit e abertura de PRs.
   - `LICENSE`: licença open-source ou proprietária declarada explicitamente.
   - `CHANGELOG.md`: histórico de alterações e versionamento semântico.

2. **Segurança de Versionamento e Sanitização**:
   - Presença de `.gitignore` cobrindo artefatos de build (`dist/`, `target/`, `node_modules/`, `__pycache__/`).
   - Verificação rigorosa contra commit acidental de arquivos de ambiente com credenciais (`.env`, `.env.local`, `.pem`, `.key`).

3. **Engenharia e Reprodutibilidade**:
   - Presença de lockfile correspondente ao gerenciador de pacotes.
   - Presença de workflows de automação (`.github/workflows/` ou equivalente).
   - Ausência de arquivos temporários, logs ou lixeiras no versionamento.

