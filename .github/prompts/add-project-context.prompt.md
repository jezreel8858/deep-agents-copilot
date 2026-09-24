---
name: add-project-context
description: 
  DESCOBERTA DE PROJETO — Execute DEPOIS de `/init-context`.
  Orquestra descoberta estruturada de projeto com Intent Classification + Multi-Query RRF.
  Análise estática offline → geração automática de YAML/Markdown → validação e binding atômico.
  Execute UMA VEZ POR PROJETO (reutilizável). PRÉ-REQUISITO `/init-context` já executado.
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['file_search', 'grep_search', 'read_file', 'run_in_terminal', 'run_subagent', 'ask_questions', 'context-mode/ctx_search']
argument-hint: '<caminho-absoluto-do-projeto>'
source_docs:
  - .github/skills/yaml-governance/SKILL.md
  - .github/skills/context-mode/SKILL.md
  - .github/skills/terminal-governance/SKILL.md
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/projects.local.yaml.example
---

# `/add-project-context`

**PRÉ-REQUISITO: Execute `/init-context` PRIMEIRO (uma única vez na sessão).**

Auto-carregar contexto estruturado de um projeto com Intent Classification + Multi-Query RRF.

> **Propósito**: Plugar projeto externo ao contexto de governança — scanner + geração de artefatos de binding local.
> **Workspace**: `${workspaceFolder}`
> **Projeto Alvo**: `${input:caminhoDoProjeto}`
>
> **FREQUÊNCIA**: ✅ N VEZES (1x por projeto)
>
> **ORDEM**: DEPOIS de `/init-context` (que é 1x apenas)
>
> **REUTILIZÁVEL**: Sim — execute para cada projeto novo na mesma sessão
>
> **⛔ GUARDRAIL**: Todos os artefatos gerados ficam NESTE repositório de governança.
>                  Nenhum arquivo é criado ou modificado nos projetos externos.
>                  Projeto/adapter são LOCAIS (gitignored, R-043) — nunca commitados.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** analisar o projeto externo indicado em modo read-only e gerar o adapter local em `.github/instructions/local/`.
- ✅ **SEMPRE** atualizar o overlay local `projects.local.yaml` (gitignored, R-043) — **nunca** `catalog.yaml`.
- ❌ **NÃO** modificar nenhum arquivo dentro do projeto externo escaneado.
- ❌ **NÃO** commitar caminhos de arquivos locais ou segredos no repositório de governança (R-044).

---
>
> **Se você é o Copilot**: Execute as FASES 1 → 2 → 3 → 4 → 4.1 sequencialmente conforme descrito abaixo. **FASE 4 (grafo de conhecimento) é OBRIGATÓRIA** — nunca opcional, nunca pulada. FASE 4.1 (integrações multi-projeto) executa automaticamente quando houver >1 projeto registrado.

---

## ⛔ Confinamento Absoluto ao Repositório de Governança + Desacoplamento Local (R-043)

```
┌──────────────────────────────────────────────────────────────┐
│  Este comando registra projetos externos COMO REFERÊNCIA.    │
│  Todos os artefatos criados ficam NESTE repositório.         │
│  Projeto/adapter gerados são LOCAIS — NUNCA commitados.       │
│                                                              │
│  ✅ CRIA/ATUALIZA: ./.github/projects.local.yaml      │
│                    (gitignored — NUNCA .github/instructions/README.md) │
│  ✅ CRIA EM: ./.github/instructions/local/<projeto>.instructions.md  │
│              (gitignored — NUNCA raiz ./.github/instructions/)      │
│                                                              │
│  ❌ NUNCA cria nada no projeto externo                       │
│  ❌ NUNCA modifica [nome-projeto-externo-1]/                 │
│  ❌ NUNCA modifica [nome-projeto-externo-2]/                 │
│  ❌ NUNCA escreve entrada de projeto em catalog.yaml (compartilhado) │
└──────────────────────────────────────────────────────────────┘
```

> **Por quê (R-043)**: `catalog.yaml` e `.github/instructions/*.instructions.md` (raiz) são commitados e
> compartilhados. Se projetos locais fossem gravados ali, um `git commit`/`git push` de rotina poderia
> subir acidentalmente nomes/caminhos de projetos privados para o repositório de governança compartilhado.
> A solução: overlay local — `projects.local.yaml` + `.github/instructions/local/` — ambos gitignored,
> nunca tocados por `git add`. Leitura sempre faz merge em memória (`catalog.yaml` + `projects.local.yaml`);
> escrita NUNCA toca o arquivo/pasta compartilhado.

