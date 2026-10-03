"""Testes unitários para `workspace_catalog` (picker `#` do composer).

Cobre a varredura de arquivos do workspace com allowlist de diretórios
ignorados, filtro por substring (case-insensitive) e orçamento de
varredura/corte (`truncated`).
"""

from __future__ import annotations

from pathlib import Path

from local_chat_gateway.workspace_catalog import listar_arquivos_workspace


def _criar_arquivo(raiz: Path, caminho_relativo: str) -> None:
    arquivo = raiz / caminho_relativo
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text("x", encoding="utf-8")


class TestListarArquivosWorkspace:
    """Testes de `listar_arquivos_workspace`."""

    def test_deve_listar_todos_os_arquivos_sem_query(self, tmp_path: Path) -> None:
        _criar_arquivo(tmp_path, "README.md")
        _criar_arquivo(tmp_path, "src/page.tsx")
        _criar_arquivo(tmp_path, "src/routes.py")

        arquivos, truncado = listar_arquivos_workspace(
            raizes=[("proj", tmp_path)], query="", limit=10
        )

        assert truncado is False
        assert {a.path for a in arquivos} == {
            "README.md",
            "src/page.tsx",
            "src/routes.py",
        }
        assert all(a.project == "proj" for a in arquivos)

    def test_deve_ordenar_por_proximidade_da_raiz(self, tmp_path: Path) -> None:
        _criar_arquivo(tmp_path, "a/b/c/muito-profundo.ts")
        _criar_arquivo(tmp_path, "raiz.ts")

        arquivos, _ = listar_arquivos_workspace(
            raizes=[("proj", tmp_path)], query="", limit=10
        )

        assert arquivos[0].path == "raiz.ts"
        assert arquivos[-1].path == "a/b/c/muito-profundo.ts"

    def test_deve_filtrar_por_substring_case_insensitive(self, tmp_path: Path) -> None:
        _criar_arquivo(tmp_path, "src/routes.py")
        _criar_arquivo(tmp_path, "src/page.tsx")

        arquivos, truncado = listar_arquivos_workspace(
            raizes=[("proj", tmp_path)], query="ROUT", limit=10
        )

        assert truncado is False
        assert [a.path for a in arquivos] == ["src/routes.py"]

    def test_deve_ignorar_diretorios_da_allowlist(self, tmp_path: Path) -> None:
        _criar_arquivo(tmp_path, "node_modules/pacote/index.js")
        _criar_arquivo(tmp_path, ".git/HEAD")
        _criar_arquivo(tmp_path, "__pycache__/modulo.pyc")
        _criar_arquivo(tmp_path, "src/valido.py")

        arquivos, _ = listar_arquivos_workspace(
            raizes=[("proj", tmp_path)], query="", limit=10
        )

        assert [a.path for a in arquivos] == ["src/valido.py"]

    def test_deve_ignorar_raiz_de_projeto_inexistente(self, tmp_path: Path) -> None:
        raiz_inexistente = tmp_path / "nao-existe"

        arquivos, truncado = listar_arquivos_workspace(
            raizes=[("fantasma", raiz_inexistente)], query="", limit=10
        )

        assert arquivos == []
        assert truncado is False

    def test_deve_combinar_multiplas_raizes_de_projetos(self, tmp_path: Path) -> None:
        raiz_a = tmp_path / "projeto-a"
        raiz_b = tmp_path / "projeto-b"
        _criar_arquivo(raiz_a, "app.py")
        _criar_arquivo(raiz_b, "app.py")

        arquivos, _ = listar_arquivos_workspace(
            raizes=[("a", raiz_a), ("b", raiz_b)], query="", limit=10
        )

        assert {(a.project, a.path) for a in arquivos} == {
            ("a", "app.py"),
            ("b", "app.py"),
        }

    def test_deve_marcar_truncado_quando_excede_limit(self, tmp_path: Path) -> None:
        for indice in range(5):
            _criar_arquivo(tmp_path, f"arquivo-{indice}.txt")

        arquivos, truncado = listar_arquivos_workspace(
            raizes=[("proj", tmp_path)], query="", limit=2
        )

        assert len(arquivos) == 2
        assert truncado is True

    def test_deve_marcar_truncado_quando_orcamento_de_varredura_estoura(
        self, tmp_path: Path
    ) -> None:
        for indice in range(5):
            _criar_arquivo(tmp_path, f"arquivo-{indice}.txt")

        arquivos, truncado = listar_arquivos_workspace(
            raizes=[("proj", tmp_path)],
            query="",
            limit=10,
            orcamento_varredura=2,
        )

        assert len(arquivos) <= 2
        assert truncado is True

    def test_deve_ocultar_dotdir_por_padrao_mesmo_sem_gitignore(
        self, tmp_path: Path
    ) -> None:
        """Paridade com ripgrep/picker da IDE: diretorio dot-prefixed fica
        oculto por padrao mesmo sem nenhum `.gitignore`/`.ignore` no projeto."""
        _criar_arquivo(tmp_path, ".vscode/settings.json")
        _criar_arquivo(tmp_path, "src/visivel.ts")

        arquivos, _ = listar_arquivos_workspace(
            raizes=[("proj", tmp_path)], query="", limit=10
        )

        assert [a.path for a in arquivos] == ["src/visivel.ts"]

    def test_deve_desocultar_dotdir_via_negacao_em_ignore(
        self, tmp_path: Path
    ) -> None:
        """Bug real corrigido: `.github/` deve aparecer quando o projeto
        declara `!.github/`/`!.github/**` em `.ignore` ou `.rgignore` --
        mesma convencao usada na raiz deste monorepo para desocultar
        `.github/` do ripgrep/picker da IDE."""
        _criar_arquivo(tmp_path, ".github/agents/foo.agent.md")
        _criar_arquivo(tmp_path, ".vscode/settings.json")
        (tmp_path / ".ignore").write_text(
            "!.github/\n!.github/**\n", encoding="utf-8"
        )

        arquivos, _ = listar_arquivos_workspace(
            raizes=[("proj", tmp_path)], query="", limit=10
        )

        caminhos = {a.path for a in arquivos}
        assert ".github/agents/foo.agent.md" in caminhos
        assert not any(c.startswith(".vscode") for c in caminhos)

    def test_deve_respeitar_gitignore_do_projeto(self, tmp_path: Path) -> None:
        """Padrao de `.gitignore` do proprio projeto (ex.: `*.log`) deve ser
        aplicado mesmo sobre arquivos nao-dot-prefixed."""
        _criar_arquivo(tmp_path, "app.log")
        _criar_arquivo(tmp_path, "app.py")
        (tmp_path / ".gitignore").write_text("*.log\n", encoding="utf-8")

        arquivos, _ = listar_arquivos_workspace(
            raizes=[("proj", tmp_path)], query="", limit=10
        )

        assert [a.path for a in arquivos] == ["app.py"]

    def test_git_nunca_aparece_mesmo_com_negacao(self, tmp_path: Path) -> None:
        """`.git/` e caso especial incondicional (nunca exibido), mesmo que
        o projeto declare uma negacao `!.git/` por engano."""
        _criar_arquivo(tmp_path, ".git/HEAD")
        (tmp_path / ".ignore").write_text("!.git/\n!.git/**\n", encoding="utf-8")

        arquivos, _ = listar_arquivos_workspace(
            raizes=[("proj", tmp_path)], query="", limit=10
        )

        assert arquivos == []


