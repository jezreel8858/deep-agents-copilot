# Riscos Aceitos e Pendências Humanas

## Riscos aceitos (decisão humana)

| Risco | Decisão | Mitigação |
| :--- | :--- | :--- |
| Daemon mvnd padrão (órfão, RAM, arquivos travados no Windows) | Aceito (ADR-1) | `--stop`, stop em falha/timeout, `DAC_MVN_STOP_ON_EXIT`, heap, override `wrapper|auto`, fallback `[FALLBACK]` |
| `./mvnw` do alvo executa código arbitrário | Aceito com política | Só em `wrapper|auto` ou `DAC_ALLOW_TARGET_WRAPPER=1`; senão exit 16 |
| Supply chain dos binários | Mitigado | SHA-256 obrigatório, hosts oficiais, tmp + `mv` atômico, exit 13 sem fallback |
| Alvo Python com dependências próprias | Limitação documentada | Usar ambiente do alvo |

## Pendências humanas (gate antes do merge)

- [ ] Revisar os SHA-256 do `tools.lock` (`[mvnd]` 1.0.6 e `[uv]` 0.12.24) contra as fontes oficiais; nenhum valor pode ser placeholder.
- [ ] Revisar o timeout padrão de 900s (`DAC_MVN_TIMEOUT`/`DAC_TEST_TIMEOUT`).
- [ ] Registrar o resultado da validação V1 (plano Python, T4).
- [ ] CI com `setup-uv` e uso opcional de `uv export` ficam fora deste commit.

## Higiene (R-038/R-043/R-044)

Arquivos versionados não podem conter caminho de máquina, usuário ou nome de projeto local; usar `<workspace>`, `<HOME>`, `[PROJETO-ALVO]`.