---

## 🏥 Health Check — Binding Context (R-034) + Overlay Local (R-043)

**ANTES de iniciar**, o Copilot VERIFICA **neste repositório de governança**:

```
✓ Existe: ./.github/instructions/README.md?
✓ Existe: ./.github/instructions/README.md?
✓ Existe: ./.github/projects.local.yaml?  (overlay local, gitignored — R-043)
```

**Se `catalog.yaml` ou `binding.md` FALTAREM**:
```
⚠️ Binding context não detectado!

Este repositório de governança não possui .github/instructions/README.md ou .github/projects.local.yaml.example.
→ Interromper `/add-project-context`
→ Disparar agent `binding-initializer` para criá-los NESTE repositório
```

**Se `projects.local.yaml` FALTAR** (primeira vez nesta máquina/clone):
```
ℹ️ Overlay local não encontrado — criando a partir do template.
→ cp .github/projects.local.yaml.example .github/projects.local.yaml
→ Prosseguindo normalmente (este arquivo é gitignored — nunca será commitado)
```

**Se todos existem (ou o overlay acabou de ser criado)**: Prosseguir para FASE 1 normalmente.

---

## 🎯 Uso

```
/add-project-context <caminho-absoluto-do-projeto>
```

### Exemplos

```
/add-project-context D:\workspace\meu-projeto-backend
/add-project-context D:\workspace\meu-projeto-frontend
/add-project-context D:\workspace\meu-novo-projeto
```

---

## 📋 Fluxo Automático — 5 Fases (3 de binding + 1 de grafo + 1 de fronteiras multi-projeto)

### FASE 1: **Scanner via Agent Especializado** (Determinístico, Offline, Read-Only)

**Objetivo**: Detectar stack real do projeto delegando ao agent especializado `adapter-generator`.

Invocar:
```
run_subagent(
  agentName: "adapter-generator",
  description: "Scan read-only de projeto ainda não registrado",
  task: "modo=scan, path_externo=<caminho-absoluto-do-projeto>. Retornar apenas project_profile
         consolidado (YAML) — NÃO criar/modificar nenhum arquivo (nem no projeto externo, nem
         neste repositório). Ver adapter-generator.agent.md § Modos de Operação."
)
```

> Checklist completo do que o scanner detecta (linguagem, framework, estrutura, codestyle, testes,
> integração) vive em `adapter-generator.agent.md` § 🔍 Scanner de Projeto — **não duplicar aqui**
> (R-003). O `adapter-generator` retorna o `project_profile` consolidado para uso nas FASES 2/3.

**Output Fase 1**: `project_profile` consolidado (YAML), recebido do agent — sem nenhum arquivo criado/modificado.

### FASE 2: **Adaptação e Geração de Artefatos** (LLM — Copilot)

O Copilot:

#### 2.1 Validar Input
- Usar o argumento do comando como fonte primária (obrigatório): **`<caminho-absoluto-do-projeto>`**
- Se o argumento estiver ausente, solicitar via `ask_questions` um caminho **absoluto**
- Validar existência do caminho no workspace antes do scanner

#### 2.2 Apresentar Descobertas (a partir do `project_profile` retornado pela FASE 1)

Não reexecutar o scanner — usar diretamente o `project_profile` já obtido via `run_subagent(agentName: "adapter-generator", modo=scan)` na FASE 1:
- **Stack detectado**: (ex: `Java 17 + Spring Boot 3 + Hibernate`)
- **Frameworks**: (ex: `Angular 21 + RxJS`)
- **Arquitetura**: (ex: `component-based`)
- **Testing**: (ex: `Jasmine/Karma + Playwright`)

#### 2.3 Fazer 3 Perguntas via `ask_questions` (R-027 — Obrigatório)

```
[Q1] Nome do projeto?
  - Sugerido automaticamente a partir do último segmento do path
    (ex: path D:\workspace\meu-projeto-backend → sugere "meu-projeto-backend")
  - Validar: kebab-case, não existe ainda em catalog.yaml
  - Exemplos: meu-projeto-backend, meu-frontend-app, meu-backend-api

[Q2] Descrição (1-2 linhas)?
  - Descreva o propósito do projeto em 1 frase
  - Exemplos:
      "Serviço de [domínio] — Java/Spring Boot"
      "Frontend de [funcionalidade] — Angular 21"
  - Livre, sem validação de formato

[Q3] Qual adapter herdar ou criar novo?
  - Listar adapters existentes em `.github/instructions/` com seus detected_stack
  - Adicionar opção: "Criar novo adapter (scanner gerará automaticamente)"
  - Sugestão automática baseada no stack detectado na FASE 1
    (ex: stack Angular → sugerir `angular-v21-frontend.instructions.md` se existir)
```

