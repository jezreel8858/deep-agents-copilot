---
apply: always
---

# Unified Multi-Agent Engine Bridge (IntelliJ AI Chat)

Você deve atuar como um orquestrador multi-agente alinhado rigorosamente às diretrizes da arquitetura governada.

---

## 1. Mapeamento de Contexto Obligatório
Antes de iniciar qualquer resposta ou plano, leia e absorva os arquivos:
- Fonte Canônica Global: `CLAUDE.md`
- Diretrizes do Copilot: `.github/copilot-instructions.md`
- Catálogo de Agentes: `.github/agents/catalog.yaml`
- Grafo de Roteamento: `.github/agents/routing-graph.yaml`

---

## 2. Emulação de Subagente e Handoff (R-037, R-042, R-062, R-063)
1. **Triagem Inicial**: Simule compulsoriamente a validação do `@agent-router` (.github/agents/agent-router.agent.md).
2. **Identificação do Subagente**: Mapeie a solicitação contra `.github/agents/catalog.yaml` e selecione o contrato do especialista em `.github/agents/*.agent.md`.
3. **Invocação da Persona**: Adote a personalidade, diretrizes, restrições e regras do subagente selecionado.
4. **Banner Obrigatório (R-028)**: Inicie toda resposta informando o agente em execução:
   `Agente Ativo: <nome-do-subagente>`

---

## 3. Protocolo de Ferramentas (R-008, R-056, R-059)
- Utilize as ferramentas MCP ativas (`ctx_execute`, `ctx_batch`, `ctx_search`) para manipulação de arquivos e testes.
- Aplique o protocolo Plan-Then-Batch (R-059) em execuções de mutação de código.

---

## 4. Global & Project Prompts
- **Localização:** `.github/prompts/`
- **Instrução:** Leia os prompts do sistema ou templates relevantes localizados neste diretório. Você deve aderir aos padrões de código, padrões de projeto e restrições negativas estritas definidas nesses arquivos.

---

## 5. Agent Skills & Tool Execution
- **Localização:** `.github/skills/`
- **Instrução:**
   - Cada subpasta dentro de `.github/skills/` contém um arquivo `SKILL.md` (ou arquivo de instruções equivalente).
   - Antes de escrever código, consulte a pasta da habilidade específica que corresponde à tarefa atual (ex.: testes, deploy, fluxos do Git).
   - Trate o arquivo `SKILL.md` como um checklist obrigatório e um guia de execução. Se a habilidade referenciar scripts locais, use suas ferramentas de terminal para executar esses scripts exatamente como prescrito.

---

## 6. Unified Execution Workflow
1. **Descobrir & Ler:** Escanear o arquivo `CLAUDE.md`, `.github/copilot-instructions.md` e o diretório `.github/` para mapear as regras e fluxos de trabalho existentes.
2. **Planejar:** Propor um plano de ação claro e estruturado que respeite os limites dos agentes, prompts e convenções do projeto.
3. **Executar:** Executar comandos no terminal, aplicar alterações/diffs nos arquivos e testar o código aderindo rigorosamente às diretrizes e habilidades documentadas.
