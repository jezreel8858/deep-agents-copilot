# Glossário Técnico — harness-eval

| Termo | Definição |
|---|---|
| **Harness** | Tudo ao redor do modelo que o transforma em agent: tools, system prompt, gestão de contexto, permissões e hooks. |
| **Claim** | Afirmação comportamental testável declarada por um prompt/harness (ex.: "nunca excede 3 tool calls"). |
| **Dual-Judge** | Técnica de avaliação com dois juízes LLM independentes avaliando o mesmo par (claim, evidência) para reduzir viés de avaliador único. |
| **Track A (Regressão de Instruções)** | Trilha de validação de que uma alteração de prompt não quebrou comportamento previamente aprovado. |
| **Track B (Calibração de Prompts)** | Trilha de comparação de uma variante experimental contra um baseline aprovado. |
| **Track C (Auditoria Dual-Judge)** | Trilha de validação formal de claims contra evidência observável via dois juízes independentes. |
| **Evidência Observável** | Dado bruto de execução (transcript, tool calls, outputs) — nunca resumo ou impressão subjetiva pós-hoc. |
| **Desempate Humano** | Intervenção humana obrigatória quando os dois juízes divergem no veredito de um claim. |
| **Score de Conformidade** | Resultado agregado por claim após avaliação dual-judge (aprovado/reprovado/divergente). |
