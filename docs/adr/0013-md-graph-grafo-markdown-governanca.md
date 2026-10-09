---
id: ADR-0013
title: "md-graph: Grafo de Conhecimento e Validação Determinística de Links em Markdown de Governança"
status: Proposto
date: 2026-10-08
decision-makers:
  - governance-maintainer
  - docs-engineer
  - tech-solution-architect
consulted:
  - agent-auditor
  - codegraph-engine
informed:
  - adr-sentinel
  - pr-gatekeeper
type: architectural-decision
diataxis: explanation
---

# ADR-0013: md-graph: Grafo de Conhecimento e Validação Determinística de Links em Markdown de Governança

> **Status**: Proposto (aguardando implementação)  
> **Data de Referência**: 2026-10-08  
> **Área / Módulo**: `docs/adr`, `.github/agents`, `.github/skills`, `.github/prompts`, `tools/governance_sync`, CI (`routing-quality-gate.yml`)  
> **Origem**: Ausência de checagem determinística de links e ausência de grafo de integridade referencial entre artefatos de governança (R-004, R-005, R-015, R-033, R-040)

---

## 1. Contexto e Declaração do Problema

O ecossistema `deep-agents-copilot` possui mais de 85 agentes especializados, dezenas de skills governadas, atalhos de prompts, ADRs e especificações técnicas documentadas inteiramente em Markdown. Enquanto a estrutura de código-fonte de aplicação é analisada via AST e grafos de símbolos pelo `@optave/codegraph`, a teia documental de governança enfrenta desafios críticos de validação automatizada:

1. **Ausência de Checagem Determinística de Links:** Não há ferramenta determinística integrada à esteira de CI validando se links relativos (`[doc](../outro.md)`) ou âncoras internas (`#secao`) apontam para alvos existentes ou se tornaram links quebrados após refatorações de nomenclatura.
2. **Documentos e Artefatos Órfãos:** Não existe mecanismo automatizado para identificar artefatos Markdown órfãos — arquivos existentes no repositório que deixaram de ser referenciados ou catalogados em `catalog.yaml`, `.index.json` ou `routing-graph.yaml`.
3. **Ausência de Grafo de Backlinks e Integridade Cruzada:** Falta visibilidade estruturada de dependências reversas (backlinks) entre nós heterogêneos do catálogo:
   - Qual agente depende de qual skill?
   - Quais ADRs fundamentam determinado agente ou protocolo operacional?
   - Há divergência entre as declarações de frontmatter (`source_docs`, `source_docs_lazy`, `tools`) e a existência real dos arquivos no disco?
4. **Inexistência de Biblioteca Pronta no Mercado:** Nenhuma biblioteca off-the-shelf pronta cobre simultaneamente a validação offline rápida de links e a semântica específica de entidades de governança de IA (`agents`, `skills`, `prompts`, `docs`, `ADRs`) e suas arestas de dependência cruzada declaradas no catálogo.

---

## 2. Decisão Arquitetural: Adoção Parcial e Híbrida (lychee + md-graph)

Propõe-se uma estratégia em duas camadas complementares que estende a ADR-0012 (`governance_sync` toolkit), evitando o acoplamento excessivo e garantindo determinismo estrito sem dependência de LLMs ou serviços externos.

### 2.1. Camada 1: Link Checking Estático com `lychee` (Offline, CI)

Propõe-se adotar o **`lychee`** como validador estático de links e âncoras para o acervo de Markdown:
- **Modo Offline:** Execução local estrita com a flag `--offline`, bloqueando chamadas HTTP externas e assegurando tempo de execução inferior a 2 segundos em esteiras de CI.
- **Integração:** Inclusão como step bloqueante nos workflows de qualidade de governança (`routing-quality-gate.yml`).
- **Instalação no Ambiente Local:** Instalação oficial via PyPI:
  ```bash
  pip install lychee-bin
  ```
  *(Distribuído sob licença Apache-2.0 OR MIT; não confundir com o pacote legatário `lychee`, gerador de blog estático. A instalação via `winget` encontra-se bloqueada por Política de Grupo no ambiente operacional).*
- **Medição Prática e Lições Aprendidas:**
  - Em medição anterior, a inclusão indevida de `--base-url` e `--root-dir` gerou 331 falsos positivos por falha de parametrização conceitual. A flag `--include-wikilinks` exige `--base-url`, mas o repositório adota links Markdown relativos padronizados e não wikilinks (confirmado via teste com 0 wikilinks em .github e docs; as 5 ocorrências de `[[` encontradas são trechos de código/tipagem em skills de teste).
  - **Diretriz de parametrização:** executar exclusivamente `lychee --offline --no-progress --format compact .github docs` (SEM `--base-url`, SEM `--root-dir` e SEM `--include-wikilinks`).
  - **Medição real de baseline:** 710 links analisados (413 únicos), 342 OK, 0 erros de caminhos relativos (8 erros iniciais sanados), 366 excluídos, concluído em 1,77s.

### 2.2. Camada 2: Utilitário Próprio Futuro `md-graph` (Urgência Reduzida — Semântica de Governança)