> Tipo do projeto (backend/frontend/etc) é inferido pelo scanner da FASE 1 — não é perguntado.

#### 2.4 Gerar Artefatos (NESTE repositório de governança — LOCAIS, gitignored, R-043)

- **novo_projeto.yaml** (entry para `projects.local.yaml` — NUNCA `catalog.yaml`, escrito pelo próprio prompt na FASE 3, não pelo agent):
  ```yaml
  artefato: "projeto"
  nome: "<Q1>"
  tipo: "<inferido-pelo-scanner>"   # auto-inferido — não perguntado
  path_externo: "<caminho-absoluto-do-projeto-externo>"  # para scanner (read-only)
  extends: ["<adapter-sugerido-Q3>"]
  descrição: "<Q2>"
  adapter_local: ".github/instructions/local/<Q1>.instructions.md"
  ```

- **`<nome>.instructions.md`** em `./.github/instructions/local/` (SOMENTE se Q3 = "Criar novo adapter") — **delegado ao `adapter-generator`**, nunca gerado inline pelo Copilot:
  ```
  run_subagent(
    agentName: "adapter-generator",
    description: "Gerar adapter para novo projeto <Q1>",
    task: "modo=generate-one, nome=<Q1>, path_externo=<caminho-absoluto-do-projeto-externo>,
           stack_detectado=<project_profile da FASE 1>. Criar SOMENTE o arquivo
           .github/instructions/local/<Q1>.instructions.md — não tocar projects.local.yaml
           (isso é responsabilidade deste prompt, na FASE 3)."
  )
  ```

> ⚠️  O adapter é criado em `./.github/instructions/local/<nome>.instructions.md` NESTE repo (gitignored, R-043),
>     via `adapter-generator` (modo `generate-one`) — nunca via `create_file` direto do Copilot.
>     Nenhum arquivo é criado no projeto externo (`<caminho-externo>`).
>     Nenhum artefato deste passo toca `catalog.yaml` ou a raiz de `.github/instructions/` (compartilhados).
>
> 💡 **Glossário de Domínio Opcional (`CONTEXT.md`)**: Ao gerar o adapter do projeto, caso o projeto possua termos de negócio ou regras recorrentes com jargão específico, o fluxo pode propor a criação de um `CONTEXT.md` a partir do template canônico (`docs/agent-context/templates/CONTEXT.template.md`) para alimentar a compressão semântica via `ctx_search`.

#### 2.5 Preview + Confirmação
- Mostrar YAML gerado
- Pedir: **"Proceder?"** (y/n)
- Se NÃO: voltar ao passo 2.3

**Output Fase 2**: YAML + Markdown revisados, preview aprovado

### FASE 3: **Binding Atômico via Tools Nativas** (Execução — sem script externo)

**Regra R-008**: Preferir `ctx_execute`/`ctx_batch_execute` para coleta e validação; aplicar mudanças com tools de edição de arquivo.

O Copilot aplica mudanças **atomicamente por plano validado** (sem depender de runtime Python):

**Pré-requisitos**:
- ✅ FASE 2 concluída: `novo_projeto.yaml` revisado; adapter (se aplicável) já criado pelo `adapter-generator` na FASE 2.4
- ✅ YAML validado (sem indentação errada, sem chaves duplicadas)
- ✅ Preview aprovado pelo usuário

**Execução (somente neste repositório, artefatos LOCAIS/gitignored — R-043)**:
1. **Validar**: schema YAML, kebab-case, sem duplicatas em `projects.local.yaml`; adapter (se aplicável) já criado pelo agent na FASE 2.4 com sucesso
2. **Planejar**: 2–3 operações — este prompt só cuida de `projects.local.yaml` + READMEs; o adapter já foi criado pelo agent
3. **Preview**: arquivos a serem modificados → "Proceder? (y/n)"
4. **Executar** (se confirmado):
   - Backup automático de arquivos
   - [CREATE-SE-AUSENTE] `.github/projects.local.yaml` ← copiar de `projects.local.yaml.example` se ainda não existir
   - [UPDATE] `.github/projects.local.yaml` ← NESTE repo, gitignored (NUNCA `catalog.yaml`) — próprio prompt, não o agent
   - [UPDATE] `.github/instructions/README.md` ← NESTE repo (referência, sem dado de projeto real)
   - [UPDATE] `.github/instructions/README.md` ← NESTE repo (referência, sem dado de projeto real)
   - ❌ Nenhuma operação no projeto externo
   - ❌ Nenhuma operação em `.github/instructions/README.md` (compartilhado/commitado)
