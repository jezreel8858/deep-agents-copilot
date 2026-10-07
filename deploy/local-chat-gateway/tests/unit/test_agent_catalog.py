"""Testes unitarios de `agent_catalog.descobrir_custom_agents` (RT-04).

Cobre o parsing de `.github/agents/**/*.agent.md` em `CustomAgentConfig`
(mock de filesystem via `tmp_path` -- nenhum teste toca o filesystem real
do repositorio de governanca).
"""

from __future__ import annotations

from pathlib import Path

from local_chat_gateway.agent_catalog import (
    _ORCAMENTO_BYTES_PROMPT,
    _agent_autorizado_para_shell_nativo,
    _traduzir_tools_para_sdk_headless,
    descobrir_custom_agents,
)


def _escrever_agent_md(diretorio: Path, nome_arquivo: str, conteudo: str) -> Path:
    caminho = diretorio / nome_arquivo
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho


def test_deve_retornar_lista_vazia_quando_diretorio_nao_existe(tmp_path: Path) -> None:
    resultado = descobrir_custom_agents(tmp_path / "nao-existe")
    assert resultado == []


def test_deve_parsear_agent_valido_com_frontmatter_completo(tmp_path: Path) -> None:
    conteudo = """---
name: python-bug-fixer
description: Especialista em bugs Python
model: Claude Sonnet 5.5
tools: ['read_file', 'run_subagent']
---

# Perfil Operacional
Você é especialista em bugs Python.
"""
    _escrever_agent_md(tmp_path, "python-bug-fixer.agent.md", conteudo)

    resultado = descobrir_custom_agents(tmp_path)

    assert len(resultado) == 1
    agente = resultado[0]
    assert agente["name"] == "python-bug-fixer"
    assert agente["description"] == "Especialista em bugs Python"
    assert agente["model"] == "Claude Sonnet 5.5"
    # RC1 (bugfix 2026-10-02): "read_file" e traduzido para o nome nativo
    # do SDK headless. "run_subagent" NAO e mais traduzido (bugfix
    # 2026-10-04 -- ver comentario em `_ALIAS_TOOLS_SDK_HEADLESS`): o alias
    # antigo para "task" causava cascatas de subagents fantasmas sem
    # correspondencia no catalogo real; permanece literal/inerte agora.
    assert agente["tools"] == ["str_replace_editor", "run_subagent"]
    assert agente["infer"] is True
    assert "Perfil Operacional" in agente["prompt"]


def test_deve_ignorar_arquivo_sem_name_no_frontmatter(tmp_path: Path) -> None:
    conteudo = """---
description: Sem nome
---

Corpo do agent.
"""
    _escrever_agent_md(tmp_path, "sem-nome.agent.md", conteudo)

    resultado = descobrir_custom_agents(tmp_path)

    assert resultado == []


def test_deve_ignorar_arquivo_sem_frontmatter(tmp_path: Path) -> None:
    _escrever_agent_md(
        tmp_path, "sem-frontmatter.agent.md", "Apenas texto puro, sem ---."
    )

    resultado = descobrir_custom_agents(tmp_path)

    assert resultado == []


def test_deve_ignorar_frontmatter_yaml_invalido(tmp_path: Path) -> None:
    conteudo = """---
name: [invalido: sem fechar colchete
---

Corpo.
"""
    _escrever_agent_md(tmp_path, "yaml-invalido.agent.md", conteudo)

    resultado = descobrir_custom_agents(tmp_path)

    assert resultado == []


def test_deve_descobrir_recursivamente_em_subdiretorios(tmp_path: Path) -> None:
    subdir = tmp_path / "backend" / "python"
    subdir.mkdir(parents=True)
    conteudo = """---
name: python-router
description: Roteador Python
---

Corpo do roteador.
"""
    _escrever_agent_md(subdir, "python-router.agent.md", conteudo)

    resultado = descobrir_custom_agents(tmp_path)

    assert len(resultado) == 1
    assert resultado[0]["name"] == "python-router"


def test_deve_descartar_nome_duplicado_mantendo_primeira_ocorrencia(
    tmp_path: Path,
) -> None:
    conteudo_a = """---
name: duplicado
description: primeiro
---

Corpo A.
"""
    conteudo_b = """---
name: duplicado
description: segundo
---

Corpo B.
"""
    _escrever_agent_md(tmp_path, "a.agent.md", conteudo_a)
    _escrever_agent_md(tmp_path, "b.agent.md", conteudo_b)

    resultado = descobrir_custom_agents(tmp_path)

    assert len(resultado) == 1
    assert resultado[0]["description"] == "primeiro"


def test_deve_truncar_prompt_que_excede_orcamento_de_bytes(tmp_path: Path) -> None:
    # Bug real investigado (2026-10-04): o orcamento original de 16 KiB
    # truncava silenciosamente 9 dos 95 agents reais do catalogo (incluindo
    # `agent-router.agent.md`, perdendo 67% do conteudo). O orcamento foi
    # elevado para 64 KiB -- este teste usa um corpo maior que o orcamento
    # ATUAL (importado de `_ORCAMENTO_BYTES_PROMPT`, nunca hardcoded) para
    # continuar validando o comportamento de truncamento em si.
    corpo_grande = "x" * (_ORCAMENTO_BYTES_PROMPT + 4 * 1024)
    conteudo = f"""---
name: agent-grande
description: teste de truncamento
---

{corpo_grande}
"""
    _escrever_agent_md(tmp_path, "grande.agent.md", conteudo)

    resultado = descobrir_custom_agents(tmp_path)

    assert len(resultado) == 1
    prompt = resultado[0]["prompt"]
    assert len(prompt.encode("utf-8")) <= _ORCAMENTO_BYTES_PROMPT
    assert "truncado por orcamento" in prompt


