## [2.8.10] — 2026-09-14

### Refatorado & Saneado
- **Limpeza Profunda de Seções Não-Homologadas e Citações em Frontmatter/Templates**:
  - Extirpação completa das seções legadas e redundantes no corpo Markdown (`## Regras Herdadas`, `## Catálogo / Conhecimento Base`, `## Skills Associadas`) em 9 arquivos de roteadores e templates (`agent-router.agent.md`, `router-agent.md`, `angular-router`, `spring-boot-router`, `spring-reactive-router`, `ejb-router`, `python-router`, `struts-router` e `database-router`).
  - Higienização de comentários e orientações nos frontmatters de todos os templates (`agent-template.md`, `operational-agent.md`, `research-agent.md`, `router-agent.md`, `skill-template.md`, `prompt-template.md`), além de `governance-factory.agent.md`, `binding-initializer.agent.md`, `governance-factory-patterns/SKILL.md` e `agent-memory-policy/SKILL.md`, removendo quaisquer menções instrucionais remanescentes aos nomes das seções legadas.
  - Consolidação formal de dependências documentais e de skills exclusivamente no frontmatter YAML `source_docs:` (SSOT), eliminando duplicação e acoplamento desnecessário no corpo dos agentes.
  - Saneamento de ferramentas do frontmatter de `agent-router.agent.md` removendo referências a ferramentas `angular-cli/*` não-reconhecidas.
- **Fortalecimento do Gate de Homologação de Seções (Smell 2.9)**:
  - `tests/governance_audit/test_template_sections.py`: O teste de homologação foi expandido para cobrir **100% dos agentes** (incluindo todos os routers e templates), garantindo que nenhuma seção não-homologada volte a ser introduzida em qualquer `.agent.md` do repositório.
  - `tests/governance_audit/test_router_agents.py`: Atualizadas as seções obrigatórias dos routers para as 4 seções canônicas de roteamento (`CRÍTICO: ESCOPO`, `Decision Tree`, `Formato de Saída`, `Retorno ao Router`), sem dependência de seções legadas no corpo.
  - Suíte global de testes preservada com **136 testes**, 100% verde (`pytest` em 11.65s).

---