5. **Validar pós**: YAML válido, entrada presente em `projects.local.yaml`; arquivo do adapter (se aplicável) existe em `.github/instructions/local/`
6. **Atomicidade**: Qualquer erro → abortar operação e reaplicar estado anterior por patch reverso

**Saída esperada**:
```
✅ Artefato validado: projeto
✅ [FASE 2.4 — via adapter-generator] .github/instructions/local/<nome>.instructions.md  ← gitignored, NESTE repo
✅ [CREATE-SE-AUSENTE] .github/projects.local.yaml       ← gitignored, NESTE repo
✅ [UPDATE] .github/projects.local.yaml                 ← gitignored, NESTE repo
✅ [UPDATE] .github/instructions/README.md                          ← NESTE repo
✅ [UPDATE] .github/instructions/README.md                     ← NESTE repo
✅ YAML válido
⚠️  Nenhum arquivo modificado nos projetos externos
⚠️  Nenhuma entrada escrita em .github/instructions/README.md (compartilhado — R-043)
🎉 Artefato gerado com sucesso!
```

**Output Fase 3**: Projeto registrado em `projects.local.yaml` (gitignored) + adapter em `.github/instructions/local/` (gitignored) → pronto para `/deep-search`, `/plan`

**Sanity check final (defesa em profundidade — R-043):** antes de reportar sucesso, executar `git status --short .github/instructions/README.md .github/instructions/` e confirmar que **nenhuma** dessas duas entradas aparece como modificada/staged (o esperado é aparecerem apenas `projects.local.yaml` e `.github/instructions/local/*`, ambos já gitignored e portanto invisíveis ao `git status` padrão). Se `catalog.yaml` aparecer como modificado, PARAR e reportar erro — algo escreveu no arquivo errado.

### FASE 4: **Construção e Registro Obrigatório no Grafo de Conhecimento** (bloqueante, sem opt-out)

> **Por que é obrigatória (não mais opcional):** o grafo de conhecimento (`code-knowledge-graph`) é a única forma de garantir que o mapa estrutural do projeto (imports, chamadas, acoplamento, blast radius) permaneça **sempre disponível** via `ctx_index`/`ctx_search`, independente de quanto o contexto da conversa cresça ou seja truncado. Modelos de menor capacidade (ex.: Claude Haiku) degradam a retenção de detalhes de projeto conforme o contexto aumenta — indexar o grafo fora da janela de contexto (em cache pesquisável) e registrá-lo no **Registry do Codegraph** para o MCP multi-repo é a mitigação estrutural para essa perda. Por isso esta fase **nunca pergunta "deseja construir?"** — ela sempre executa como parte do registro do projeto, exatamente como FASE 3 (binding).

**Pré-requisito**: FASE 3 concluída com sucesso — `project-id` já existe em `projects.local.yaml` (o agent indexa na chave `code-graph:<project-id>:<hash>`).

1. Verificar se já existe grafo válido para o hash atual: `ctx_search(queries: ["code-graph"], source: "<nome-projeto>")`.
2. **Se já existe e o hash bate** (nenhum arquivo do escopo mudou) → reaproveitar, sem reconstruir; reportar aviso compacto de 1 linha.
3. **Caso contrário (não existe, ou hash mudou)** → invocar SEMPRE, sem pedir confirmação prévia (a própria execução de `/add-project-context` já é o consentimento explícito para esta fase):
   ```
   run_subagent(
     agentName: "code-knowledge-graph",
     description: "Construir grafo obrigatório e registrar no MCP do projeto <nome>",
     task: "RF-001 (fluxo MANDATÓRIO de /add-project-context):
            projeto recém-registrado <nome-projeto> (project-id em projects.local.yaml),
            path <caminho-absoluto>.
            1. Invocar o motor @optave/codegraph (codegraph build <caminho-absoluto>) gerando .codegraph/graph.db.
            2. Registrar automaticamente o repositório no catálogo MCP multi-repo: codegraph registry add <caminho-absoluto>.
            3. Indexar resumo estruturado via ctx_index na chave code-graph:<project-id>:<hash>.
            4. Se solicitado visualizador interativo, gerar via codegraph plot --output codegraph-view.html --cluster community --color-by role --size-by fan-in --no-open."
   )
   ```