def test_deve_ignorar_arquivo_sem_corpo(tmp_path: Path) -> None:
    conteudo = """---
name: sem-corpo
description: agent sem prompt
---
"""
    _escrever_agent_md(tmp_path, "sem-corpo.agent.md", conteudo)

    resultado = descobrir_custom_agents(tmp_path)

    assert resultado == []


def test_deve_descobrir_multiplos_agents_em_ordem_alfabetica(tmp_path: Path) -> None:
    for nome in ("zebra", "alpha", "mike"):
        conteudo = f"""---
name: {nome}
description: agent {nome}
---

Corpo de {nome}.
"""
        _escrever_agent_md(tmp_path, f"{nome}.agent.md", conteudo)

    resultado = descobrir_custom_agents(tmp_path)

    nomes = [a["name"] for a in resultado]
    assert nomes == ["alpha", "mike", "zebra"]


def test_deve_usar_leitor_arquivo_injetavel_para_mock(tmp_path: Path) -> None:
    caminho = _escrever_agent_md(
        tmp_path,
        "mockado.agent.md",
        "conteudo original no disco (nao deve ser usado)",
    )

    def leitor_fake(_: Path) -> str:
        return """---
name: mockado
description: via mock
---

Corpo via mock.
"""

    resultado = descobrir_custom_agents(tmp_path, leitor_arquivo=leitor_fake)

    assert len(resultado) == 1
    assert resultado[0]["name"] == "mockado"
    assert resultado[0]["description"] == "via mock"
    assert caminho.exists()  # arquivo real no disco permanece intacto


class TestTraduzirToolsParaSdkHeadless:
    """T1-T8 (bugfix 2026-10-02, RC1) -- expansao de `_ALIAS_TOOLS_SDK_HEADLESS`
    + allowlist deny-by-default para tools de shell real (`run_in_terminal`)."""

    def test_traduzir_tools_mapeia_read_file_para_str_replace_editor(self) -> None:
        assert _traduzir_tools_para_sdk_headless(["read_file"]) == [
            "str_replace_editor"
        ]

    def test_traduzir_tools_nao_traduz_mais_run_subagent_para_task(self) -> None:
        # Bugfix 2026-10-04: alias "run_subagent" -> "task" foi REMOVIDO
        # (cascata de subagents fantasmas, ver comentario em
        # `_ALIAS_TOOLS_SDK_HEADLESS`). Nome permanece literal/inerte.
        assert _traduzir_tools_para_sdk_headless(["run_subagent"]) == [
            "run_subagent"
        ]

    def test_traduzir_tools_mapeia_grep_search_para_grep(self) -> None:
        assert _traduzir_tools_para_sdk_headless(["grep_search"]) == ["grep"]

    def test_traduzir_tools_omite_run_in_terminal_sem_allowlist(self) -> None:
        frontmatter = {"tools": ["run_in_terminal"]}  # sem source_docs
        resultado = _traduzir_tools_para_sdk_headless(
            ["run_in_terminal"], frontmatter=frontmatter
        )
        assert resultado == []
        assert "bash" not in resultado
        assert "run_in_terminal" not in resultado

    def test_traduzir_tools_libera_bash_com_allowlist_completa(self) -> None:
        frontmatter = {
            "tools": ["run_in_terminal"],
            "source_docs": [".github/skills/terminal-governance/SKILL.md"],
        }
        resultado = _traduzir_tools_para_sdk_headless(
            ["run_in_terminal"], frontmatter=frontmatter
        )
        assert resultado == ["bash"]

    def test_traduzir_tools_nega_bash_so_com_tool_sem_skill(self) -> None:
        frontmatter = {"tools": ["run_in_terminal"], "source_docs": ["outra-skill"]}
        resultado = _traduzir_tools_para_sdk_headless(
            ["run_in_terminal"], frontmatter=frontmatter
        )
        assert resultado == []

    def test_traduzir_tools_nega_bash_so_com_skill_sem_tool_declarada(self) -> None:
        frontmatter = {
            "tools": ["read_file"],
            "source_docs": [".github/skills/terminal-governance/SKILL.md"],
        }
        resultado = _traduzir_tools_para_sdk_headless(
            ["run_in_terminal"], frontmatter=frontmatter
        )
        assert resultado == []

    def test_traduzir_tools_preserva_nome_mcp_sem_alias(self) -> None:
        resultado = _traduzir_tools_para_sdk_headless(["mcp_context-mode_ctx_execute"])
        assert resultado == ["mcp_context-mode_ctx_execute"]


class TestAgentAutorizadoParaShellNativo:
    """Testes diretos de `_agent_autorizado_para_shell_nativo` (allowlist
    deny-by-default, Security Checkpoint Risco #1)."""

    def test_nega_sem_frontmatter_tools_nem_source_docs(self) -> None:
        assert _agent_autorizado_para_shell_nativo({}) is False

    def test_autoriza_com_ambos_sinais(self) -> None:
        frontmatter = {
            "tools": ["run_in_terminal"],
            "source_docs": [".github/skills/terminal-governance/SKILL.md"],
        }
        assert _agent_autorizado_para_shell_nativo(frontmatter) is True
