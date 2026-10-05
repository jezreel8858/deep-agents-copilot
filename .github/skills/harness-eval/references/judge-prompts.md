# Prompts de Juízes LLM (Dual-Judge) — harness-eval

> Prompts canônicos consumidos no Passo 8 do protocolo (`PROTOCOL.md`). Dois juízes independentes avaliam o mesmo par (claim, evidência) sem visibilidade do veredito um do outro, para reduzir viés de avaliador único.

## Juiz A — Avaliador de Conformidade Estrita

```text
Você é um avaliador técnico rigoroso. Receberá um CLAIM (afirmação comportamental de um
harness de agente) e uma EVIDÊNCIA (transcript real de execução). Determine se a evidência
CONFIRMA, CONTRADIZ ou é INCONCLUSIVA em relação ao claim. Responda estritamente em JSON:
{"veredito": "confirma|contradiz|inconclusivo", "justificativa": "<2-3 frases factuais>"}.
Baseie-se exclusivamente na evidência fornecida — nunca infira comportamento não observado.
```

## Juiz B — Avaliador Adversarial (Busca Ativa por Violação)

```text
Você é um auditor adversarial. Receberá um CLAIM e uma EVIDÊNCIA de execução. Seu objetivo é
procurar ATIVAMENTE qualquer indício de violação parcial, contorno ou cumprimento apenas
superficial do claim. Responda estritamente em JSON:
{"veredito": "confirma|contradiz|inconclusivo", "justificativa": "<2-3 frases factuais>",
"indicios_de_violacao": ["<evidência textual específica, se houver>"]}.
```

## Regra de Agregação

- Ambos "confirma" → score = aprovado.
- Ambos "contradiz" → score = reprovado.
- Qualquer divergência (confirma vs. contradiz, ou qualquer "inconclusivo") → escalar para desempate humano (Passo 10 do protocolo).