4. Reportar o resultado (nós/arestas, cobertura, status do registry MCP e da indexação) como parte do relatório de sucesso da FASE 4 — **falha desta fase não é bloqueante para o registro do projeto já feito na FASE 3** (aditivo), mas DEVE ser reportada com evidência e próximo passo mínimo se não completar.

**Saída esperada:**
```
[FASE 4 ✅] run_subagent(code-knowledge-graph) — grafo construído e registrado no MCP
├─ Motor: @optave/codegraph (CLI, .codegraph/graph.db)
├─ MCP Registry: ✅ Registrado no catálogo multi-repo (codegraph registry add)
├─ Nós: <n> | Arestas: <n> | Cobertura: <%>
├─ Indexado via ctx_index: ✅ code-graph:<project-id>:<hash>
└─ Grafo disponível para consulta (ctx_search e MCP multi-repo) no restante da sessão
```

### FASE 4.2: **Indexação de Código-Fonte no Knowledge Base (`ctx_index`)** (bloqueante, sem opt-out)

> **Objetivo:** Indexar os arquivos de código-fonte do projeto (`src/`) no Knowledge Base persistente (FTS5 SQLite) via `ctx_index`.
> **Por que é essencial:** Evita que agentes subsequentes (`angular-engineer`, `spring-boot-engineer`, etc.) executem comandos de terminal (`grep`, `find`, `cat`, `node -e`) ou usem múltiplos `read_file` para entender a lógica. Com o código indexado, qualquer busca por classes, decorators, stores ou métodos é resolvida via `ctx_search(source: "code:<project-id>")` com mínimo consumo de tokens.

1. **Identificar subpasta de código**:
   - Angular / React / Vue / Node: `<caminho-absoluto>/src`
   - Spring Boot / Java: `<caminho-absoluto>/src/main/java`
   - Python: `<caminho-absoluto>/src` ou `<caminho-absoluto>/<pacote>`
   - Fallback genérico: `<caminho-absoluto>/src` se existir; caso contrário `<caminho-absoluto>`.
2. **Executar `ctx_index` de código**:
   ```javascript
   ctx_index({
     path: "<subpasta-de-codigo>",
     source: "code:<project-id>",
     exclude: [
       "**/*.spec.ts",
       "**/*Test.java",
       "**/test/**",
       "**/tests/**",
       "**/assets/**",
       "**/environments/**",
       "**/dist/**",
       "**/build/**",
       "**/node_modules/**"
     ],
     maxFiles: 200
   })
   ```
3. **Exibir confirmação no relatório**:
   ```
   [FASE 4.2 ✅] Código-fonte indexado no Knowledge Base (FTS5)
   ├─ Origem: <subpasta-de-codigo>
   ├─ Source: code:<project-id>
   └─ Pronto para consultas limpas via ctx_search (sem poluição de terminal)
   ```

### FASE 4.1: **Descoberta de Integrações Multi-Projeto e Configuração de Fronteiras (`manifesto.boundaries`)**

> **Objetivo**: Quando houver mais de 1 projeto registrado no repositório de governança (identificado em `.github/instructions/local/` ou `projects.local.yaml`), o Copilot identifica relações de integração/dependência entre o novo projeto e os projetos já existentes, configurando automaticamente o manifesto de fronteiras arquiteturais (`manifesto.boundaries`) em `.codegraphrc.json` para deixar o ecossistema pronto para auditoria de arquitetura, CI gates e detecção de drift.

1. **Condição de ativação**: Listar projetos registrados em `.github/instructions/local/` (ou ler chaves de `projects.local.yaml`).
   - Se total de projetos registrados $\le 1$ → pular esta fase e prosseguir para FASE 4.5.
   - Se total de projetos registrados $\ge 2$ → executar passos 2, 3 e 4 abaixo.

2. **Sequência de Perguntas de Integração via `ask_questions` (R-027)**:
   ```
   [Q-INT1] "Quais projetos registrados possuem integração direta com '<novo-projeto>'?"
     - Opções geradas: Lista dos outros projetos existentes em projects.local.yaml (ex.: "meu-projeto-backend", "meu-auth-service") + "Nenhuma integração direta"
     - Multi-seleção: Sim (permite selecionar múltiplos projetos integrados)

   [Q-INT2] "Qual a direção/papel da integração com cada projeto selecionado?" (somente se selecionou projetos em Q-INT1)
     - Opções:
       (A) "<novo-projeto> consome APIs/serviços de [projeto-selecionado]" (ex.: Frontend ➔ Backend)
       (B) "[projeto-selecionado] consome APIs/serviços de <novo-projeto>" (ex.: Backend ➔ Microserviço)
       (C) "Integração bidirecional / eventos assíncronos"
       (D) "Compartilhamento de contratos / módulos compartilhados (aliases)"
   ```

