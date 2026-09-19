---
name: security-review-patterns
description: >
  Diretrizes consolidadas de segurança aplicada para revisão especializada de código —
  OWASP Top 10:2025, ASVS 5.0, OWASP Top 10 para LLM Apps (2025) e OWASP Agentic
  AI Security (2026). Cobre SAST, SCA (dependências/CVE), detecção de secrets,
  triagem de falso-positivo e checklists por domínio (auth, input, crypto).
tier: 2
category: security
triggers:
  - "revisão de segurança"
  - "security review"
  - "owasp"
  - "cve"
  - "vulnerabilidade"
  - "sql injection"
  - "xss"
  - "csrf"
  - "secrets no código"
  - "dependência vulnerável"
  - "sast"
  - "sca"
  - "asvs"
  - "auditoria de segurança"
source_docs:
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
  - ".github/skills/code-review-patterns/SKILL.md"
  - ".github/skills/sonarqube-governance/SKILL.md"
tools: []
---

# Security Review Patterns

> Base de conhecimento para agents que fazem **revisão especializada de segurança de código de aplicação** (não confundir com `agent-safety-guardrails`, que cobre segurança do **próprio agent de IA** — prompt injection, blast radius de tools).

## Quando Usar

- Antes de aprovar merge de código que lida com autenticação, autorização, input externo, criptografia ou dados sensíveis.
- Ao revisar dependências novas/atualizadas (SCA — Software Composition Analysis).
- Ao investigar relato de vulnerabilidade ou CVE em dependência do projeto.
- Ao desenhar endpoint de API que recebe input externo.

## 1) Standards e Pilares AppSec Consolidados (2025-2026)

### 1.1 Normas e Padrões Globais
| Standard | Versão | Foco |
|---|---|---|
| **OWASP Top 10** | 2025 | Vulnerabilidades web — 3 categorias renomeadas vs. 2021, não usar IDs antigos |
| **OWASP ASVS** | 5.0.0 | Requisitos de verificação de segurança (Level 1/2/3), estrutura renumerada vs. 4.0 |
| **OWASP API Security Top 10** | 2024/2025 | Segurança de APIs modernas (BOLA, Broken Authentication, Mass Assignment) |
| **CWE Top 25** | Mais recente | Fraquezas de software mais perigosas e recorrentes no mercado |
| **OWASP Top 10 for LLM Apps** | 2025 | Riscos LLM01-LLM10 para chatbots, RAG, tool-calling apps |
| **OWASP Agentic AI Security** | 2026.1 (dez/2025) | Riscos ASI01-ASI10 para sistemas de agents autônomos — **escopo do agent de IA em si**, não da aplicação revisada |

### 1.2 A Matriz Canônica de Segurança de Aplicação (AppSec Stack)
O ecossistema implementa a cobertura em profundidade através de 6 pilares complementares (detalhes em [`docs/architecture/APPLICATION_SECURITY_GUIDE.md`](../../docs/architecture/APPLICATION_SECURITY_GUIDE.md)):
1. **SAST (Static Application Security Testing)**: Varredura de código-fonte proprietário (Shift-Left) via AST e *Taint Analysis* (Semgrep, SonarQube, CodeQL).
2. **SCA (Software Composition Analysis) + Reachability**: Análise de dependências com verificação de alcançabilidade no grafo de chamadas (Trivy, Snyk, pip-audit, npm audit).
3. **DAST (Dynamic Application Security Testing)**: Testes de caixa preta em runtime contra APIs e endpoints (OWASP ZAP, StackHawk).
4. **IAST (Interactive Application Security Testing)**: Instrumentação de runtime durante execução de testes com zero falso-positivo.
5. **Secrets Detection**: Varredura pré-commit e pós-merge com análise de entropia e prefixos conhecidos (Gitleaks, TruffleHog).
6. **ASPM (Application Security Posture Management)**: Camada de correlação e orquestração de risco consolidada.

## 2) Taxonomia de Achados de Segurança

| Categoria | Exemplos | Severidade típica |
|---|---|---|
| **Injeção** | SQL Injection, Command Injection, LDAP Injection | 🔴 Bloqueador |
| **Quebra de Autenticação** | Sessão sem expiração, senha em texto claro, bypass de MFA | 🔴 Bloqueador |
| **Exposição de Dados Sensíveis** | PII/CPF/cartão sem mascaramento em log, secret hardcoded | 🔴 Bloqueador |
| **Controle de Acesso Quebrado** | IDOR, falta de verificação de ownership de recurso | 🔴 Bloqueador |
| **Configuração Insegura** | CORS `*`, debug mode em produção, headers de segurança ausentes | 🟠 Alta |
| **XSS / CSRF** | Output não sanitizado, falta de CSRF token | 🔴 Bloqueador (se explorável) |
| **Componentes Vulneráveis** | Dependência com CVE conhecido (crítico/alto) | 🟠 Alta a 🔴 Bloqueador (por CVSS) |
| **Criptografia Fraca** | MD5/SHA1 para senha, chave hardcoded, TLS desabilitado | 🔴 Bloqueador |
| **Logging Insuficiente** | Ausência de log de eventos de segurança (login, permissão negada) | 🟡 Sugestão |

