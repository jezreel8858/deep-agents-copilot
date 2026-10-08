# Guardrail de Segredos — Defesa em Camadas (Nível 3 — git-governance)

> Complementa R-010 / R-044. Esta é a **camada 3** (agente); não substitui as camadas 1 e 2.

## 1) Camadas

| Camada | Onde | Ferramentas típicas | Função |
|---|---|---|---|
| 1. Pre-commit | Máquina do dev | `gitleaks protect --staged`, `detect-secrets`, `pre-commit` | Bloqueia antes do commit |
| 2. CI | Pipeline/PR | `gitleaks detect`, GitHub Secret Scanning + Push Protection, `trufflehog` | Rede de segurança no servidor |
| 3. Agent | `/commit`, `@pr-gatekeeper` | Varredura regex do diff (via `ctx_execute`) | Bloqueio antes de gerar mensagem/PR |

## 2) Catálogo de Padrões (camada 3)

| Alvo | Regex |
|---|---|
| AWS Access Key | `AKIA[0-9A-Z]{16}` |
| OpenAI/Stripe-like | `sk-[A-Za-z0-9]{20,}` |
| GitHub token | `gh[pousr]_[A-Za-z0-9]{36,}` / `github_pat_[A-Za-z0-9_]{22,}` |
| GitLab PAT | `glpat-[A-Za-z0-9_\-]{20,}` |
| Slack | `xox[baprs]-[A-Za-z0-9-]{10,}` |
| Chave privada | `-----BEGIN [A-Z ]*PRIVATE KEY-----` |
| Atribuição literal | `(?i)(password\|passwd\|secret\|token\|apikey)\s*[=:]\s*["\']?[^\s"\'$\{]{6,}` |
| URL com credencial | `://[^/\s:@]+:[^/\s@]+@` / `https://[A-Za-z0-9_\-]{20,}@` |
| Caminho local absoluto | `[A-Za-z]:\\Users\\\|/home/[a-z]+/` (R-044) |

## 3) Falsos Positivos

Ignorar quando o valor for: variável de ambiente (`${VAR}`, `process.env.X`, `os.getenv`), placeholder (`<token>`, `changeme`, `xxxx`, `example`), fixture claramente fictícia em `tests/` ou documentação com padrão truncado. Em dúvida, reportar como "suspeito" e pedir confirmação — nunca silenciar.

## 3.1) Exclusões da Varredura

`*.lock`, `*.min.js`, binários e snapshots geradas.

## 4) Decisão

- **Achado confirmado**: PARAR; reportar `arquivo:linha` (sem ecoar o valor); instruir remoção + **rotação** da credencial + limpeza de histórico se já commitada. Não gerar commit/PR.
- **Limpo**: prosseguir e declarar "camada 3 executada".
