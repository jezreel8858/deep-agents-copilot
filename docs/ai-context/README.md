# AI Context — Governança e Binding de Adapters

> Documentação consolidada sobre descoberta progressiva, binding hierárquico e mecanismos de carregamento de instruções para IA neste ecossistema.

---

## 📋 Índice

| Arquivo | Propósito |
|---------|-----------|
| **`binding.md`** | Guia detalhado do binding hierárquico com adapters e mecanismo de descoberta |
| **`catalog.yaml`** | Manifest de binding — adapters de stack, governance_artefacts e discovery (compartilhado/commitado, **sem projetos** — R-043) |
| **`catalog.local.yaml`** | Overlay local de projetos (gitignored) — nunca commitado |
| **`catalog.local.yaml.example`** | Template do overlay local (tracked, sem dados reais) |
| **Este README** | Índice e entry point de contexto de IA |

> `catalog-base.yaml` e `binding-base.md` (templates genéricos de bootstrap) foram removidos —
> divergiam estruturalmente do `catalog.yaml`/`binding.md` reais (faltavam `governance_artefacts`
> e adapters adicionados organicamente) e o fluxo de "regeneração" que os consumia era destrutivo
> na prática. `binding-initializer.agent.md` agora gera o esqueleto inline, sem template externo.

---

## 🚀 Quick Start

### Para Desenvolvedores

1. **Etapa 1:** Ler [`CLAUDE.md`](../../CLAUDE.md) — regras globais (5 min)
2. **Etapa 2:** Ler [`.github/copilot-instructions.md`](../../.github/copilot-instructions.md) — operacional (3 min)
3. **Etapa 3:** Se trabalhando com backend Java → ler `.github/instructions/spring-boot-backend.instructions.md`
4. **Etapa 4:** Se trabalhando com frontend → ler `.github/instructions/angular-v21-frontend.instructions.md`

**Bônus:** Abra seu IDE — copilot carrega adapters **automaticamente** via `applyTo` glob!

### Para Arquitetos / Mantenedores

1. Entender o binding: [`binding.md`](binding.md) — hierarquia, adapters e discovery (10 min)
2. Revisar estrutura: [`catalog.yaml`](catalog.yaml)
3. Adicionar novo adapter (se necessário): seção "Adicionando Novo Adapter" abaixo
4. Sincronizar: `.github/instructions/README.md` + `catalog.yaml`

---

## 🔗 Mapa de Navegação

```
<repo>/
├── CLAUDE.md ......................... Regras globais de IA (CLAUDE.md)
├── .github/
│   ├── copilot-instructions.md ....... Operacional + Roteamento
│   └── instructions/
│       ├── README.md ................. Índice de adapters
│       ├── spring-boot-backend.instructions.md  ← Carrega em **/*.java
│       ├── angular-v21-frontend.instructions.md ← Carrega em **/*.ts
│       ├── python-backend.instructions.md       ← Carrega em **/*.py
│       ├── database.instructions.md             ← Carrega em **/*.sql
│       └── devops.instructions.md               ← Carrega em Dockerfile/K8s/CI
│
└── docs/
    └── ai-context/
        ├── README.md ................. Este arquivo
        ├── binding.md ................ Guia de binding hierárquico
        ├── catalog.yaml .............. Manifest de binding (compartilhado, sem projetos)
        ├── catalog.local.yaml ........ Overlay local de projetos (gitignored)
        └── catalog.local.yaml.example  Template do overlay local (tracked)
```

---

## 🏗️ Hierarquia de 3 Camadas

```
┌─────────────────────────────────┐
│ Camada 1: GLOBAL (Priority 100) │
│ CLAUDE.md + .github/copilot-... │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│ Camada 2: ADAPTER (Priority 50) │
│ .github/instructions/*.md       │
│ (applyTo glob patterns)         │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│ Camada 3: PROJETO (Priority 40) │
│ Local Overlay — catalog.local.yaml (R-043) │
└─────────────────────────────────┘
```

**Aplicação automática** via GitHub Copilot quando arquivo combina `applyTo` pattern.

---

## 📦 Adapters Convencionais Atuais

| Adapter | Stack | Aplica A |
|---------|-------|----------|
| `spring-boot-backend.instructions.md` | Java/Spring Boot | `**/*.java`, `pom.xml` |
| `angular-v21-frontend.instructions.md` | Angular 21 | `**/*.ts`, `**/*.js` |
| `python-backend.instructions.md` | Python Backend | `**/*.py`, `pyproject.toml` |
| `database.instructions.md` | Banco de Dados / Migrações | `migrations/**`, `**/*.sql` |
| `devops.instructions.md` | DevOps / CI-CD / Containers | `**/Dockerfile*`, `kubernetes/**` |