## 3) Rubrica de Triagem (reduz falso-positivo)

Antes de reportar um achado como vulnerabilidade, confirmar 3 critérios:

1. **Input controlado por atacante**: a entrada realmente vem de fora do trust boundary (usuário, API externa, arquivo upload)?
2. **Sink alcançável**: o dado flui até uma operação sensível (query SQL, exec, render HTML, chamada de API)?
3. **Blast radius real**: qual o impacto se explorado — leitura de dado, escrita, RCE, DoS?

Sem os 3 critérios confirmados → rebaixar para 🟡 sugestão ou não reportar.

## 4) SCA — Análise de Dependências & Reachability Analysis (CVE Scanning)

| Ferramenta | Uso |
|---|---|
| **Trivy** | Scan de imagem de container + filesystem + IaC |
| **Snyk** | Scan de dependências (npm, Maven, pip) + containers |
| **OWASP Dependency-Check** | Scan de dependências Java/Node open-source |
| **npm audit / pip-audit** | Scan nativo de linguagem, baixo custo |

### 4.1 Protocolo de Reachability Analysis (Redução de Ruído)
Ao analisar uma CVE reportada em dependência transitiva:
1. **Alcançabilidade no Grafo de Chamadas**: A classe ou método vulnerável da biblioteca de fato é invocado pelo código da aplicação (verificável via `@code-knowledge-graph` / callee trace)?
2. **Critério de Severidade Efetiva**:
   - CVE com CVSS ≥ 7.0 (Alto/Crítico) **e alcançável pelo código da aplicação** → 🔴 **Bloqueador Imediato**.
   - CVE com CVSS ≥ 7.0 **mas comprovadamente inalcançável (dead code/unreachable path)** → 🟠 **Alta Prioridade** (remediação programada, sem travamento de hotfix emergencial).
   - CVE 4.0–6.9 → 🟡 **Média Prioridade** (correção na sprint ou no próximo ciclo do `WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION`).

## 5) Detecção de Secrets

- Nunca aprovar merge com: API key, token, senha, connection string hardcoded no diff.
- Padrões de detecção: regex de alta entropia, prefixos conhecidos (`sk-`, `ghp_`, `AKIA`), arquivos `.env` commitados.
- Ferramentas: `git-secrets`, `gitleaks`, `trufflehog`.
- Ação ao detectar: 🔴 Bloqueador + recomendar rotação imediata da credencial exposta (não apenas remoção do commit — histórico do git preserva).

## 6) Checklist por Domínio

### Autenticação/Autorização
- [ ] Senhas com hash Argon2/bcrypt (nunca MD5/SHA1 puro).
- [ ] Sessão com expiração e invalidação no logout.
- [ ] MFA disponível para operações sensíveis.
- [ ] Verificação de ownership antes de retornar/alterar recurso (anti-IDOR).

### Input Handling
- [ ] Toda entrada externa validada (allowlist > denylist).
- [ ] Queries parametrizadas (nunca concatenação de SQL).
- [ ] Output sanitizado antes de renderizar em HTML (anti-XSS).
- [ ] Upload de arquivo com validação de tipo/tamanho/nome.

### Criptografia
- [ ] TLS 1.2+ obrigatório em trânsito.
- [ ] Dados sensíveis (PII) criptografados em repouso.
- [ ] Chaves de criptografia nunca hardcoded — usar secret manager.

### API Design
- [ ] Rate limiting em endpoints públicos.
- [ ] CORS restrito a origens conhecidas (nunca `*` em produção).
- [ ] Headers de segurança (`Content-Security-Policy`, `X-Frame-Options`).

## 7) Anti-Padrões

- ❌ Reportar "possível vulnerabilidade" sem confirmar os 3 critérios da rubrica (§3).
- ❌ Bloquear por CVE em dependência **não usada em produção** (ex.: devDependency de teste) sem análise de exploitability.
- ❌ Ignorar contexto — mesmo padrão pode ser seguro em código interno vs. exposto publicamente.
- ❌ Sugerir "usar criptografia" sem especificar algoritmo/padrão concreto.
- ❌ Confundir segurança de aplicação (este skill) com segurança do próprio agent de IA (`agent-safety-guardrails`).

## Checklist de Saída

- [ ] Cada achado classificado por categoria (§2) e severidade.
- [ ] Rubrica de triagem aplicada antes de reportar (§3).
- [ ] CVEs citados com CVSS score quando aplicável.
- [ ] Nenhuma credencial real reproduzida no relatório — apenas indicação de localização.
- [ ] Recomendação de remediação concreta por achado (não apenas "corrigir").

## Referências

- OWASP Top 10:2025 — https://owasp.org/Top10/2025
- OWASP ASVS 5.0 — https://github.com/OWASP/ASVS
- OWASP Top 10 for LLM Applications (2025) — https://genai.owasp.org
- OWASP Agentic AI Security Initiative (2026.1) — https://genai.owasp.org/initiative/agentic-security-initiative
- Checkmarx — Secure Coding Practices 2026: real-time IDE scanning, SAST+SCA+secrets unificados.

