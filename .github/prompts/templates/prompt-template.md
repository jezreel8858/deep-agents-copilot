---
name: '<verbo>-<objeto>'
description: '<Ação imperativa em 1 linha — ex.: Analisa e refatora o arquivo ativo aplicando padrões de Clean Architecture>'
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['read_file', 'get_errors']
# Se run_in_terminal for declarado em tools, é OBRIGATÓRIO incluir .github/skills/terminal-governance/SKILL.md em source_docs (R-049).
argument-hint: '[caminho-do-arquivo | contexto-opcional]'
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# `/<verbo>-<objeto>`

> **Propósito**: Descreva o que este prompt executa em 1-2 frases diretas e imperativas.
> **Arquivo Ativo**: `${file}`
> **Workspace**: `${workspaceFolder}`

---

## 🎯 Invocação e Variáveis Nativas

Este prompt utiliza as variáveis de contexto nativas do VS Code Copilot:

```bash
# Execução direta com base no arquivo ativo no editor:
/<verbo>-<objeto>

# Execução passando argumento explícito ou filtro:
/<verbo>-<objeto> <argumento>
```

### Variáveis Disponíveis no Template
- `${file}`: Caminho absoluto do arquivo aberto e em foco no editor.
- `${selection}`: Trecho de código ou texto atualmente selecionado pelo usuário.
- `${workspaceFolder}`: Diretório raiz do workspace ativo.
- `${input:nomeDoParametro}`: Parâmetro dinâmico solicitado ao usuário no momento da invocação.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** processar o arquivo alvo `${file}` ou a seleção `${selection}`.
- ✅ **SEMPRE** verificar erros via `get_errors` antes e após alterações.
- ❌ **NÃO** inferir requisitos ou refatorar além da intenção declarada ("Never infer intent").
- ❌ **NÃO** executar operações destrutivas ou irreversíveis sem confirmação prévia explícita.
- ❌ **NÃO** modificar arquivos fora do escopo sem instrução direta.

---

## 📋 Fluxo de Execução Passo a Passo

### Passo 1 — Coleta de Contexto e Linha de Base
- Avalie se o usuário forneceu `${selection}` ou se o alvo é o arquivo completo `${file}`.
- Se necessário um parâmetro complementar em runtime, interaja via `${input:nomeDoParametro}`.
- Leia o arquivo alvo usando `read_file` e colete o estado atual de integridade via `get_errors`.

### Passo 2 — Processamento e Transformação
- Aplique a transformação técnica planejada respeitando convenções e menor privilégio.
- Preserve estilo existente, tipagem estrita e regras de linting do projeto.

### Passo 3 — Validação e Checagem Imediata
- Execute novamente `get_errors` sobre o arquivo alterado.
- Caso novos erros ou avisos apareçam, corrija-os antes de apresentar a conclusão.

### Passo 4 — Saída Estruturada
- Apresente um resumo enxuto e rastreável do resultado obtido.

---

## ✅ Checklist Antes de Apresentar

- [ ] Arquivo alvo (`${file}` ou argumento) verificado antes da intervenção.
- [ ] Transformação aplicada de forma atômica e pontual.
- [ ] `get_errors` rodado com 0 novos erros introduzidos.
- [ ] Limites de Não-Escopo respeitados.
- [ ] Nenhuma alteração não autorizada fora do arquivo alvo.

---

## 📊 Formato de Saída

```markdown
### Execução de `/<verbo>-<objeto>`

- **Arquivo Processado**: `${file}`
- **Status de Integridade**: ✅ Sem erros (`get_errors` validado)

### Alterações Realizadas
- <Item 1 das alterações executadas>
- <Item 2 das alterações executadas>

### Próximo Passo Sugerido
- <Próxima ação recomendada, ex.: rodar testes ou comando encadeado>
```

---

## 🚨 Regras de Autonomia

- ❌ **NUNCA** executar comandos de exclusão, git push, migrações de banco ou reescrita massiva sem confirmação humana.
- ✅ **SEMPRE** expor evidências com referências de linhas e arquivos tocados.

---

## 🔄 Combina Com (Encadeamento)

```text
/<prompt-anterior> → /<verbo>-<objeto> → /<prompt-seguinte>
```

- `/<prompt-anterior>`: Gera o insumo ou contexto preliminar.
- `/<prompt-seguinte>`: Consome o artefato produzido (ex.: `/review` ou `/commit`).

