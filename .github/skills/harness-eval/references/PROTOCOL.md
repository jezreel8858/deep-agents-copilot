# Protocolo de Avaliação de Harness (harness-eval) — 11 Passos

> Procedimento detalhado consumido por `.github/skills/harness-eval/SKILL.md` § 2. Carregado sob demanda (`source_docs_lazy`).

## Passo 1 — Delimitação do Harness-Alvo
Identificar precisamente o artefato sob avaliação: prompt/system message, tool-set habilitado, hooks ativos e versão exata (hash/commit) do harness-alvo.

## Passo 2 — Extração de Claims Testáveis
Extrair do prompt/harness-alvo todas as afirmações comportamentais testáveis (ex.: "nunca edita arquivos fora de X", "sempre delega Y para Z"). Validar estrutura contra `claims.schema.json`.

## Passo 3 — Seleção da Trilha (Track A/B/C)
Selecionar a trilha conforme o objetivo: A (regressão), B (calibração contra baseline) ou C (auditoria dual-judge de conformidade).

## Passo 4 — Definição de Casos Canônicos
Definir casos de teste representativos do uso típico (caminho feliz) para cada claim.

## Passo 5 — Definição de Casos de Borda
Definir casos de borda/adversariais que testem os limites de cada claim (ambiguidade, tentativa de violação, input malformado).

## Passo 6 — Execução Controlada
Executar o harness-alvo contra todos os casos definidos em ambiente controlado e determinístico (seed/temperatura fixa quando aplicável).

## Passo 7 — Captura Estruturada de Evidência
Capturar transcript completo, tool calls emitidos, outputs e metadados de execução (nunca confiar em memória/resumo pós-hoc).

## Passo 8 — Avaliação Dual-Judge
Submeter cada par (claim, evidência) a dois juízes LLM independentes usando os prompts de `judge-prompts.md`. Cada juiz emite veredito + justificativa.

## Passo 9 — Cálculo de Score de Conformidade
Agregar vereditos por claim: concordância entre os dois juízes = score direto; divergência = sinalizado para desempate humano.

## Passo 10 — Desempate Humano (Quando Aplicável)
Casos divergentes são revisados por um humano com acesso à evidência bruta e às justificativas de ambos os juízes antes do veredito final.

## Passo 11 — Registro Auditável do Resultado
Registrar o veredito final, score por claim, evidência e decisão de desempate (se houve) em artefato auditável — nunca aprovar harness por impressão subjetiva sem este registro (R-044).
