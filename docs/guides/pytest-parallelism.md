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

| Modo | Tempo | Speed-up | Observações |
|------|-------|---------|---|
| **Sequencial** (`-n 0`) | ~165-170s | 1x | Baseline |
| **`-n auto`** (2 CPUs) | ~165s | ~1x | Padrão (auto-detecta) |
| **`-n 2`** | ~130-145s | ~1.1x | Bom balanço |
| **`-n 4`** | ~128s | ~1.3x | **Mais rápido, mas com mais I/O contention** ⚠️ |

### Trade-off: Velocidade vs Warnings
- **`-n auto` (padrão)**: Seguro, sem warnings, mas mais lento no Windows
- **`-n 4`**: ~3-5% mais rápido, mas alguns testes I/O-bound excedem orçamento (warnings de 3-5s)
- **`-n 2`**: Bom balanço entre velocidade e estabilidade

---

## 🪟 Performance no Windows (Git + I/O Lento)

No Windows, Git e operações de I/O em disco são **significativamente mais lentos** do que em Linux/Mac.

### ⚠️ Observações Importantes
- Testes com I/O pesado (criação de repositórios Git em `tmp_path`) sofrem contenção de disco com múltiplos workers
- Fixtures `scope="session"` que constroem repositórios Git só rodam uma vez (gargalo inicial)
- Overhead de inter-processo entre workers em Windows é maior que em Linux

### 📊 Benchmarks Realistas (Windows)

| Modo | Tempo | Observações |
|------|-------|---|
| **Sequencial** (`-n 0`) | ~160s | Baseline |
| **`-n auto` (2 CPUs)** | ~130-140s | **Padrão recomendado** ✅ |
| **`-n 4`** | ~128s | Ligeiramente mais rápido, mas margem pequena |
| **`-n auto --dist loadscope`** | ~160s+ | Menos eficiente em Windows |

## 🎯 Recomendações por Cenário

### Desenvolvimento Local (Windows)
```bash
# Padrão seguro (auto)
pytest tests/

# Se quiser mais velocidade, aceitar warnings
pytest tests/ -n 4

# Bom balanço
pytest tests/ -n 2
```

### CI/CD (GitHub Actions / Windows)
```bash
# Use menos workers para evitar timeouts
pytest tests/ -n 2 -v --tb=short
```

### Diagnóstico / Debug
```bash
# Modo sequencial para baseline
pytest tests/ -n 0 -v

# Ver duração individual dos testes
pytest tests/ -n auto --durations=20
```

---

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
# Usar menos workers (útil em Windows com contenção)
pytest tests/ -n 2

# Usar distribuição por escopo (pode ser mais lento em Windows)
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

O arquivo `.github/workflows/routing-quality-gate.yml` está configurado para usar paralelismo automático:

```yaml
- name: Run pytest suite
  run: pytest tests/ -n auto -v --tb=short
```

**Nota**: No Windows (como `windows-latest` em GitHub Actions), considere usar `-n 2` se houver timeout excessivo devido a contenção de disco.

---

## 📚 Referências

- [pytest-xdist Documentation](https://pytest-xdist.readthedocs.io/)
- [pytest Parallel Execution](https://docs.pytest.org/en/latest/how-to/xdist.html)

---

## ❓ Troubleshooting

### "Testes lentos mesmo com paralelismo (Windows)"
No Windows, I/O e Git são lentos. Tente:
```bash
# Usar menos workers para reduzir contenção
pytest tests/ -n 2

# Ou modo sequencial para baseline
pytest tests/ -n 0

# Ver quais testes estão demorando
pytest tests/ -n auto -v --durations=10
```

### "Warnings: teste excedeu orçamento de 5s"
Isso é esperado para testes I/O-bound no Windows (especialmente `tests/model_profiles`).
O aviso é informativo e não falha o teste. Considere:
- Usar `-n 2` em vez de `-n auto`
- Aumentar orçamento em conftest.py se necessário

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
- Em Windows, tentar `-n 2` em vez de `-n auto`
- Usar modo verbose: `pytest tests/ -n auto -v`
- Verificar duração dos testes: `pytest tests/ -n auto --durations=10`