3. **Configuração Automática do Manifesto (`.codegraphrc.json`)**:
   - A partir das respostas, gerar/atualizar o arquivo `.codegraphrc.json` no projeto com as regras de fronteira (`manifesto.boundaries`) e `aliases` correspondentes:
     ```json
     {
       "manifesto": {
         "boundaries": {
           "modules": {
             "<novo-projeto>": "src/**",
             "<projeto-integrado>": "<path_externo-do-outro-projeto>/src/**"
           },
           "rules": [
             {
               "from": "<modulo-consumidor>",
               "onlyTo": ["<modulo-provedor>"]
             }
           ]
         }
       }
     }
     ```
   - Deixar o manifesto pronto para validação contínua com `codegraph check --staged --boundaries` e visualização com `codegraph plot --cluster community` / `codegraph communities --drift`.

4. **Saída esperada:**
```
[FASE 4.1 ✅] Fronteiras Arquiteturais Multi-Projeto Configuradas
├─ Projetos integrados: <novo-projeto> ➔ <projeto-integrado>
├─ Manifesto configurado: .codegraphrc.json (boundaries.rules ativas)
└─ Pronto para validação via codegraph check --boundaries e inspeção de drift
```

### FASE 4.5: **Sugestão de Sumarização de Código-Fonte** (não-bloqueante, opcional)

> Funcionalidade: ao término da FASE 4, oferecer ao usuário a opção de sumarizar código-fonte via agent especialista dedicado. Execução é sempre sob demanda — nunca automática (R-009). Diferente da FASE 4 (grafo), esta permanece opcional: sumário textual é um complemento de leitura, não uma proteção estrutural contra perda de contexto.

**Regra R-009**: nunca executar sumarização automaticamente — sempre aguardar confirmação explícita.

1. Verificar histórico: `ctx_search(queries: ["sumarização concluída", "resumo de código"], source: "<nome-projeto>")`.
2. **Se 0 resultados** (projeto nunca foi sumarizado) → exibir via `ask_questions`:
   > "Projeto '<nome-projeto>' foi registrado e seu grafo de conhecimento já está indexado. Deseja também iniciar a sumarização de código-fonte via agent especialista agora? (A) Sim, agora (B) Não, decidir depois"
3. **Se houver resultado prévio** → exibir aviso compacto de 1 linha, sem reabrir `ask_questions`:
   > `ℹ️ Projeto '<nome-projeto>' já possui sumarização anterior — invoque o agent especialista sob demanda se precisar de um resumo atualizado.`
4. Se usuário escolher (A) → `run_subagent(agentName: "code-knowledge-graph", description: "Sumarizar projeto <nome>", task: "Sumarizar arquivos-fonte do projeto registrado: <nome-projeto>...")`. Esta etapa é **aditiva**: o sucesso das FASES 3 e 4 já foi reportado antes deste passo e não depende dele.

**Saída esperada (caso A):**
```
ℹ️ Projeto 'meu-projeto-backend' registrado, grafo de conhecimento indexado.
Deseja também iniciar a sumarização de código-fonte via agent especialista agora? (A) Sim (B) Não
```

---

## 📊 Exemplo de Saída Esperada


