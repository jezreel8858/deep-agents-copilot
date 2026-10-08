---
title: Guia Rápido de Git Commits e Governança
description: Referência rápida de Conventional Commits e governança Git para desenvolvedores, alinhada à SSOT normativa git-governance.
type: reference
status: active
ssot_reference: .github/skills/git-governance/SKILL.md
last_updated: 2026-10-08
---

# Guia Rápido de Git Commits e Governança

> **SSOT Normativa do Repositório**:  
> A especificação técnica canônica e obrigatória para agentes de IA e automações de CI/CD reside na skill [`.github/skills/git-governance/SKILL.md`](../../.github/skills/git-governance/SKILL.md) e em seus módulos em [`.github/skills/git-governance/references/`](../../.github/skills/git-governance/references/).  
> Este documento é o **guia prático de consulta rápida para desenvolvedores humanos**, assegurando alinhamento imediato aos padrões do projeto sem divergências normativas.

---

## 1. Mapa de Referências Normativas (SSOT)

Para detalhes normativos e regras automatizadas consumidas por ferramentas e agentes, consulte diretamente a documentação especializada:

| Necessidade | Módulo Canônico | Descrição |
|---|---|---|
| Formatos A/B, tipos e atomicidade | [`commit-formats.md`](../../.github/skills/git-governance/references/commit-formats.md) | Regras completas de estrutura, quebra de contratos e trailers. |
| Template de PR e Rollback | [`pr-template.md`](../../.github/skills/git-governance/references/pr-template.md) | Estrutura obrigatória de PR com plano de reversão e checklist. |
| Avaliação de Risco e Blast Radius | [`risk-matrix.md`](../../.github/skills/git-governance/references/risk-matrix.md) | Matriz de classificação de risco e raio de impacto da alteração. |
| Prevenção contra Vazamento de Segredos | [`secrets-guardrail.md`](../../.github/skills/git-governance/references/secrets-guardrail.md) | Defesa em 3 camadas, regexes proibidas e bloqueio em CI/agentes. |
| Registro no Histórico de Mudanças | [`changelog.md`](../../.github/skills/git-governance/references/changelog.md) | Padrão Keep a Changelog 1.1 e mapeamento semântico de commits. |

---

## 2. Anatomia da Mensagem de Commit

Todo commit no repositório segue o padrão **Conventional Commits**:

```text
<tipo>(<escopo>): <resumo curto no imperativo>

- Descrição narrativa do que foi alterado e do porquê (wrap em máx. 72 colunas).

Arquivos modificados / adicionados / removidos:
- caminho/do/Arquivo.ts — o que mudou e por quê

Como validar:
- <comando executável de teste ou verificação>

Rodapé opcional (Trailers):
BREAKING CHANGE: <descrição do impacto>
Closes #123
```

### 2.1 Regras de Redação do Título

1. **Idioma**: sempre em **Português do Brasil (PT-BR)**.
2. **Resumo (Título)**:
   - Verbo no **imperativo**: `adiciona`, `corrige`, `atualiza`, `remove`, `refatora`, `migra`, `documenta`, etc.
   - **Sem ponto final** ao término do título.
   - Limite estrito de **72 caracteres**.
3. **Escopo**: substantivo conciso em `kebab-case` indicando o módulo, camada ou domínio afetado (ex.: `auth`, `api`, `deps`, `governance`, `ui`).
4. **Breaking Changes**: utilize `!` antes dos dois pontos (ex.: `feat(api)!: altera schema da rota /login`) **ou** declare o trailer `BREAKING CHANGE:` no rodapé — nunca utilize ambos simultaneamente.

### 2.2 Estrutura do Corpo e Trailers

- **Wrap de 72 colunas**: limite cada linha a 72 caracteres para legibilidade no `git log`.
- **Foco no Porquê**: contextualize a motivação da mudança, não apenas a listagem técnica de arquivos.
- **Trailers válidos**: dados reais como `BREAKING CHANGE: <desc>`, `Closes #123`, `Refs #456`, `Co-authored-by: Nome <email>`.

---

## 3. Tipos de Commit Válidos

### 3.1 Tabela de Tipos Convencionais

| Tipo | Quando usar |
|---|---|
| `feat` | Nova funcionalidade voltada ao usuário ou sistema |
| `fix` | Correção de bug com alteração de comportamento externo |
| `refactor` | Reestruturação de código sem alteração funcional externa |
| `test` | Criação, ajuste ou exclusão de suítes de testes |
| `docs` | Alterações exclusivas em documentação (`.md`, JSDoc, comentários) |
| `chore` | Manutenções gerais (tarefas auxiliares, dependências, configs, dead code) |
| `perf` | Melhoria mensurável de performance ou consumo de recursos |
| `build` | Alterações no sistema de build (`package.json`, `Dockerfile`, `pom.xml`) |
| `ci` | Alterações em pipelines de integração contínua e automações |
| `style` | Ajustes de formatação pura (espaçamentos, lint) sem impacto de lógica |
| `revert` | Reversão explícita de commit anterior |
| `wip` | Trabalho em progresso temporário (**vedado merge direto na branch principal**) |

