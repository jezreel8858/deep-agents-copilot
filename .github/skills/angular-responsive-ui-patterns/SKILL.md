---
name: angular-responsive-ui-patterns
description: >-
  Diretrizes para responsividade em Angular: mobile-first, breakpoints,
  layout fluido, container queries, imagens responsivas, acessibilidade e
  validação em múltiplas larguras de tela.
tier: 2
category: quality
triggers:
  - "responsividade angular"
  - "angular responsivo"
  - "layout mobile first angular"
  - "breakpoints angular"
  - "container queries angular"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/frontend/angular/angular-router.agent.md
tools: []
---

# Angular Responsive UI Patterns

## Quando Usar

- Quando houver análise de layout que quebra em diferentes larguras de tela.
- Quando a decisão envolver mobile-first, breakpoints ou container queries.
- Quando for necessário revisar imagens, tipografia, espaçamento ou densidade visual.
- Quando a recomendação precisar considerar acessibilidade e interação em telas pequenas.

## Padrões Recomendados

| Pilar | Diretriz | Evidência mínima |
|---|---|---|
| Mobile-first | Projetar a interface para a menor largura crítica e ampliar progressivamente | Regras claras para comportamento em mobile, tablet e desktop |
| Layout fluido | Preferir grids e flexbox com medidas relativas, evitando larguras rígidas desnecessárias | Trechos de SCSS e templates com unidades flexíveis |
| Breakpoints | Definir pontos de quebra com base em conteúdo e não em dispositivos específicos | Lista de breakpoints justificada por comportamento real |
| Container queries | Usar quando o componente depende do tamanho do próprio contêiner | Evidência de componentes reutilizáveis em contextos diferentes |
| Imagens responsivas | Ajustar srcset, sizes, aspect ratio e prioridade de carregamento | Diretriz para LCP, corte e resolução por viewport |
| Legibilidade | Preservar contraste, espaçamento, line-height e hierarquia visual em telas pequenas | Critérios mínimos de leitura e escaneabilidade |
| Interação touch | Garantir alvos clicáveis e espaçamentos adequados para toque | Tamanho mínimo de alvo e distância entre ações críticas |
| Formulários | Reorganizar campos e ações para reduzir fricção em telas menores | Ordem dos campos, agrupamento e fallback para mensagens de erro |
| Validação multi-viewport | Revisar cenários críticos em múltiplas larguras antes de aprovar a recomendação | Screenshots, checklist ou evidências comparativas por viewport |

## Checklist de Revisão

- [ ] A experiência foi pensada primeiro para a menor largura relevante.
- [ ] O layout evita overflow horizontal e truncamento crítico.
- [ ] A hierarquia visual permanece clara em telas pequenas.
- [ ] Os pontos de quebra têm justificativa ligada ao conteúdo.
- [ ] Imagens e mídias possuem comportamento adequado por viewport.
- [ ] Alvos de toque e ações primárias continuam acessíveis.
- [ ] Há validação explícita em mais de uma largura de tela.

## Anti-padrões

- ❌ Fixar larguras em pixels sem necessidade funcional.
- ❌ Resolver responsividade apenas com "esconde e mostra" conteúdo importante.
- ❌ Definir breakpoints por nomes de dispositivos em vez de comportamento.
- ❌ Ignorar container queries quando um componente é reutilizado em contextos variados.
- ❌ Aprovar layout sem validar mobile, tablet e desktop em fluxos críticos.

## Referências

- MDN Responsive Design: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Responsive_Design
- MDN Media Queries: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_media_queries
- MDN Container Queries: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_container_queries
- web.dev Responsive Images: https://web.dev/learn/images/
- Angular Style Guide: https://angular.dev/style-guide

