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
- **Conteúdo Mínimo Obrigatório** (conforme `.github/skills/documentation-writing-patterns/SKILL.md` § 2.1 — Categoria IMPLEMENTAÇÃO):
  1. Front-matter YAML de implementação canônico (`status: draft`, `date`, `autor`, `workflow`, `related-planning-doc: <path-do-doc-de-planejamento-aprovado>`, `progress: 0`) — obrigatório R-064.
  2. Referência explícita ao Plano de Planejamento aprovado correspondente (`related-planning-doc`).
  3. Checklist GFM unificado obrigatório no formato `- [ ] <descrição> {paralelizavel: bool, responsavel: "<agent>"}` com indicador agregado `Progresso: N/M tarefas concluídas`.
  4. Lista exata dos arquivos a serem criados, alterados ou removidos.
  5. Sequência cronológica de alterações (ordem de execução em lote / Plan-Then-Batch, R-059).
  6. Abordagem técnica de baixo nível e diffs conceituais planejados.
  7. Riscos de regressão e matriz de blast radius.
  8. Estratégia de rollback e plano de contingência por etapa (R-031 / R-050.2).
  9. Checklist Defensivo Pré-Code-Review obrigatório com validações de segurança prévias à submissão.

## 🔒 Checklist Defensivo Pré-Code-Review

Todo documento de implementação técnica DEVE incorporar ao final o checklist defensivo com os seguintes itens obrigatórios:
- [ ] **Sanitização & Validação de Borda**: Validação estrita de tipos, tamanhos e formatos em todos os pontos de entrada e parâmetros externos.
- [ ] **Zero Hardcoded Secrets**: Ausência absoluta de credenciais, tokens de API, senhas ou certificados codificados no código ou fixtures.
- [ ] **Logging & Dados Sensíveis**: Mascaramento ou omissão de PII, senhas, tokens e dados sensíveis em logs de depuração e traces.
- [ ] **Controle de Acesso & Autorização**: Validação de escopos, papéis e permissões no nível de serviço/controlador para evitar broken object level authorization (BOLA/IDOR).
- [ ] **Tratamento Seguro de Falhas**: Exceções tratadas sem expor stacktraces ou dados internos ao usuário final, mantendo estado consistente.
- [ ] **Cobertura de Testes Defensivos**: Testes cobrindo fluxos de erro, inputs maliciosos/inválidos e limites de contorno.