### 3.2 Classificação de Exclusões

Ao remover código ou arquivos, classifique com o tipo semântico preciso:

| Situação da exclusão | Tipo recomendado |
|---|---|
| Classe/módulo substituído por novo design | `refactor` |
| Código morto, arquivo órfão ou legado sem uso | `chore` |
| Teste unitário ou suíte duplicada/desnecessária | `test` |
| Arquivo de configuração ou dependência obsoleta | `chore` |
| Remoção intencional de funcionalidade com quebra | `feat` (com `BREAKING CHANGE`) |
| Remoção de elemento deprecado pós-janela de migração | `refactor` |

---

## 4. Atomicidade e Regras de Escopo

- **Uma intenção lógica por commit**: cada commit deve representar uma unidade indivisível e coerente.
- **O Teste do "e"**: se a mensagem precisa da conjunção "e" para juntar frentes não correlatas (ex.: "adiciona rota de login *e* corrige bug no carrinho"), divida o trabalho em múltiplos commits.
- **Separação de Camadas e Monorepos**:
  - Evite misturar commits de documentação (`docs`) com código funcional (`feat`/`fix`), a menos que a documentação componha a entrega obrigatória da funcionalidade.
  - Em projetos desacoplados (ex.: `apps/web` e `services/api`), gere commits com escopos dedicados por aplicação.

---

## 5. Formatos de Mensagem

Conforme definido na skill [`commit-formats.md`](../../.github/skills/git-governance/references/commit-formats.md), escolha o formato proporcional ao escopo:

### 5.1 Formato A: Commits Simples (1 a 5 arquivos)

Recomendado para a maioria das alterações cotidianas:

```text
tipo(escopo): resumo conciso no imperativo

- Explicação objetiva do contexto e impacto da alteração.

Arquivos modificados:
- caminho/do/Arquivo.ts — o que mudou e por quê

Como validar:
- npm test -- path/to/arquivo.spec.ts
```

### 5.2 Formato B: Commits Complexos (6+ arquivos ou múltiplas frentes)

Recomendado para grandes refatorações, migrações de arquitetura ou novos módulos. Agrupe os arquivos por responsabilidade lógica usando marcadores visuais:

```text
tipo(escopo): resumo consolidado no imperativo

- Descrição narrativa do objetivo e da abordagem adotada.
- Referência a plano ou issue quando aplicável (ex.: Plano de Modernização).

─── Novos arquivos ──────────────────────────────────────
  [Domínio / Camada]
  - caminho/NovoComponente.ts — responsabilidade da nova classe

─── Arquivos modificados ────────────────────────────────
  [Infraestrutura / Serviços]
  - caminho/ServicoExistente.ts — delega execução para novo componente

─── Arquivos removidos ──────────────────────────────────
  [Legado / Obsoleto]
  - caminho/ComponenteAntigo.ts — removido; substituído por NovoComponente.ts

─── Breaking changes ────────────────────────────────────
  (omitir caso não haja quebra de contrato)

Como validar:
- npm run test:unit
```

> **Regra de Ouro para Arquivos Removidos:** nunca liste uma remoção sem declarar o **motivo** e o **substituto** (se houver).

---

## 6. Instruções de Validação ("Como validar")

O bloco `Como validar:` é **obrigatório** em commits dos tipos `feat`, `fix` e `refactor`.
- Forneça o comando exato em linha de comando para reprodução rápida.
- Exemplos:
  - `npm test -- src/auth/auth.service.spec.ts`
  - `mvn -pl modulo-core test -Dtest=UsuarioServiceTest`

---

## 7. Guardrails de Governança e Segurança

1. **Prevenção Absoluta contra Vazamento de Segredos (R-010 / R-044)**:
   - Nunca inclua senhas, tokens de API, chaves privadas ou certificados no histórico do Git.
   - Consulte o módulo [`secrets-guardrail.md`](../../.github/skills/git-governance/references/secrets-guardrail.md) para detalhes de proteção e remediação em caso de incidente.
2. **Autonomia de Agentes de IA (R-031)**:
   - Assistentes virtuais e agentes de IA **nunca executam `git commit` ou `git push` de forma autônoma**.
   - O agente gera e propõe a mensagem padronizada; a revisão, confirmação e execução cabem exclusivamente ao desenvolvedor humano.
3. **Rebase e Merge**:
   - Commits `wip:` **nunca devem entrar na branch principal**; faça squash ou reword antes da abertura do PR.
   - Evite rebase destrutivo em branches públicas/compartilhadas.
   - Utilize squash merge para features pequenas (1 a 3 commits) e merge commit para releases consolidadas.

---

## 8. Aplicação Segura no Terminal

Para preservar quebras de linha e blocos estruturados sem problemas de escape no terminal, aplique o commit via bloco heredoc:

```bash
git commit -F - << 'EOF'
feat(auth): adiciona validação de token jwt expirado

- Intercepta requisições não autenticadas e aciona o fluxo de refresh automático.

Arquivos modificados:
- src/auth/jwt-interceptor.ts — valida expiração antes do dispatch

Como validar:
- npm test -- src/auth/jwt-interceptor.spec.ts
EOF
```