## 📋 Projetos Mapeados

> Projetos vivem exclusivamente em `catalog.local.yaml` (gitignored, R-043) — nunca neste README nem em `catalog.yaml`.
> Para ver a lista real desta máquina, consulte `docs/ai-context/catalog.local.yaml` (se existir localmente).

---

## ✨ Features

### ✅ Implementado

- [x] Binding de 3 camadas (Global → Stack → Projeto)
- [x] Frontmatter YAML com `applyTo` glob
- [x] Manifest declarativo (`catalog.yaml`)
- [x] Auto-discovery via IDE (GitHub Copilot, Cursor)
- [x] Local Overlay Pattern (R-043) — projetos nunca commitados
- [x] Documentação completa (`binding.md`)
- [x] Sem duplicação de regras (R-003)

### 🔮 Futuro

- [ ] Adapters por domínio adicional (Mobile, Security)
- [ ] Integração com git hooks para validação de frontmatter
- [ ] Dashboard de discovery e health check

---

## 📚 Documentação

👉 **[`binding.md`](binding.md)** — Guia de binding com:
- O que é binding e por que importa
- Hierarquia de 3 camadas
- Adapters disponíveis e como funcionam
- Gerenciamento de projetos (`/add-project-context`, `/del-project-context`)

👉 **[`catalog.yaml`](catalog.yaml)** — Manifest com:
- Bindings globais e adapters de stack
- `governance_artefacts` (routing-graph, evals)
- Discovery e fallback

👉 **Para Regras Globais**

👉 **[`CLAUDE.md`](../../CLAUDE.md)** — Regras normativas globais

👉 **[`.github/copilot-instructions.md`](../../.github/copilot-instructions.md)** — Operacional

👉 **[`.github/skills/project-scanner/SKILL.md`](../../.github/skills/project-scanner/SKILL.md)** — Diretrizes para scanner automático de projeto

---

## 🚀 Adicionando Novo Adapter

```bash
# 1. Criar arquivo
touch .github/instructions/novo-dominio.instructions.md

# 2. Adicionar frontmatter
cat > .github/instructions/novo-dominio.instructions.md << 'EOF'
---
applyTo: ["caminho/glob/**/*.ext"]
version: "1.0"
title: "Título do Adapter"
---

# Conteúdo aqui
EOF

# 3. Atualizar índice
# Editar .github/instructions/README.md — adicionar tabela

# 4. Atualizar manifest
# Editar docs/ai-context/catalog.yaml — adicionar entry em `adapters:`

# 5. Commit
git add .github/instructions/novo-dominio.instructions.md
git add .github/instructions/README.md
git add docs/ai-context/catalog.yaml
git commit -m "feat: adicionar adapter novo-dominio"
```

👉 Detalhes completos: seção "Adicionando Novo Adapter" de [`binding.md`](binding.md)

---

## 🔗 Referências

- **GitHub Docs:** [Copilot Custom Instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions)
- **Cursor Docs:** [Rules for AI](https://docs.cursor.com/context/rules-for-ai)
- **CLAUDE.md:** Governança global (CLAUDE.md)

---

## 📞 Suporte / Dúvidas

| Dúvida | Resposta |
|--------|----------|
| Como adicionar novo adapter? | Seção "Adicionando Novo Adapter" acima |
| IDE não carrega adapter | Verificar `applyTo` glob e frontmatter YAML |
| Qual a diferença entre camadas? | Seção "Hierarquia de 3 Camadas" acima |
| Como registrar um projeto? | `/add-project-context <caminho>` (grava em `catalog.local.yaml`) |

---

## 📈 Status

| Item | Status | Nota |
|------|--------|------|
| Binding de 3 camadas | ✅ Ativo | Consolidado no mercado (GitHub pattern) |
| Adapters atuais | ✅ 5 adapters | Backend Java, Frontend Angular, Backend Python, Database, DevOps |
| Local Overlay Pattern (R-043) | ✅ Ativo | Projetos em `catalog.local.yaml` (gitignored) |
| Discovery automática | ✅ IDE | GitHub Copilot, Cursor, Claude Code |
| Documentação | ✅ Completa | `binding.md` + este README |

---

**Última atualização:** 2026-09-01
**Versão do mecanismo:** 1.1 (pós-remoção de templates `catalog-base.yaml`/`binding-base.md`)
**Padrão consolidado:** GitHub Copilot (R-019)
