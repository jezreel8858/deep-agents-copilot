---
name: yaml-governance
description: >
  Boas práticas genéricas para ler, gerar, revisar e validar arquivos YAML/YML
  com segurança, tipagem explícita e schema validation.
tier: 2
category: governance
triggers:
  - "yaml"
  - "yml"
  - "yamllint"
  - "schema"
  - "kubernetes"
  - "helm"
  - "values.yaml"
  - "config.yaml"
  - "yaml-language-server"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# YAML Governance — Boas práticas genéricas

Use esta skill sempre que a tarefa envolver arquivos `.yml` ou `.yaml`.

## 1) Diretrizes essenciais

- Indentação com **2 espaços**; nunca use tabs.
- Não misture convenções de nomes no mesmo arquivo.
- Valores ambíguos, datas e versões devem ficar entre aspas.
- Evite coerções de YAML 1.1 (`on/off/yes/no`) — prefira `true/false`.
- Comentários devem registrar **por quê** da decisão, não repetir o conteúdo.
- Segredos nunca em texto plano; use secret managers/variáveis seguras.
- Em Kubernetes/Helm, fixe versões, declare recursos e mantenha probes/labels consistentes.

## 2) Fluxo recomendado para o agente

1. Identificar tipo de arquivo e schema esperado.
2. Verificar indentação, aspas, tipos, chaves duplicadas e aliases.
3. Validar com `yamllint` e com schema (`check-jsonschema`) quando houver contrato.
4. Para manifests Kubernetes, validar também o resultado renderizado (`helm template` + `kubeconform`).
5. Em caso de ambiguidade, consultar exemplos do projeto antes de alterar.

## 3) Ferramentas de validação

- `yamllint` para estilo e sintaxe
- `check-jsonschema` para contrato estrutural/tipos
- `yq` para leitura e transformação segura
- `kubeconform` para manifests Kubernetes
- `safe_load` (ou equivalente) para parsing seguro

## 4) Schema validation (recomendado)

```yaml
# Associe schema no topo do arquivo para validação em IDE (YAML Language Server)
# yaml-language-server: $schema=./schema/meu-arquivo.schema.json
```

```bash
# Exemplo de validação local
yamllint caminho/arquivo.yaml
check-jsonschema --schemafile schema/meu-arquivo.schema.json caminho/arquivo.yaml
```

## 5) Checklist antes de concluir

- [ ] Sem tabs e sem chaves duplicadas
- [ ] Valores ambíguos com aspas
- [ ] Sem segredos hardcoded
- [ ] Schema validado (quando existir)
- [ ] Lint validado (`yamllint`)
- [ ] Compatível com renderizador final (Kubernetes/Helm/CI)

## 6) Anti-padrões

- ❌ `YES`, `NO`, `on`, `off` e datas sem aspas
- ❌ Anchors e aliases excessivamente encadeados
- ❌ `latest` em imagens ou valores não versionados
- ❌ Segredos em texto plano
- ❌ Comentários desatualizados ou redundantes
- ❌ Validar apenas sintaxe sem validar schema

## 7) Referências

- YAML 1.2 Spec: https://yaml.org/spec/1.2.2/
- Yamllint: https://yamllint.readthedocs.io/
- check-jsonschema: https://check-jsonschema.readthedocs.io/
- Kubernetes schema validation: https://github.com/yannh/kubeconform
