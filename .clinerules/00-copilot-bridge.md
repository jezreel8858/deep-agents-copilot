# Unified AI Architecture Bridge (Cline, Copilot & Claude)

Esta ponte de governança estabelece o alinhamento operacional entre **Cline**, **GitHub Copilot** e **Claude Desktop** com o ecossistema de agentes especializado do repositório. É **estritamente obrigatório** ler e seguir este documento antes de iniciar qualquer tarefa.

## Execução de Comandos Python
Sempre utilize o caminho absoluto do interpretador Python:
`/d/Dev/Programas/python-3.12.10.amd64/python/python.exe`

---

## 1. Fonte Única de Verdade (SSOT) & Diretrizes Globais
- **Governança Canônica Universal:** `CLAUDE.md` (na raiz).
  - Define as regras normativas inegociáveis (R-001 a R-067).
  - Estabelece as convenções de código, gestão de estado e políticas de segurança.
- **Runtime e Instruções Operacionais:** `.github/copilot-instructions.md`.
  - Estabelece as regras operacionais de runtime, gerenciamento de modelos e a política de ferramentas.

---

## 2. Protocolo de Subagentes & Emulação no Cline (R-037 / R-042)
No Cline, onde a invocação nativa de API de subagente (`run_subagent`) não está disponível para executores de terceiros, a orquestração ocorre via **Emulação de Perfil (In-Context Persona Swapping)**:

1. **Agent Router First (R-037)**:
  - **Toda solicitação** deve iniciar consultando `.github/agents/agent-router.agent.md`, `.github/agents/catalog.yaml` e `.github/agents/routing-graph.yaml`.
  - O assistente deve classificar a intenção do usuário e determinar o especialista correto para o atendimento.

2. **Carregamento Dinâmico de Contrato de Subagente**:
  - Após o roteamento, o assistente **deve ler o arquivo do subagente delegado** em `.github/agents/<agente-delegado>.agent.md`.
  - Adote imediatamente o perfil, as restrições inegociáveis (`❌ CRÍTICO`), as ferramentas e o checklist do subagente selecionado.

3. **Re-triagem por Turno e Anti Sticky-Session (R-042)**:
  - A cada novo turno, avalie se a nova mensagem do usuário implica em alteração de escopo ou deriva de intenção.
  - Se houver deriva de intenção, devolva o controle ao `@agent-router` antes de responder.

---

## 3. Workflows Operacionais Determinísticos (R-050)
Toda tarefa técnica deve se enquadrar e seguir os estágios formais descritos em `.github/agents/workflows.md`:
- **`WORKFLOW-BUG-FIX`**: Triagem -> Red Test -> Fix Cirúrgico -> Green Test -> Quality Gate.
- **`WORKFLOW-REFACTORING`**: Extração de Regras -> Mapeamento de Grafo/Blast Radius -> Plano Mikado -> Execução em Lote -> Validação.
- **`WORKFLOW-FEATURE-DEVELOPMENT`**: Elicitação de Requisitos -> Blueprint Técnico -> Estratégia de Testes -> TDD -> Duplo Gate.
- **`WORKFLOW-GOVERNANCE-MAINTENANCE`**: Auditoria -> Checkpoint Humano -> Execução em Lote -> Gate de Governança.

---

## 4. Banner de Agente Ativo & Formato de Saída (R-028)
Toda resposta técnica gerada pelo assistente (seja no Copilot ou Cline) **deve iniciar obrigatoriamente** declarando o agente ativo e o workflow atual:

```text
Agente Ativo: @<nome-do-agente-delegado>
Workflow: <NOME-DO-WORKFLOW>
Etapa: <Etapa Atual Workflow do>

### 1. Abordagem
<Estratégia de resolução>

### 2. Artefatos Modificados
<Caminhos alterados arquivos dos exatos>

### 3. Economia de Turnos
<Consolidação de em lote operações>

### 4. Riscos / Alinhamento
<Invariantes e gates preservados quality>

### 5. Próximo Passo
<Conclusão da do etapa ou próxima workflow>
```

---

## 5. Mapeamento de Ferramentas e Execução no Cline
Quando operando via Cline, utilize a seguinte correspondência de ferramentas:

| Operação no Copilot / MCP | Ferramenta Nativa no Cline |
|---|---|
| Leitura / Inspeção de código | `read_file` |
| Criação / Modificação de arquivos | `write_to_file` / `replace_in_file` |
| Execução de Comandos / Build / Testes | `execute_command` |
| Pesquisas / Varreduras | `search_files` / `find_by_name` |
| Pesquisa Read-Only em Subagente (`deep-search`) | `use_subagents` (recurso nativo do Cline para exploração paralela) |

---

## 6. Fluxo Unificado de Execução
1. **Health Check (R-034)**: Valide a existência de `.github/instructions/README.md` e dos arquivos de ambiente local.
2. **Descobrir & Rotear (R-037)**: Leia `agent-router.agent.md` e `catalog.yaml`, defina a rota e o workflow correto.
3. **Ingerir Contrato**: Carregue o arquivo `.github/agents/<agente>.agent.md`.
4. **Planejar**: Proponha o plano de execução alinhado com o workflow ativo.
5. **Executar em Lote (R-046)**: Aplique as alterações e rode testes de verificação antes de concluir a entrega.
