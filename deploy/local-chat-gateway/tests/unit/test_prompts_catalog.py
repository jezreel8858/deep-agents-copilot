"""Testes unitarios de `prompts_catalog.descobrir_comandos` (picker `/`
do composer, pedido explicito do usuario 2026-10-02).

Cobre o parsing de `.github/prompts/*.prompt.md` + `.github/skills/**/
SKILL.md` em `ComandoCatalogItem` (mock de filesystem via `tmp_path` --
nenhum teste toca o filesystem real do repositorio de governanca).
"""

from __future__ import annotations

from pathlib import Path

from local_chat_gateway.prompts_catalog import descobrir_comandos


def _escrever(caminho: Path, conteudo: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(conteudo, encoding="utf-8")


def test_deve_retornar_lista_vazia_quando_nenhum_diretorio_existe(tmp_path: Path) -> None:
    resultado = descobrir_comandos(tmp_path / "nao-existe")
    assert resultado == []


def test_deve_descobrir_prompt_valido_com_frontmatter_completo(tmp_path: Path) -> None:
    conteudo = """---
name: commit
description: Gera mensagem de commit convencional (PT-BR) baseada no diff.
---

Corpo do prompt.
"""
    _escrever(tmp_path / "prompts" / "commit.prompt.md", conteudo)

    resultado = descobrir_comandos(tmp_path)

    assert len(resultado) == 1
    assert resultado[0]["name"] == "commit"
    assert resultado[0]["kind"] == "prompt"
    assert "Gera mensagem de commit" in resultado[0]["description"]


def test_deve_descobrir_skill_valida_em_subpasta_recursiva(tmp_path: Path) -> None:
    conteudo = """---
name: context-mode
description: Boas praticas de uso do context-mode MCP.
tier: 1
---

Corpo da skill.
"""
    _escrever(tmp_path / "skills" / "context-mode" / "SKILL.md", conteudo)

    resultado = descobrir_comandos(tmp_path)

    assert len(resultado) == 1
    assert resultado[0]["name"] == "context-mode"
    assert resultado[0]["kind"] == "skill"
    assert "context-mode MCP" in resultado[0]["description"]


def test_deve_usar_nome_do_arquivo_quando_frontmatter_sem_name(tmp_path: Path) -> None:
    conteudo = """---
description: Sem campo name.
---

Corpo.
"""
    _escrever(tmp_path / "prompts" / "meu-prompt.prompt.md", conteudo)

    resultado = descobrir_comandos(tmp_path)

    assert len(resultado) == 1
    assert resultado[0]["name"] == "meu-prompt"


def test_deve_usar_nome_da_pasta_quando_skill_sem_name_no_frontmatter(tmp_path: Path) -> None:
    conteudo = """---
description: Sem campo name.
---

Corpo.
"""
    _escrever(tmp_path / "skills" / "minha-skill" / "SKILL.md", conteudo)

    resultado = descobrir_comandos(tmp_path)

    assert len(resultado) == 1
    assert resultado[0]["name"] == "minha-skill"


def test_deve_ignorar_frontmatter_yaml_invalido(tmp_path: Path) -> None:
    conteudo = """---
name: [invalido: sem fechar colchete
---

Corpo.
"""
    _escrever(tmp_path / "prompts" / "invalido.prompt.md", conteudo)

    resultado = descobrir_comandos(tmp_path)

    # Fallback de nome (arquivo) ainda se aplica mesmo com frontmatter
    # invalido -- `_parse_frontmatter` retorna {} e o nome_fallback e usado.
    assert len(resultado) == 1
    assert resultado[0]["name"] == "invalido"
    assert resultado[0]["description"] == ""


def test_deve_descartar_nome_duplicado_mantendo_1a_ocorrencia(tmp_path: Path) -> None:
    conteudo_prompt = """---
name: duplicado
description: Versao do prompt.
---

Corpo.
"""
    conteudo_skill = """---
name: duplicado
description: Versao da skill (nunca deve aparecer).
---

Corpo.
"""
    _escrever(tmp_path / "prompts" / "duplicado.prompt.md", conteudo_prompt)
    _escrever(tmp_path / "skills" / "duplicado" / "SKILL.md", conteudo_skill)

    resultado = descobrir_comandos(tmp_path)

    assert len(resultado) == 1
    assert resultado[0]["kind"] == "prompt"
    assert resultado[0]["description"] == "Versao do prompt."


def test_deve_descobrir_prompts_e_skills_juntos_ordenados(tmp_path: Path) -> None:
    _escrever(
        tmp_path / "prompts" / "b-prompt.prompt.md",
        "---\nname: b-prompt\ndescription: B.\n---\n\nCorpo.",
    )
    _escrever(
        tmp_path / "prompts" / "a-prompt.prompt.md",
        "---\nname: a-prompt\ndescription: A.\n---\n\nCorpo.",
    )
    _escrever(
        tmp_path / "skills" / "z-skill" / "SKILL.md",
        "---\nname: z-skill\ndescription: Z.\n---\n\nCorpo.",
    )

    resultado = descobrir_comandos(tmp_path)

    nomes = [item["name"] for item in resultado]
    # Prompts (ordem alfabetica) primeiro, depois skills (ordem alfabetica).
    assert nomes == ["a-prompt", "b-prompt", "z-skill"]
    assert [item["kind"] for item in resultado] == ["prompt", "prompt", "skill"]