Uma vez que o `lychee` já cobre de forma completa e instantânea (< 2s) a checagem sintática de links e âncoras locais em CI, a urgência de desenvolvimento do `md-graph` foi significativamente reduzida. O utilitário **`md-graph`** seria reservado exclusivamente para necessidades semânticas avançadas que extrapolam a sintaxe de links (cálculo de backlinks reversos, identificação de artefatos órfãos não catalogados e validação cruzada de consistência entre `agent` ↔ `skill` ↔ `catalog.yaml`), operando como extensão complementar ao `governance_sync` (ADR-0012) em Python ou Node.js (`unified`/`remark`):

1. **Fonte Canônica da Verdade:** O arquivo `catalog.yaml` (em conjunto com `.index.json`) rege as entidades oficiais do ecossistema (R-005, R-015, R-040).
2. **Modelo de Grafo Determinístico:**
   - **Nós (Nodes):** `agents` (`.github/agents/*.agent.md`), `skills` (`.github/skills/*/SKILL.md`), `prompts` (`.github/prompts/*.prompt.md`), `docs` (`docs/**/*.md`), `ADRs` (`docs/adr/*.md`).
   - **Arestas (Edges):** Hiperlinks Markdown (`[texto](caminho)`), backlinks bidirecionais computados, metadados estruturados de frontmatter YAML (`source_docs`, `source_docs_lazy`, `tools`), e relações relacionais declaradas em `catalog.yaml` (`agents.<id>.skills`).
3. **Contrato de Interface CLI:**
   - Padronizado com o `governance_sync` (ADR-0012): execução sem flags ou com `--check` opera em modo fail-safe (read-only), emitindo exit code `0` para conformidade e exit code `1` em caso de drift referencial, links órfãos ou inconsistência no catálogo.
   - Suporte adicional às flags `--dry-run` e `--apply` para refatorações automáticas seguras de links relativos.

---

### 2.3. Comparativo de Alternativas Avaliadas

| Solução / Abordagem | Veredito | Justificativa Arquitetural |
|---|---|---|
| **`lychee`** | **Adotado Parcialmente (Camada 1)** | Escrito em Rust, extremamente rápido, excelente suporte a validação local offline (`--offline`). Limitação: desconhece a semântica das entidades de governança do repositório. |
| **`markdown-link-check`** | **Rejeitado** | Baseado em Node.js, tempo de execução significativamente superior ao `lychee`, suporte offline menos maduro e histórico de falsos positivos em links locais relativos. |
| **`remark` / `unified`** | **Candidato de Implementação (`md-graph`)** | Ecossistema AST para Markdown flexível e extensível. Permite construir o parser de nós e arestas caso se opte pelo ecossistema JavaScript/TypeScript. |
| **`IWE` (Integrated Writing Env.)** | **Rejeitado** | Focado em edição assistida e PKM pessoal. Forte acoplamento com interface de usuário e inviável para esteiras headless de CI. |
| **`Graphify`** | **Sob Observação (Reavaliar Futuramente)** | Ferramenta emergente de visualização de grafos documentais. Deve ser reavaliada após a maturidade do `md-graph` para geração de diagramas exploratórios. |
| **`GraphRAG` / `LlamaIndex` + `Neo4j`** | **Rejeitado Enfaticamente** | Abordagens baseadas em LLM, inferência probabilística e bancos orientados a grafos pesados. Totalmente incompatíveis com validação determinística de CI (R-008, R-050): estocasticidade, custo desnecessário de tokens e latência proibitiva. |
| **`Microsoft Agent Governance Toolkit`** | **Não Adotado (Referência Conceitual)** | Focado em governança em tempo de execução de agentes em produção corporativa (telemetria, firewalls de prompt de runtime). O projeto atual governa catálogo estático, contratos e templates de design de IA; mantido como referência conceitual. |

---

## 3. Consequências

### Positivas:
- **Detecção Precoce de Drift:** Bloqueio determinístico em PRs (`exit code 1`) para links mortos ou artefatos renomeados sem sincronização referencial.
- **Análise de Impacto Rastreável:** Possibilidade de consultar o grafo para identificar instantaneamente quais agentes e skills dependem de um documento antes de sua alteração ou depreciação.
- **Sincronia Estrita de Catálogo:** Garantia de que nenhum agente ou skill referencie artefatos inexistentes no sistema de arquivos.

### Negativas / Débito Técnico Planejado:
- **Manutenção de Tooling Adicional:** Necessidade de sustentar a evolução do script `md-graph` alinhada a futuras modificações no schema dos agentes e skills.
- **Dois Passos de Validação:** Execução separada do `lychee` (sintaxe de links) e do `md-graph` (semântica do catálogo).

### Riscos, Incertezas e Mitigações:
- **Falsos Positivos do `lychee`:** Risco mitigado pela medição empírica realizada (zero falsos positivos com a parametrização canônica: sem `--base-url` e sem `--root-dir`).
- **Custo de Manutenção do Parser:** Risco de complexidade excessiva no motor AST do `md-graph`. *Mitigação*: Iniciar com implementação mínima em Python baseada no `core.py` do `governance_sync`.
- **Licenciamento Corporativo de Dependências:** Conformidade atendida para o `lychee` (licença dupla Apache-2.0 / MIT via `lychee-bin` no PyPI); pacotes futuros do `md-graph` serão restritos a licenças permissivas MIT/Apache-2.0.
