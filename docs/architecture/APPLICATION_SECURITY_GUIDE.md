# Guia Canônico de Segurança de Aplicação e Gestão de Vulnerabilidades (AppSec Guide)

> **Referência Normativa:** [`CLAUDE.md`](../../CLAUDE.md) § R-002, R-031, R-046, R-048.1, R-050.  
> **Agente Guardião:** [`@security-reviewer`](../../.github/agents/security-reviewer.agent.md) | **Skill Base:** [`security-review-patterns`](../../.github/skills/security-review-patterns/SKILL.md).  
> **Padrões Globais:** OWASP Top 10:2025, OWASP ASVS 5.0, OWASP API Security Top 10, CWE Top 25, OWASP Agentic AI Security (2026).

---

## 1. Visão Geral e Princípios de DevSecOps

Em ecossistemas modernos de engenharia assistida por agentes de IA, a segurança de software deixa de ser uma auditoria tardia e isolada e se torna uma **propriedade intrínseca, contínua e determinística** do ciclo de vida de desenvolvimento (*Shift-Left Security*).

### 1.1 Princípios Fundamentais
1. **Shift-Left Real (Segurança no Design e no Commit)**: As vulnerabilidades devem ser detectadas e sanadas no momento da concepção da arquitetura (`tech-solution-architect`), na escrita do código pelos especialistas de domínio e na validação pré-merge (`security-reviewer`), onde o custo de correção é exponencialmente menor.
2. **Defesa em Profundidade (Layered AppSec)**: Nenhuma ferramenta de segurança isolada é suficiente. A segurança efetiva combina análise de código-fonte (SAST), análise de dependências e alcançabilidade (SCA + Reachability), testes de runtime e APIs (DAST), instrumentação dinâmica (IAST), varredura ativa de segredos (Secrets Detection) e gestão integrada de postura (ASPM).
3. **Redução Rigorosa de Falso-Positivo**: Alertas infundados geram fadiga de segurança (*alert fatigue*) e desvios desnecessários. Toda sinalização de vulnerabilidade exige validação do fluxo completo: **Input controlado por atacante + Sink alcançável + Impacto/Blast Radius real**.
4. **Zero Tolerância para Segredos Expostos**: Credenciais, chaves criptográficas e tokens de acesso nunca devem residir no código-fonte ou no histórico de versionamento.
5. **Autonomia de Remediação com Supervisão Humana**: Agentes de IA auxiliam na identificação, cálculo de blast radius e implementação de correções cirúrgicas de dependências (`WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION`), mantendo o checkpoint de aprovação humana antes de deploys críticos.

---

