"""Testes unitários para `projects_catalog` (descoberta automática de projetos).

Cobre a tradução `path_externo` (host, Windows OU POSIX) -> path no
container, sob a convenção de que todos os projetos vivem sob um único
diretório-pai comum montado em `/workspaces` (`PROJECTS_ROOT_PATH`).
"""

from __future__ import annotations

from pathlib import Path

from local_chat_gateway.projects_catalog import carregar_projetos


def _escrever_yaml(tmp_path: Path, conteudo: str) -> str:
    arquivo = tmp_path / "projects.local.yaml"
    arquivo.write_text(conteudo, encoding="utf-8")
    return str(arquivo)


class TestCarregarProjetos:
    """Testes de `carregar_projetos`."""

    def test_deve_retornar_lista_vazia_quando_projects_root_path_nao_definido(
        self, tmp_path: Path
    ) -> None:
        yaml_path = _escrever_yaml(
            tmp_path,
            "projetos:\n"
            '  - id: "a"\n'
            '    name: "A"\n'
            '    path_externo: "D:\\\\workspace\\\\a"\n',
        )
        assert (
            carregar_projetos(
                projects_yaml_path=yaml_path, projects_root_path_host=None
            )
            == []
        )

    def test_deve_retornar_lista_vazia_quando_yaml_nao_existe(
        self, tmp_path: Path
    ) -> None:
        caminho_inexistente = str(tmp_path / "nao-existe.yaml")
        assert (
            carregar_projetos(
                projects_yaml_path=caminho_inexistente,
                projects_root_path_host="D:/workspace",
            )
            == []
        )

    def test_deve_traduzir_path_windows_para_path_no_container(
        self, tmp_path: Path
    ) -> None:
        yaml_path = _escrever_yaml(
            tmp_path,
            "projetos:\n"
            '  - id: "deep-agents-copilot"\n'
            '    name: "Deep Agents Copilot"\n'
            '    path_externo: "D:\\\\workspace\\\\deep-agents-copilot"\n'
            '  - id: "projeto-exemplo-app"\n'
            '    name: "Projeto Exemplo App"\n'
            '    path_externo: "D:\\\\workspace\\\\projeto-exemplo-app"\n',
        )

        projetos = carregar_projetos(
            projects_yaml_path=yaml_path, projects_root_path_host="D:/workspace"
        )

        assert len(projetos) == 2
        por_id = {p.id: p for p in projetos}
        assert por_id["deep-agents-copilot"].path_container == (
            "/workspaces/deep-agents-copilot"
        )
        assert por_id["projeto-exemplo-app"].path_container == (
            "/workspaces/projeto-exemplo-app"
        )
        assert por_id["projeto-exemplo-app"].nome == "Projeto Exemplo App"

    def test_deve_traduzir_path_posix_para_path_no_container(
        self, tmp_path: Path
    ) -> None:
        yaml_path = _escrever_yaml(
            tmp_path,
            "projetos:\n"
            '  - id: "meu-projeto"\n'
            '    name: "Meu Projeto"\n'
            '    path_externo: "/home/dev/workspace/meu-projeto"\n',
        )

        projetos = carregar_projetos(
            projects_yaml_path=yaml_path,
            projects_root_path_host="/home/dev/workspace",
        )

        assert len(projetos) == 1
        assert projetos[0].path_container == "/workspaces/meu-projeto"

    def test_deve_ignorar_projeto_fora_da_raiz_montada(self, tmp_path: Path) -> None:
        yaml_path = _escrever_yaml(
            tmp_path,
            "projetos:\n"
            '  - id: "dentro"\n'
            '    name: "Dentro"\n'
            '    path_externo: "D:\\\\workspace\\\\dentro"\n'
            '  - id: "fora"\n'
            '    name: "Fora"\n'
            '    path_externo: "E:\\\\outro-disco\\\\fora"\n',
        )

        projetos = carregar_projetos(
            projects_yaml_path=yaml_path, projects_root_path_host="D:/workspace"
        )

        assert len(projetos) == 1
        assert projetos[0].id == "dentro"

    def test_deve_ignorar_projeto_sem_path_externo_ou_sem_id(
        self, tmp_path: Path
    ) -> None:
        yaml_path = _escrever_yaml(
            tmp_path,
            "projetos:\n"
            '  - id: "sem-path"\n'
            '    name: "Sem Path"\n'
            '  - name: "Sem Id"\n'
            '    path_externo: "D:\\\\workspace\\\\sem-id"\n'
            '  - id: "valido"\n'
            '    name: "Valido"\n'
            '    path_externo: "D:\\\\workspace\\\\valido"\n',
        )

        projetos = carregar_projetos(
            projects_yaml_path=yaml_path, projects_root_path_host="D:/workspace"
        )

        assert [p.id for p in projetos] == ["valido"]

    def test_deve_retornar_lista_vazia_quando_yaml_malformado(
        self, tmp_path: Path
    ) -> None:
        yaml_path = _escrever_yaml(tmp_path, "projetos: [sem fechar\n  - id: a")
        assert (
            carregar_projetos(
                projects_yaml_path=yaml_path,
                projects_root_path_host="D:/workspace",
            )
            == []
        )

    def test_deve_mapear_projeto_que_e_a_propria_raiz(self, tmp_path: Path) -> None:
        """`path_externo == projects_root_path_host` (raiz e o proprio
        projeto, sem sufixo) deve mapear para o mountpoint puro."""
        yaml_path = _escrever_yaml(
            tmp_path,
            "projetos:\n"
            '  - id: "raiz"\n'
            '    name: "Raiz"\n'
            '    path_externo: "D:\\\\workspace"\n',
        )

        projetos = carregar_projetos(
            projects_yaml_path=yaml_path, projects_root_path_host="D:/workspace"
        )

        assert projetos[0].path_container == "/workspaces"