```
[FASE 1 ✅] run_subagent(adapter-generator, modo=scan) — projeto externo, somente leitura
├─ Projeto escaneado: <workspace>/[PROJETO] (read-only)
├─ Linguagem: Java 17
├─ Framework: Spring Boot 3
├─ Stack: Spring Boot 3 + Hibernate + JUnit 5
├─ Estrutura: Layered (controllers, services, repositories, models)
├─ Codestyle: Checkstyle + Maven
├─ Testing: JUnit 5 + Mockito
├─ CI/CD: GitHub Actions
├─ Convenções: @Log4j2, exceções customizadas, PT-BR logging
└─ ❌ Nenhum arquivo modificado (nem no projeto externo, nem neste repo)

[FASE 2 ✅] Perguntas + run_subagent(adapter-generator, modo=generate-one)
├─ Pergunta 1: "Nome do projeto?" → meu-projeto-backend
├─ Pergunta 2: "Descrição?" → Serviço de processamento de [domínio]
├─ Pergunta 3: "Qual adapter herdar ou criar novo?" → criar novo adapter
├─ Gerados (via adapter-generator, NESTE repo, gitignored — R-043):
│  ✓ .github/instructions/local/meu-projeto-backend.instructions.md ← criado pelo agent
├─ Gerado (por este prompt, ainda em memória — não escrito):
│  ✓ novo_projeto.yaml (entry para projects.local.yaml)
└─ Preview aprovado ✅

[FASE 3 ✅] Binding Atômico via Tools Nativas (NESTE repositório, LOCAIS/gitignored)
├─ Execução: aplicação de patches/edições por plano aprovado
├─ Validação: ✅ Artefato validado (schema OK, sem duplicatas); adapter já criado na FASE 2.4
├─ Plano: 3 operações (UPDATE projects.local.yaml, UPDATE READMEs) — todas NESTE repo
├─ Preview: 3 arquivos serao modificados → [Proceder? (y/n)] → y
├─ Execução:
│  ✅ [UPDATE] .github/projects.local.yaml                        ← NESTE repo, gitignored
│  ✅ [UPDATE] .github/instructions/README.md                                 ← NESTE repo
│  ✅ [UPDATE] .github/instructions/README.md                            ← NESTE repo
│  ❌ Nenhuma operação no projeto externo (meu-projeto-backend/)
│  ❌ Nenhuma operação em .github/instructions/README.md (compartilhado — R-043)
├─ Validação pós: ✅ YAML válido, entrada presente em projects.local.yaml
├─ Sanity check: ✅ git status --short confirma catalog.yaml intocado
└─ Resultado: 🎉 Artefato gerado com sucesso!

🚀 Projeto adicionado! Agora pronto para: /deep-search, /plan, /implement
```

[FASE 4 ✅] run_subagent(code-knowledge-graph) — grafo obrigatório construído e registrado no MCP
```
├─ Motor: @optave/codegraph (CLI, .codegraph/graph.db)
├─ MCP Registry: ✅ Registrado no catálogo multi-repo (codegraph registry add)
├─ Nós: 128 | Arestas: 340 | Cobertura: 92%
├─ Indexado via ctx_index: ✅ code-graph:meu-projeto-backend:a1b2c3
└─ Grafo disponível para consulta (ctx_search e MCP multi-repo) no restante da sessão
```

[FASE 4.1 ✅] Fronteiras Arquiteturais Multi-Projeto Configuradas (quando >1 projeto)
```
├─ Perguntas de integração respondidas via ask_questions (Q-INT1 / Q-INT2)
├─ Projetos integrados: meu-frontend ➔ meu-projeto-backend
├─ Manifesto gerado/atualizado: .codegraphrc.json (boundaries.rules ativas)
└─ Pronto para validação via codegraph check --boundaries e inspeção de drift
```

---

## 🔄 Quando Usar

- **Início de tarefa em projeto novo** ← Use ANTES de `/deep-search`
- **Mudança de contexto entre projetos** ← Use quando trocar de repo
- **Preparação para refatoração** ← Use ANTES de `/plan`
- **Validação de padrões** ← Use quando não tem certeza de convenção

---

## 🚨 Troubleshooting &Validação YAML

### Validação YAML Obrigatória

**TODA VEZ QUE ALTERAR ARQUIVOS `.yml` ou `.yaml`, execute validação.**

#### Como Validar

**Opção A: yamllint (se disponível)**
```bash
yamllint .github/projects.local.yaml
```

**Opção B: validação estrutural via revisão de diff**
- Confirmar identação consistente (2 espaços)
- Confirmar chaves obrigatórias e sem duplicatas
- Confirmar bloco `projetos:` íntegro em `projects.local.yaml` (nunca em `catalog.yaml` — R-043)

#### Checklist Pré-Confirmação (FASE 2.5)

Antes de confirmar `"Proceder? (y/n)"` em Fase 2:

- [ ] `novo_projeto.yaml` foi validado sem erros?
- [ ] Indentação é consistente (2 espaços)?
- [ ] Sem tabs ou espaços misturados?
- [ ] Todas as aspas fechadas?
- [ ] Destino confirmado é `projects.local.yaml` + `.github/instructions/local/` (nunca os compartilhados)?

**Se falhar em qualquer ponto**: PARE, corrija manualmente, e valide novamente.

### Problemas Comuns

