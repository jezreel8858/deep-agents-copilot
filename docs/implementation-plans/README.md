# Planos de Implementação Técnica (R-064)

Diretório canônico para persistência versionada dos **Planos de Implementação Técnica Detalhada** gerados imediatamente antes de qualquer mutação de código, conforme a norma **R-064**.

## Convenção de Nomenclatura

```
docs/implementation-plans/<AAAAMMDD>-<workflow>-<identificador-curto>.md
```

- `<AAAAMMDD>`: Data da elaboração no formato ISO básico (ex.: `20260401`).
- `<workflow>`: Identificador do workflow canônico em minúsculas sem prefixo `workflow-` (ex.: `feature-development`, `bug-fix`, `refactoring`, `governance-maintenance`, `dependency-vulnerability-remediation`, `framework-migration`).
- `<identificador-curto>`: Slug kebab-case correspondente ao Plano de Planejamento aprovado.

## Propósito e Autoria

- **Quando é gerado**: Imediatamente após a aprovação humana do Plano de Planejamento e **ANTES de qualquer mutação de código** (`insert_edit_into_file`, `replace_string_in_file`, `create_file` ou scripts mutativos em sandbox).
- **Autoria**: 
  - Quando o workflow possui stack de domínio identificada: o respectivo especialista **`<stack>-arch-advisor`** (Angular, Spring Boot, Spring Reactive, EJB, Struts, Python — perfil Read-Only) estrutura o plano técnico detalhado.
  - Em workflows agnósticos ou transversais (Governance, Dependency Vulnerability, Framework Migration, Technical Analysis): o especialista analítico responsável pelo planejamento técnico daquele workflow assume a autoria.
- **Materialização e Aprovação**: O Orquestrador Raiz materializa o arquivo neste diretório e submete ao usuário via `ask_questions` para aprovação prévia obrigatória. Nenhuma mutação de código pode ser iniciada com o plano pendente ou sob ajuste solicitado.
- **Conteúdo Mínimo Obrigatório**:
  1. Referência explícita ao Plano de Planejamento aprovado correspondente.
  2. Lista exata dos arquivos a serem criados, alterados ou removidos.
  3. Sequência cronológica de alterações (ordem de execução em lote / Plan-Then-Batch, R-059).
  4. Abordagem técnica de baixo nível e diffs conceituais planejados.
  5. Riscos de regressão e matriz de blast radius.
  6. Estratégia de rollback e plano de contingência por etapa (R-031 / R-050.2).
