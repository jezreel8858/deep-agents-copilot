# [Papel Especialista / Stack Detectada]

> Template canônico reutilizável de saída do WORKFLOW-PROMPT-SYNTHESIS e comando /craft-prompt.
> Finalidade: Consumo exclusivo downstream por agents e workflows em uma nova sessão limpa (nunca resposta final direta de negócio ao usuário).

## Contexto do Projeto
<!-- Dados estáticos da aplicação, convenções arquiteturais, dependências e diretrizes para alinhamento com Prompt Caching -->

## Arquivos e Referências Grounded
<!-- Caminhos reais no repositório verificados deterministamente via @code-knowledge-graph e componentes irmãos canônicos homologados -->
- `caminho/do/arquivo_1.ext`
- `caminho/do/arquivo_2.ext`
- Componente irmão canônico homologado: `caminho/do/irmao_canonico.ext`

## Tarefa
<!-- Descrição clara e concisa do objetivo a ser executado no novo chat pelo agente especialista -->

## Critérios de Aceitação
<!-- Checklist objetivo e verificável em formato INVEST/Gherkin -->
- [ ] Critério 1: <condição verificável>
- [ ] Critério 2: <condição verificável>

## Restrições e Não-Escopo
<!-- Restrições negativas, o que NÃO fazer, convenções obrigatórias (ex.: R-046 / Single-Turn Batching) e eventuais lacunas residuais declaradas -->
- **Não-Escopo Negativo**: <o que expressamente NÃO deve ser alterado>
- **Governança de Lote**: Injeção compulsória de R-046 (Single-Turn Batching, diffs cirúrgicos, dry-run prévio em memória).
- **Lacunas Residuais Declaradas**: <pontos em aberto após o teto de 10 rodadas de elicitação, se houver>

## Protocolo de Execução Recomendado
<!-- Passos operacionais recomendados para o agente executor na nova sessão limpa -->
1. Inspecionar os arquivos grounded e validar premissas em memória.
2. Planejar as modificações em lote cirúrgico.
3. Executar as alterações conforme os critérios de aceitação.
4. Validar compilação e testes antes da entrega.

## Formato de Saída Esperado
<!-- Formato conciso de entrega sem narrativa ociosa -->
