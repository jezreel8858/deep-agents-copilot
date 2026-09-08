---
name: del-project-context
description:
  Remove contexto estruturado de um projeto do overlay local (catalog.local.yaml,
  gitignored — R-043) e do cache Context Mode. Operação destrutiva com validação
  prévia, confirmação e rollback via Git. NUNCA toca docs/ai-context/catalog.yaml
  (compartilhado/commitado).
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['read_file', 'insert_edit_into_file', 'file_search', 'list_dir', 'ask_questions', 'run_subagent']
argument-hint: '<nome-do-projeto>'
source_docs:
  - CLAUDE.md
  - docs/ai-context/catalog.local.yaml.example
  - .github/instructions/README.md
---

# `/del-project-context`

> **Propósito**: Remover o registro de um projeto no overlay local `catalog.local.yaml` e seu adapter em `.github/instructions/local/`.
> **Workspace**: `${workspaceFolder}`
> **Projeto Alvo**: `${input:nomeDoProjeto}`

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** remover o projeto especificado de `catalog.local.yaml` e deletar seu adapter correspondente em `.github/instructions/local/`.
- ✅ **SEMPRE** solicitar confirmação humana explícita antes de executar a exclusão.
- ❌ **NÃO** tocar em `docs/ai-context/catalog.yaml` (compartilhado/commitado, R-043).
- ❌ **NÃO** excluir código-fonte ou diretórios do projeto real externo.

---

workflow:
  1: "User fornece nome do projeto"
  2: "Agent valida existência em catalog.local.yaml (gitignored, R-043)"
  3: "Agent lista artefatos a remover (YAML entry + arquivo .instructions.md em local/)"
  4: "Agent pede confirmação explícita"
  5: "Se confirmado: Atualiza catalog.local.yaml + valida YAML + registra em audit.log"

constraints:
  - "Operação destrutiva — exigir confirmação explícita"
  - "Validar YAML imediatamente após alteração"
  - "NÃO remove adapters globais nem código-fonte"
  - "NÃO usa rm ou operações shell destrutivas — Python via project-context-builder"
  - "NUNCA edita docs/ai-context/catalog.yaml (compartilhado/commitado) — R-043"
  - "Registrar ação em audit.log"
---

# `/del-project-context` — Remoção de Contexto de Projeto

## Visão Geral

Remove um projeto do overlay local (`docs/ai-context/catalog.local.yaml`, gitignored) e do
armazenamento de instruções locais (`.github/instructions/local/`) — **todos os artefatos
são NESTE repositório de governança, porém LOCAIS/gitignored (R-043)**. Reversível via Git
(arquivo local) ou recriação via `/add-project-context`.

> ⚠️  Esta operação modifica APENAS artefatos locais/gitignored deste repositório.
>     O repositório externo do projeto removido NÃO é tocado.
>     `docs/ai-context/catalog.yaml` (compartilhado/commitado) NUNCA é tocado.

## Uso

```bash
/del-project-context <nome-do-projeto>
```

### Exemplos

```
/del-project-context project-app
```

## O Que é Removido (NESTE repositório, LOCAIS/gitignored)

| Alvo | Ação | Observação |
|------|------|-----------|
| `./docs/ai-context/catalog.local.yaml` | Remove entrada YAML do projeto | Sintaticamente validado; gitignored |
| `./.github/instructions/local/<projeto>.instructions.md` | Deleta arquivo de instruções | Específico do projeto; gitignored |
| Context Mode Cache (FTS5) | Invalida índice + snapshot | TTL reset (24h) |

## O Que NÃO é Removido

- ✗ Repositório Git / código-fonte do projeto externo
- ✗ Qualquer arquivo dentro do projeto externo
- ✗ Adapters genéricos já existentes em `.github/instructions/` (raiz, compartilhados)
- ✗ `docs/ai-context/catalog.yaml` (compartilhado/commitado) — nunca teve entrada de projeto (R-043)
- ✗ Regras em `CLAUDE.md` (governança global)
- ✗ Documentação em `docs/` (preservada)

## Fluxo

```
/del-project-context meu-projeto-backend

[1] Validar existência em catalog.local.yaml (gitignored)  ✓
[2] Listar artefatos a remover                          ✓
[3] Pedir confirmação explícita (sim/não)               → User
[4] Se sim:
    ├─ Atualizar catalog.local.yaml (remove entrada YAML)
    ├─ Validar YAML com yamllint                        [fallback: abortar + Git checkout]
    ├─ Deletar .github/instructions/local/<projeto>.instructions.md
    └─ Registrar em audit.log
[5] Relatório: artefatos removidos + próximos passos    ✓
```

## Validação de YAML (Obrigatória)

Após qualquer alteração em `catalog.local.yaml`:

**Python (recomendado)**
```bash
python -c "import yaml; yaml.safe_load(open('docs/ai-context/catalog.local.yaml')); print('✅ Válido')" || echo "❌ Erro"
```

**yamllint**
```bash
yamllint docs/ai-context/catalog.local.yaml
```

Erros comuns:

| Erro | Causa | Solução |
|------|-------|---------|
| `mapping values are not allowed here` | Indentação errada | Revise indentação (2 espaços) |
| `could not find expected ':'` | Colon faltando | Verifique sintaxe |
| `unexpected indent` | Tabs/espaços misturados | Use sempre 2 espaços |

## Casos de Uso

| Situação | Ação |
|----------|------|
| Projeto descontinuado | `/del-project-context <nome>` |
| Reorganizar binding | `/del-project-context <antigo>` + `/add-project-context <novo>` |
| Cache corrompido | `/del-project-context` + `/add-project-context` (recupera) |
| Remover adapter customizado | `/del-project-context <nome>` |

## Recuperação

Se remover por engano:

```bash
# Recuperar via Git (só funciona se catalog.local.yaml estiver sob controle de versão local
# customizado pelo dev — por padrão é gitignored, então a via normal de recuperação é recriar):
/add-project-context <caminho-absoluto-do-projeto>
```

## Fallbacks

| Cenário | Ação |
|---|---|
| Project não encontrado em catalog.local.yaml | Abortar com mensagem clara |
| YAML inválido após remoção | Reverter com Git checkout (se local.yaml estiver versionado) ou recriar manualmente + report |
| Confirmação não fornecida | Aguardar entrada do user |

---

**Status**: Prompt v1.2 (Local Overlay Pattern — R-043)
**Integração**: Agent `project-context-builder`
**Dependência**: `yaml-governance` skill
**Referência**: `/add-project-context` (operação inversa)
**Audit**: Registrado em `.github/hooks/context-mode.json`
