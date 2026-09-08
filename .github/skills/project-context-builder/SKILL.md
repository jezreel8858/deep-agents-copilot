---
name: project-context-builder
tier: 2
type: discovery-and-generation
input_type: path-based
output_type: structured-artifacts

description: 
  Scanner automático de projetos + Copilot Chat. Detecta stack, padrões e convenções
  localmente (offline), depois Copilot gera novo_projeto.yaml + xxx.instructions.md
  usando SEU PRÓPRIO MODELO (sem APIs externas). Funciona via `/add-project-context`.

triggers:
  - "/add-project-context"
  - "novo projeto"
  - "adicionar projeto ao binding"
  - "scaffolding automático"
  - "escanear projeto"

source_docs:
  - ".github/prompts/add-project-context.prompt.md"
  - ".github/agents/adapter-generator.agent.md"
  - "docs/ai-context/catalog.yaml"

capabilities:
  - name: "scan_project_structure"
    input: "caminho relativo ou absoluto do projeto"
    output: "detected stack, patterns, examples, conventions"
    
  - name: "generate_project_yaml"
    input: "scan output + nome + tipo + descrição"
    output: "novo_projeto.yaml pronto para atualização atômica do catalog"
    
  - name: "generate_instructions_md"
    input: "scan output + patterns coletados"
    output: "xxx.instructions.md com conventions do projeto"

workflow:
  1: "User informa caminho do projeto"
  2: "Scanner detecta stack, coleta exemplos (offline)"
  3: "Bot pergunta estrutura (nome, tipo, extends, descrição)"
  4: "Copilot Chat usa seu modelo para gerar artefatos (sem APIs)"
  5: "Executa atualização guiada via tools nativas (sem script externo)"

constraints:
  - "Scanner executado localmente (offline, sem custo)"
  - "Geração de artefatos feita por Copilot Chat (seu modelo, sem APIs externas)"
  - "Sempre pedir confirmação antes de criar arquivos"
  - "Fallback para atualização manual com preview em caso de falha de tooling"

category: process
tools:
  - "read_file"
  - "create_file"
  - "list_dir"
  - "grep_search"
  - "file_search"
---

# project-context-builder — Skill de Descoberta de Projeto

## Precedentes de Mercado (Pesquisa Externa — R-019, 2026-09-01)

> O padrão "scanner local determinístico → IA gera artefato customizado → preview → confirmação" já é validado por ferramentas reais de mercado (2025-2026):
> - **GitHub Copilot CLI `/init`**: "Copilot will scan your project and create tailored instruction files" ([github/copilot-cli-for-beginners](https://github.com/github/copilot-cli-for-beginners)).
> - **`npx ai-setup`**: escaneia o codebase e gera `.github/copilot-instructions.md`, `CLAUDE.md`, `.cursorrules` automaticamente ([Reddit r/GithubCopilot](https://www.reddit.com/r/GithubCopilot/comments/1s6ppan/)).
> - **`npx agentseed init`**: lê o codebase e gera `AGENTS.md` via análise estática (sem custo), com fallback LLM opcional ([Reddit r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/comments/1r0ixum/)).
>
> Conclusão: nenhuma mudança estrutural é necessária neste fluxo — a arquitetura já reflete o padrão consolidado. Ver também `project-scanner-governance/SKILL.md` § 7 para a pesquisa completa (inclui OWASP LLM02/LLM06 e nomenclatura `OverwriteStrategy` do Nx).

## Overview

Automatiza o processo de **adicionar novo projeto ao binding** via Copilot Chat:

```
User: /add-project-context
  ↓
FASE 1: Scanner Local (offline)
  • Detecta stack (Java, TS, Python, etc)
  • Extrai padrões (nomeclatura, tests, structure)
  • Coleta exemplos reais
  ↓
FASE 2: Perguntas Estruturadas (no chat)
  • Nome? Tipo? Extends? Descrição?
  ↓
FASE 3: Copilot Chat Gera Artefatos (seu modelo, sem APIs)
  • novo_projeto.yaml
  • xxx.instructions.md
  ↓
FASE 4: Preview + Confirmação
  • User revisa no chat
  • Confirma para executar
  ↓
FASE 5: Executa atualização atômica
  • Cria arquivos atomicamente
```

## Fluxo Completo

### Stage 1: Input & Validation

```text
input_path = "caminho do projeto (relativo ou absoluto)"
validated_path = validate_path(input_path)
if not is_valid_project_path(validated_path):
  return "❌ Caminho inválido ou projeto não detectado"
```

### Stage 2: Local Scanning (Offline)

```text
scanner = ProjectScanner(validated_path)
detected = scanner.detect_stack()
patterns = scanner.extract_patterns()
examples = scanner.collect_examples(count=5)
```

### Stage 3: Structured Questions (no Copilot Chat)

```
Copilot pergunta:
1. Nome do projeto? [custom-app]
2. Tipo? [backend ou frontend]
3. Extends? [backend-stack ou frontend-stack]
4. Descrição? [Serviço customizado]
```

### Stage 4: Copilot Chat Generation (Seu Modelo, Sem APIs)

```
Copilot Chat recebe o contexto:
{
  "detected_stack": "java-spring",
  "patterns": {package_base, naming, structure, tests, ...},
  "real_examples": [3-5 arquivos reais do projeto],
  "user_input": {nome, tipo, extends, descrição}
}

Copilot usa SEU PRÓPRIO MODELO (instalado em seu IDE):
✅ Claude em VS Code/JetBrains com Copilot Chat
✅ GPT-4 em outros IDEs
✅ Sem chamar APIs externas (tudo local)

Copilot gera:
{
  "novo_projeto.yaml": "artefato: projeto\nnome: ...",
  "xxx.instructions.md": "---\napplyTo: [...]\n..."
}

Resultado: TUDO NO CHAT, visível para revisar
```

### Stage 5: Preview, Confirmação & Execução

```
1. User revisa os arquivos gerados NO CHAT
   • novo_projeto.yaml
   • xxx.instructions.md
   • (pode editar se precisar)

3 Confirmar para executar
   ↓
4. Handler executa atualização atômica do binding
   (catalog + binding + README de instruções)
   
4. Resultado:
   ✅ Arquivos criados atomicamente
   ✅ YAML validado
   ✅ Rollback lógico com patch mínimo se erro
```

## Casos de Uso

| Caso | Input | Output |
|------|-------|--------|
| Novo backend Spring Boot | `/add-project-context` → path | novo_projeto.yaml + backend.instructions.md |
| Novo frontend Angular | path | novo_projeto.yaml + frontend.instructions.md |
| Variante de stack existente | path (herda padrões) | yaml + instructions com padrões customizados |

## Fallbacks & Contingências

| Cenário | Fallback |
|---|---|
| Scanner falha | CLI interativa (perguntas manuais) |
| Copilot timeout (raro) | Usar templates base (genéricos) |
| Arquivo existe | Ask overwrite ou versioning |
| Path inválido | Sugerir paths válidos do workspace |

## Extensibilidade

Adicionar novo tipo de stack:
1. Criar detector em `scanner.py` (e.g., `detect_rust()`)
2. Adicionar exemplos de nomeclatura
3. Criar template `rust-stack.instructions.md`
4. Atualizar config.json

---

**Status**: Skill v1.0 (Copilot Chat) — Pronto para uso imediato  
**Integração**: `/add-project-context` no Copilot Chat  
**LLM**: Copilot Chat (seu modelo no IDE, sem APIs externas)  
**Custo**: Zero (offline na Fase 1, Copilot nativo na Fase 2)

