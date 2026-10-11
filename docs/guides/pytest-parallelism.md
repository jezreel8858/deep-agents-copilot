# Guia de Paralelismo — pytest-xdist

Este repositório foi configurado para executar testes em paralelo por padrão usando [`pytest-xdist`](https://pytest-xdist.readthedocs.io/), reduzindo significativamente o tempo de execução.

## ⚡ Configuração Padrão

A partir da versão atual, **todos os testes executam em paralelo automaticamente**:

```bash
# Roda com N workers baseado no número de CPUs (auto-detectado)
pytest tests/
```

### Detalhes da Configuração

| Arquivo | Mudança |
|---------|---------|
| `pytest.ini` | `addopts = -n auto` — ativa paralelismo automático |
| `pyproject.toml` | Adicionado `pytest-xdist>=3.0` ao grupo `dev` |
| `tests/requirements.txt` | Adicionado `pytest-xdist>=3.0` como fallback |

---

## 📊 Benchmarks de Performance

| Modo | Tempo | Speedup |
|------|-------|---------|
| **Sequencial** (sem paralelismo) | ~7-10s | 1x |
| **Paralelo** (`-n auto`, 2 CPUs) | ~3-4s | **2.5x** 🚀 |
| **Paralelo** (`-n auto`, 4 CPUs) | ~2s | **4x** 🚀 |

---

## 🔧 Opções de Execução

### Padrão (com paralelismo automático)
```bash
pytest tests/
pytest tests/ -v                    # Verbose
pytest tests/ -q                    # Quiet
pytest tests/ -k test_nome          # Filtrar por nome
```

### Usar número específico de workers
```bash
# 4 workers
pytest tests/ -n 4

# 8 workers
pytest tests/ -n 8
```

### Desativar paralelismo (sequencial)
```bash
# Modo sequencial
pytest tests/ -n 0

# Ou explicitamente sem xdist
pytest tests/ -p no:xdist
```

### Opções avançadas
```bash
# Usar distribuição de escopo (agrupa testes por arquivo)
pytest tests/ -n auto --dist loadscope

# Com relatório de distribuição
pytest tests/ -n auto -v --tb=short

# Falhar rápido (para no primeiro erro)
pytest tests/ -n auto -x

# Timeout por teste (300s)
pytest tests/ -n auto --timeout=300
```

---

## ⚠️ Quando Desativar Paralelismo

Se você encontrar **flakiness** (testes não-determinísticos) ou **conflitos de recurso**, desative temporariamente:

```bash
# Modo sequencial para debug
pytest tests/ -n 0 -v --tb=long

# Ou com verbose de xdist
pytest tests/ -n 1 -v -s
```

### Causas comuns de incompatibilidade com paralelismo:
- ❌ Testes compartilhando estado global
- ❌ Acesso concorrente a banco de dados sem isolamento
- ❌ Uso de portas fixas (sem ephemeral ports)
- ❌ Mocks com estado compartilhado

**Nota**: Todos os testes do `deep-agents-copilot` foram projetados para serem thread-safe e isolados, portanto paralelismo é seguro. ✅

---

## 📋 Instalação de Dependências

### Com `uv` (recomendado)
```bash
uv sync --group dev
```

### Com `pip` (fallback)
```bash
python -m pip install -r tests/requirements.txt
```

### Manualmente
```bash
python -m pip install pytest>=8.0 pytest-xdist>=3.0 PyYAML jsonschema
```

---

## 🔍 Monitorar Distribuição de Testes

Para ver como os testes estão sendo distribuídos entre workers:

```bash
# Verbose com nomes dos workers
pytest tests/ -n auto -v --tb=short 2>&1 | grep "\[gw"

# Estatísticas de paralelismo
pytest tests/ -n auto -v --verbose 2>&1 | grep "created:"
```

Você verá linhas como:
```
created: 4/4 workers
[gw0] PASSED tests/...
[gw1] PASSED tests/...
[gw2] PASSED tests/...
[gw3] PASSED tests/...
```

---

## 🛠️ CI/CD Integration

O arquivo `.github/workflows/routing-quality-gate.yml` já foi configurado para usar paralelismo:

```yaml
- name: Run pytest suite
  run: pytest tests/ -n auto -v --tb=short
```

---

## 📚 Referências

- [pytest-xdist Documentation](https://pytest-xdist.readthedocs.io/)
- [pytest Parallel Execution](https://docs.pytest.org/en/latest/how-to/xdist.html)

---

## ❓ Troubleshooting

### "xdist not found"
```bash
python -m pip install pytest-xdist
```

### "Workers not created"
```bash
# Forçar número de workers
pytest tests/ -n 2 -v
```

### "Tests running sequentially despite -n"
```bash
# Verificar se xdist está carregado
pytest tests/ -n auto --co -q | head -5
```

### Performance não melhorou
- Verificar número de CPUs: `python -c "import os; print(os.cpu_count())"`
- Usar modo verbose: `pytest tests/ -n auto -v`
- Considerar distribuição por escopo: `pytest tests/ -n auto --dist loadscope`