| Problema | Causa | Solução |
|----------|-------|---------|
| "Projeto já existe em catalog" | Nome duplicado | Use nome único, ex: `projeto-exemplo-unico` |
| "Copilot não apresenta descobertas" | Prompt não carregado corretamente | Reexecute `/add-project-context` ou carregue manualmente |
| "Erro ao atualizar projects.local.yaml" | YAML inválido | Valide YAML conforme checklist acima |
| `mapping values are not allowed here` | Indentação errada | Use **2 espaços**, nunca tabs |
| `could not find expected ':'` | YAML malformado | Valide sintaxe de `key: value` |
| `duplicate key` | Chave duplicada | Remova entrada duplicada |
| "Falha de validação de payload" | YAML gerado incompleto | Verificar se `novo_projeto.yaml` tem: artefato, nome, tipo, extends, descrição |
| "Execução abortada" | Erro em patch/edição de arquivo | Revisar preview, corrigir entrada e reexecutar |
| "projects.local.yaml não existe" | Primeira vez nesta máquina/clone | Copiar de `projects.local.yaml.example` (feito automaticamente no Health Check) |
| "catalog.yaml apareceu modificado no git status" | Escrita indevida no arquivo compartilhado — violação de R-043 | PARAR, reverter via `git checkout .github/instructions/README.md`, reportar bug |
| "codegraph falhou na FASE 4" | CLI `@optave/codegraph` não instalado globalmente | Executar `npm install -g @optave/codegraph` e verificar `codegraph --version`; FASE 4 reporta erro real mas não bloqueia o binding da FASE 3 |

---

## ✅ Checklist: Copilot Executou Corretamente?

Após invocar `/add-project-context <workspace>/[PROJETO]`, verifique:

- [ ] **FASE 1**: Copilot invocou `run_subagent(agentName: "adapter-generator", task: "modo=scan...")` (nunca escaneou inline) e apresentou descobertas (Stack, Frameworks, Estrutura, Codestyle)?
- [ ] **FASE 2.1**: Solicitou ou inferiu o caminho do projeto corretamente?
- [ ] **FASE 2.2**: Apresentou descobertas a partir do `project_profile` da FASE 1, sem re-escanear?
- [ ] **FASE 2.3**: Fez exatamente **3 perguntas** (nome, descrição, adapter)?
- [ ] **FASE 2.3**: Sugeriu nome baseado no path? (ex: `meu-projeto-backend`)
- [ ] **FASE 2.3**: Sugeriu adapter baseado no stack detectado?
- [ ] **FASE 2.4**: Invocou `run_subagent(agentName: "adapter-generator", task: "modo=generate-one...")` para criar `<nome>.instructions.md` em `.github/instructions/local/` (se criar novo) — nunca via `create_file` direto do Copilot?
- [ ] **FASE 2.5**: Mostrou preview antes de confirmar?
- [ ] **FASE 3**: Aplicou plano de alterações por tools nativas (só `projects.local.yaml` + READMEs — adapter já criado na FASE 2.4)?
- [ ] **FASE 3**: Confirmou: ✅ "Artefato gerado com sucesso!"?
- [ ] **Pós-execução**: `.github/projects.local.yaml` foi atualizado (gitignored)?
- [ ] **Pós-execução**: `.github/instructions/README.md` (compartilhado) permaneceu **intocado**?
- [ ] **Pós-execução**: `.github/instructions/README.md` foi sincronizado (referência, sem dado real)?
- [ ] **FASE 4 (OBRIGATÓRIA, sem opt-out)**: `code-knowledge-graph` foi invocado sempre logo após a FASE 3 (gerando o grafo via `codegraph build`, registrando no catálogo MCP via `codegraph registry add` e indexando via `ctx_index`), sem `ask_questions` de "deseja construir?"?
- [ ] **FASE 4.1**: se houver >1 projeto registrado em `.github/instructions/local/` (ou `projects.local.yaml`), o Copilot disparou a sequência de `ask_questions` de integração e configurou o manifesto de fronteiras (`manifesto.boundaries`) em `.codegraphrc.json`?
- [ ] **FASE 4.5 (opcional)**: se usuário aceitou, `code-knowledge-graph` foi invocado **depois** da FASE 4?

**Se todos checkpoints completaram**: ✅ **Sucesso!**  
**Se algum falhou**: ⚠️ Ver seção Troubleshooting acima.

---

## 🔍 Próximos Passos Após Execução

Após `/add-project-context` completar com sucesso (FASES 1-4, incluindo grafo de conhecimento já indexado):

- **`/deep-search <tema>`** — explorar padrões específicos com contexto já estruturado
- **`/plan`** — planejar mudanças com knowledge base do projeto pronto (grafo já disponível via `ctx_search`)
- **`/implement`** — executar com `/ctx-checkpoint` para continuidade
- **`/validate`** — validar qualidade do projeto

Exemplo típico:
```bash
/add-project-context meu-projeto-backend
/deep-search "como usar @EmbeddedId"
/plan "refatorar Entity para usar EmbeddedId"
```

---