## 2. A Matriz Holística de Segurança de Aplicação (Os 6 Pilares de AppSec)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│              ASPM (Application Security Posture Management)                     │
│       Orquestração, Correlação de Risco, Deduplicação e Priorização             │
├───────────────────────┬─────────────────────────┬───────────────────────────────┤
│         SAST          │           SCA           │       SECRETS DETECTION       │
│ Análise Estática de   │ Dependências & Open     │ Varredura de Chaves, Tokens   │
│ Código Proprietário   │ Source + Reachability   │ e Entropia Pré-Commit         │
├───────────────────────┼─────────────────────────┼───────────────────────────────┤
│         DAST          │          IAST           │     CONTAINER & IaC SEC       │
│ Teste Dinâmico em     │ Instrumentação Intera-  │ Dockerfile, Imagens Base,     │
│ Runtime e Fuzzing API │ tiva durante Testes     │ Kubernetes e Terraform        │
└───────────────────────┴─────────────────────────┴───────────────────────────────┘
```

### 2.1 SAST (Static Application Security Testing)
- **O que é**: Análise estática profunda do código-fonte proprietário sem necessidade de executar a aplicação.
- **Como atua**: Examina a Árvore Sintática Abstrata (AST) e executa rastreamento de fluxo de dados (*Taint Analysis*), mapeando a trajetória desde as fontes de entrada não confiáveis (*sources*) até as operações críticas do sistema (*sinks*).
- **Vulnerabilidades Detectadas**: Injeções SQL, NoSQL e Command Injection; Cross-Site Scripting (XSS); Path Traversal; desserialização insegura de objetos; controle de acesso quebrado (IDOR); e uso de funções criptográficas obsoletas (MD5, SHA1 puro, DES).
- **Ferramentas de Referência**: Semgrep, SonarQube (Quality Profile de Segurança), CodeQL, Bandit (Python), ESLint Security Plugin (TypeScript/JavaScript).

### 2.2 SCA (Software Composition Analysis) & Reachability Analysis
- **O que é**: Varredura automatizada de manifestos de dependências (`package.json`, `pom.xml`, `pyproject.toml`, `go.mod`) contra bases de dados globais de vulnerabilidades conhecidas (CVEs, NVD, GitHub Advisory Database, OSV).
- **Avanço de Mercado (Reachability Analysis 2025/2026)**: Ferramentas modernas de SCA não apenas alertam sobre a presença de uma biblioteca vulnerável na árvore de dependências transitivas, mas realizam **análise de alcançabilidade no grafo de chamadas**. Se a função ou classe específica afetada pela CVE nunca é invocada pelo código da aplicação, a severidade é contextualizada, reduzindo drasticamente o ruído e priorizando o que é explorável em produção.
- **Ferramentas de Referência**: Snyk, Trivy (filesystem scan), OWASP Dependency-Check, Dependabot, npm audit, pip-audit.

### 2.3 DAST (Dynamic Application Security Testing)
- **O que é**: Teste de segurança de caixa preta executado contra a aplicação em funcionamento (geralmente em ambiente de staging ou contêiner de integração contínua).
- **Como atua**: Simula ataques externos reais através de sondagens HTTP, fuzzing de parâmetros de API, injeção de payloads maliciosos e análise das respostas recebidas.
- **Vulnerabilidades Detectadas**: Configurações incorretas de CORS (`Access-Control-Allow-Origin: *`), ausência de headers de segurança (HSTS, CSP, X-Frame-Options), vazamento de stack traces em respostas de erro HTTP 500, vulnerabilidades em fluxos de autenticação/sessão e cookies desprovidos das flags `HttpOnly`, `Secure` e `SameSite`.
- **Ferramentas de Referência**: OWASP ZAP (ZAP CLI em pipeline), Burp Suite Enterprise / DAST, StackHawk (especializado em REST/GraphQL).

### 2.4 IAST (Interactive Application Security Testing)
- **O que é**: Segurança interativa baseada em instrumentação de agentes inseridos diretamente no runtime da aplicação (ex.: Java Agent na JVM, middleware no Node.js/Python) durante a execução da suíte de testes funcionais e de integração.
- **Vantagem**: Une a precisão do SAST (aponta exatamente o arquivo e a linha do sink vulnerável) com a certeza do DAST (comprova que o código de fato executou com dados reais), operando com taxas próximas a zero de falsos-positivos.
- **Ferramentas de Referência**: Contrast Security, Invicti Shark, Synopsys Seeker.

### 2.5 Secrets Detection (Detecção de Segredos & Análise de Entropia)
- **O que é**: Varredura contínua de diffs, commits, branches e arquivos de configuração para impedir que credenciais e dados sensíveis sejam expostos.
- **Como atua**: Combina regras baseadas em expressões regulares com padrões estruturados de provedores (ex.: `ghp_`, `AKIA`, `sk-proj-`, strings de conexão JDBC/Postgres) e algoritmos de cálculo de entropia de Shannon para detectar senhas e chaves criptográficas geradas aleatoriamente.
- **Regra de Ouro**: A remoção de um segredo em um novo commit **não anula a vulnerabilidade**, pois o histórico do Git preserva o valor. Todo segredo vazado exige **revogação e rotação imediata** na infraestrutura.
- **Ferramentas de Referência**: Gitleaks (em pre-commit e CI), TruffleHog, detect-secrets.

### 2.6 ASPM (Application Security Posture Management)
- **O que é**: Camada superior de orquestração, agregação e governança que centraliza e correlaciona os achados provenientes de todas as ferramentas de AppSec (SAST, SCA, DAST, Secrets, Containers).
- **Como atua**: Elimina duplicatas de alertas (ex.: o mesmo endpoint apontado pelo DAST, pelo SAST e por uma CVE de SCA), cruza os achados com o contexto do repositório e o status de exposição à internet, e gera uma fila de remediação unificada ranqueada por risco real de negócio.
- **Ferramentas de Referência**: Cycode, Checkmarx One, Veracode Risk Manager, OX Security.

### 2.7 Container & Infrastructure-as-Code (IaC) Security
- **O que é**: Análise de conformidade e vulnerabilidades em arquivos de empacotamento Dockerfile, imagens de contêiner e manifests de infraestrutura declarativa (Kubernetes manifests, Terraform, Helm charts).
- **Práticas Obrigatórias**:
  - Imagens base mínimas e oficiais (Alpine, Distroless).
  - Execução compulsória sob usuário não-root (`USER nonroot:nonroot`).
  - Multi-stage builds para isolar ferramentas de compilação da imagem final de produção.
  - Varredura de IaC contra privilégios excessivos (ex.: containers rodando em `privileged: true` ou montando `/var/run/docker.sock`).
- **Ferramentas de Referência**: Trivy (container image scan), Hadolint (linter de Dockerfile), Checkov (IaC security).

---

## 3. Padrões e Normas Internacionais Aplicadas

O ecossistema implementa controles alinhados aos principais frameworks internacionais de segurança:

### 3.1 OWASP Top 10:2025 (Aplicações Web)
1. **A01: Broken Access Control (Controle de Acesso Quebrado)**: Verificação de autorização em nível de registro (prevenção de IDOR), princípio do privilégio mínimo e bloqueio de bypass de permissão por URL.
2. **A02: Cryptographic Failures (Falhas Criptográficas)**: Criptografia de dados sensíveis em repouso e em trânsito (TLS 1.3 obrigatório), armazenamento de senhas com algoritmos de hashing com sal e custo calibrado (Argon2id ou bcrypt com fator de trabalho ≥ 12).
3. **A03: Injection (Injeções)**: Parametrização compulsória de consultas SQL/NoSQL (ORM seguro ou Prepared Statements); sanitização estrita de comandos de sistema operacional.
4. **A04: Insecure Design (Design Inseguro)**: Modelagem de ameaças prévia, validação fail-fast em bordas de API e limites estruturais de consumo de recursos (Rate Limiting).
5. **A05: Security Misconfiguration (Configuração Insegura)**: Desativação de páginas de erro com stack trace em produção, headers de segurança configurados e remoção de endpoints e contas default.
6. **A06: Vulnerable and Outdated Components (Componentes Desatualizados/Vulneráveis)**: Monitoramento contínuo de CVEs via SCA e execução prioritária de atualizações de dependências (`WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION`).
7. **A07: Identification and Authentication Failures (Falhas de Identificação e Autenticação)**: Bloqueio contra força bruta, expiração segura de tokens JWT/sessões e obrigatoriedade de MFA em fluxos privilegiados.
8. **A08: Software and Data Integrity Failures (Falhas de Integridade de Software e Dados)**: Validação de assinaturas em pacotes/plugins, prevenção de desserialização arbitrária e pipelines de CI/CD protegidos.
9. **A09: Security Logging and Monitoring Failures (Falhas de Logging e Monitoramento)**: Registro estruturado de eventos de segurança (falhas de login, acessos negados, modificações de perfil) sem expor PII ou segredos nos logs.
10. **A10: Server-Side Request Forgery - SSRF (Falsificação de Requisição do Servidor)**: Validação estrita de URLs fornecidas pelo usuário, restrição de portas e bloqueio de chamadas a endereços internos (`localhost`, `127.0.0.1`, `169.254.169.254`).

### 3.2 OWASP Agentic AI Security (2026.1 / ASI01..ASI10)
Diretrizes aplicáveis diretamente aos agentes de inteligência artificial que atuam no repositório:
- **ASI01 (Agent Goal Hijacking)**: Proteção contra injeções de prompt indiretas através de dados inspecionados no código.
- **ASI02 (Tool Misuse)**: Confinamento rigoroso das ferramentas invocadas por cada agente. Routers possuem estritamente o baseline de 7 ferramentas de leitura (R-054); agentes analíticos são proibidos de possuir ferramentas mutativas.
- **ASI03 (Over-Privileged Agents)**: Os agentes de IA não possuem permissões autônomas de `git commit` ou `git push` (R-031); a aplicação de alterações é entregue ao engenheiro humano para validação.
- **ASI05 (Insecure Inter-Agent Communication)**: Todo handoff entre agentes segue contratos tipados com validação de payload em `workflow_tracking` (R-050).

---

## 4. Classificação de Severidade (CVSS) e SLAs de Remediação

O projeto adota a taxonomia do Common Vulnerability Scoring System (CVSS v3.1 / v4.0) com as seguintes diretrizes de priorização:

| Nível de Severidade | Range CVSS | Critério de Bloqueio | SLA de Remediação | Exemplos Típicos |
|---|:---:|---|:---:|---|
| **🔴 Crítico** | 9.0 – 10.0 | **Bloqueio Total de Merge e Release.** Nenhum código avança para homologação ou produção. | **≤ 24 horas** | RCE remoto não autenticado, SQL Injection direta, segredo corporativo exposto no Git, CVE crítica com exploit público ativo. |
| **🟠 Alto** | 7.0 – 8.9 | **Bloqueio de Release.** Exige plano de correção ou mitigação documentada para merge em develop. | **≤ 7 dias** | IDOR em dados sensíveis, XSS persistente, bypass de autenticação, dependência de produção com CVSS ≥ 7.0 sem exploit imediato. |
| **🟡 Médio** | 4.0 – 6.9 | Alerta de conformidade. Não bloqueia hotfix emergencial, mas exige registro em backlog e correção na sprint. | **≤ 30 dias** | Ausência de headers de segurança, CORS permissivo em ambiente de desenvolvimento, CVE média em dependência transitiva. |
| **🔵 Baixo / Informativo** | 0.1 – 3.9 | Recomendação de boas práticas e endurecimento de código (*hardening*). | **≤ 90 dias** | Vazamento de versão de servidor em cabeçalhos, ausência de rate limiting em rota pública informativa, comentários com TODOs antigos. |

---

## 5. Integração com os Workflows Canônicos do Repositório

A segurança é operacionalizada de forma determinística dentro dos Workflows Canônicos (R-050):

### 5.1 No `WORKFLOW-FEATURE-DEVELOPMENT` (Estado 6a — Security Review)
- Todo novo endpoint, fluxo ou modelo de dados passa compulsoriamente pelo **Gate 1 de Segurança** liderado pelo `@security-reviewer`.
- O revisor aplica a **Rubrica de Triagem em 3 Etapas** (Input controlado? Sink alcançável? Blast radius real?). Se vulnerabilidades de nível Alto ou Crítico forem detectadas, o workflow aciona o loop de remediação (máximo 2 tentativas) antes de liberar para o Quality Gate de PR.

### 5.2 No `WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION` (Workflow 6)
- Despachado imediatamente quando um alerta SCA (Snyk/Trivy/Dependabot) reporta CVE em biblioteca.
- A sequência canônica executa: *(1)* Triagem pelo `@security-reviewer`; *(2)* Mapeamento de blast radius pelo `@code-knowledge-graph` (R-045); *(3)* Bump cirúrgico de versão do manifesto no sandbox pelo especialista; *(4)* Adaptação de eventuais breaking changes com suite de testes; e *(5)* Validação final com nova varredura limpa.

### 5.3 No `WORKFLOW-RELEASE-READINESS` (Workflow 8 — Estado 3)
- Antes de qualquer tag ou release, o `@security-reviewer` em conjunto com o `@repo-hygiene-auditor` executa a **Varredura Final de Segredos e Higiene**.
- Verifica ausência de arquivos `.env` commitados, ausência de tokens de alta entropia nos diffs e conformidade de licenças de pacotes terceiros.

---

## 6. Checklist de Implementação Segura por Domínio de Código

Ao implementar ou revisar código, todo especialista deve validar as seguintes diretrizes:

### 6.1 Autenticação e Gestão de Sessão
- [ ] Senhas armazenadas exclusivamente com hashes lentos adaptativos (Argon2id ou bcrypt com fator de trabalho ≥ 12), nunca MD5, SHA1 ou SHA256 puro.
- [ ] Tokens JWT assinados com algoritmos assimétricos fortes (RS256, EdDSA) ou HMAC com chave secreta de alta entropia (mínimo 256 bits).
- [ ] Tokens JWT validam compulsoriamente os campos de expiração (`exp`), emissor (`iss`) e audiência (`aud`), rejeitando tokens com algoritmo `"none"`.
- [ ] Sessões invalidadas formalmente no servidor durante o logout.
- [ ] Cookies de sessão e autenticação configurados com `HttpOnly`, `Secure` e `SameSite=Strict` ou `Lax`.

### 6.2 Autorização e Controle de Acesso
- [ ] Toda rota de API valida explicitamente o papel ou escopo do usuário autenticado.
- [ ] Consultas a entidades e registros utilizam compulsoriamente o identificador do usuário autenticado no filtro da query (`WHERE usuario_id = :usuarioIdLogado`), prevenindo acesso direto a objetos de terceiros (IDOR).
- [ ] Bloqueio fail-safe por padrão: acessos não autorizados explicitamente devem ser negados (*Deny by Default*).

### 6.3 Tratamento de Entradas e Prevenção de Injeção
- [ ] 100% das consultas SQL utilizam parametrização nativa (*bind parameters* / Prepared Statements). Proibição absoluta de concatenação de strings em queries.
- [ ] Dados renderizados em templates HTML são devidamente escapados pelo motor do framework (prevenção de XSS).
- [ ] Uploads de arquivos validam tipo de conteúdo real (magic bytes), limitam tamanho máximo e armazenam arquivos fora da raiz pública de execução do servidor com nomes aleatórios (`uuidv4`).
- [ ] Caminhos de arquivo fornecidos pelo usuário são estritamente sanitizados e resolvidos contra um diretório base permitido para prevenir Path Traversal.

### 6.4 Criptografia e Proteção de Dados Sensíveis
- [ ] Comunicação de rede utiliza TLS 1.3 (ou TLS 1.2 como fallback estrito). Proibido aceitar cifras antigas ou TLS 1.0/1.1.
- [ ] Dados regulados (CPF, cartão de crédito, dados de saúde) são mascarados antes de qualquer emissão de log (`***.***.***-**`).
- [ ] Geração de números aleatórios de segurança (tokens, salts, nonces) utiliza geradores criptograficamente seguros (`crypto.getRandomValues`, `SecureRandom`).

