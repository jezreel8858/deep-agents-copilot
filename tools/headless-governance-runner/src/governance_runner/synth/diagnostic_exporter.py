"""
diagnostic_exporter — Exportacao deterministica bit-a-bit (YAML + MD) e guardas de path (B3-02 / CA-05 / CA-07 / P5).

Invariantes:
- Denylist imutavel de escrita (.github/agents/routing-graph.yaml, .github/agents/agent-router.agent.md,
  .github/agents/evals/casos-roteamento.yaml) comparada por path resolvido (case-insensitive no Windows),
  valendo MESMO quando --allow-root eh especificado.
- Sem --allow-root, o diretorio de saida deve residir sob .synth/ ou .github/agents/evals/synthetic/.
- Escrita deterministica com newline="\n", yaml.safe_dump(sort_keys=True, allow_unicode=True,
  default_flow_style=False) e sanitizacao de excertos Markdown (escape de |, `, < e truncamento a 240 chars).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

from governance_runner.synth.diagnostics import DiagnosticoAssertividade
from governance_runner.synth.routing_graph import EXIT_PATH_PROIBIDO

__all__ = [
    "DEFAULT_DIAGNOSTIC_OUT_REL_DIR",
    "DENYLIST_REL_PATHS",
    "FORMATOS_DIAGNOSTICO",
    "MAX_EXCERPT_LEN",
    "FormatoDiagnostico",
    "SynthDiagnosticPathError",
    "ResultadoExportDiagnostico",
    "sanitizar_excerto_md",
    "ensure_allowed_write_path",
    "ensure_allowed_Write_path",
    "serializar_diagnostico_dict",
    "renderizar_diagnostico_yaml",
    "renderizar_diagnostico_md",
    "exportar_diagnostico",
]

DEFAULT_DIAGNOSTIC_OUT_REL_DIR = Path(".github") / "agents" / "evals" / "synthetic"
ALT_DIAGNOSTIC_OUT_REL_DIR = Path(".synth")
DENYLIST_REL_PATHS: tuple[Path, ...] = (
    Path(".github") / "agents" / "routing-graph.yaml",
    Path(".github") / "agents" / "agent-router.agent.md",
    Path(".github") / "agents" / "evals" / "casos-roteamento.yaml",
)
DENYLIST_BASENAMES_LOWER: frozenset[str] = frozenset(
    {
        "routing-graph.yaml",
        "agent-router.agent.md",
        "casos-roteamento.yaml",
    }
)

FormatoDiagnostico = Literal["yaml", "md", "both"]
FORMATOS_DIAGNOSTICO: tuple[FormatoDiagnostico, ...] = ("yaml", "md", "both")
MAX_EXCERPT_LEN = 240
_REPO_ROOT_PADRAO: Path = Path(__file__).resolve().parents[5]


class SynthDiagnosticPathError(ValueError):
    """Violacao de guarda de path ou arquivo em denylist imutavel (exit code 5)."""

    exit_code = EXIT_PATH_PROIBIDO


@dataclass(frozen=True)
class ResultadoExportDiagnostico:
    yaml_path: Path | None
    md_path: Path | None
    yaml_content: str
    md_content: str


def _norm_key(p: Path) -> str:
    return str(p.resolve(strict=False)).replace("\\", "/").lower()


def _verificar_denylist(alvo: Path, raiz_repo: Path) -> None:
    """Garante que `alvo` nao coincide com nenhum arquivo protegido da denylist (mesmo com allow_root)."""
    alvo_key = _norm_key(alvo)
    nome_lower = alvo.name.lower()
    if nome_lower in DENYLIST_BASENAMES_LOWER:
        raise SynthDiagnosticPathError(
            "Escrita bloqueada: arquivo-alvo pertence a denylist imutavel de governanca."
        )
    for rel in DENYLIST_REL_PATHS:
        protegido_key = _norm_key(raiz_repo / rel)
        if alvo_key == protegido_key:
            raise SynthDiagnosticPathError(
                "Escrita bloqueada: caminho resolve para arquivo protegido da denylist."
            )


def ensure_allowed_write_path(
        target_path: str | Path,
        *,
        repo_root: Path | None = None,
        allow_root: bool | Path | str = False,
) -> Path:
    """Valida se target_path eh seguro para escrita, rejeitando traversal, symlinks externos e denylist."""
    raiz = (repo_root if repo_root is not None else _REPO_ROOT_PADRAO).resolve(strict=False)
    bruto = Path(target_path)
    if ".." in bruto.parts:
        raise SynthDiagnosticPathError("Escrita bloqueada: path traversal ('..') detectado.")

    candidato = bruto if bruto.is_absolute() else (raiz / bruto)
    resolvido = candidato.resolve(strict=False)

    # Denylist imutavel vale SEMPRE, inclusive com allow_root
    _verificar_denylist(resolvido, raiz)
    if candidato.exists() and candidato.is_symlink():
        real = candidato.resolve(strict=True)
        _verificar_denylist(real, raiz)
        if not real.is_relative_to(raiz):
            raise SynthDiagnosticPathError("Escrita bloqueada: symlink escapa da raiz permitida.")

    if isinstance(allow_root, (Path, str)) and not isinstance(allow_root, bool):
        raiz_custom = Path(allow_root).resolve(strict=False)
        _verificar_denylist(raiz_custom, raiz)
        if not resolvido.is_relative_to(raiz_custom):
            raise SynthDiagnosticPathError("Escrita bloqueada: destino fora do allow_root especificado.")
        return resolvido

    if allow_root is True:
        if not resolvido.is_relative_to(raiz):
            raise SynthDiagnosticPathError("Escrita bloqueada: destino fora da raiz do repositorio.")
        return resolvido

    # Modo padrao (allow_root=False): restrito a .github/agents/evals/synthetic/ ou .synth/
    dir_synthetic = (raiz / DEFAULT_DIAGNOSTIC_OUT_REL_DIR).resolve(strict=False)
    dir_dot_synth = (raiz / ALT_DIAGNOSTIC_OUT_REL_DIR).resolve(strict=False)
    if not (resolvido.is_relative_to(dir_synthetic) or resolvido.is_relative_to(dir_dot_synth)):
        raise SynthDiagnosticPathError(
            "Escrita bloqueada: --out deve residir em .github/agents/evals/synthetic/ ou .synth/."
        )
    return resolvido


ensure_allowed_Write_path = ensure_allowed_write_path


def sanitizar_excerto_md(texto: str, *, max_len: int = MAX_EXCERPT_LEN) -> str:
    """Escapa |, backticks (`) e < e trunca a max_len chars para tabelas/blocos Markdown."""
    if not texto:
        return ""
    limpo = " ".join(str(texto).splitlines()).strip()
    escapado = (
        limpo.replace("|", "\\|")
        .replace("`", "\\`")
        .replace("<", "<")
    )
    if len(escapado) > max_len:
        return escapado[:max_len]
    return escapado


def _fmt_float_opt(val: float | None) -> float | None:
    if val is None:
        return None
    return round(float(val), 6)


def serializar_diagnostico_dict(diag: DiagnosticoAssertividade) -> dict[str, Any]:
    """Converte DiagnosticoAssertividade em dicionario canonico pronto para YAML/JSON."""
    _payload: dict[str, Any] = {
        "aviso": diag.aviso,
        "colisoes": [
            {
                "edges": list(c.edges),
                "keyword_norm": c.keyword_norm,
                "tipo": c.tipo,
            }
            for c in diag.colisoes
        ],
        "diagnostic_id": diag.diagnostic_id,
        "diagnostic_version": int(diag.diagnostic_version),
        "divergencias_router_md": {
            "citados_fora_do_grafo": list(diag.divergencias_router_md.citados_fora_do_grafo),
            "nos_nao_citados": list(diag.divergencias_router_md.nos_nao_citados),
            "rotas_fantasma": list(diag.divergencias_router_md.rotas_fantasma),
        },
        "eval_run_id": diag.eval_run_id,
        "finished_at": diag.finished_at,
        "hashes": {
            "golden_set_sha256": diag.hashes.golden_set_sha256,
            "router_agent_sha256": diag.hashes.router_agent_sha256,
            "routing_graph_sha256": diag.hashes.routing_graph_sha256,
        },
        "matriz_confusao": {
            k: {obs: int(v) for obs, v in sorted(sub.items())}
            for k, sub in sorted(diag.matriz_confusao.items())
        },
        "orfas": {
            "sem_avaliacao": list(diag.orfas.sem_avaliacao),
            "sem_golden": list(diag.orfas.sem_golden),
            "uncoverable": list(diag.orfas.uncoverable),
        },
        "por_aresta": [
            {
                "edge_id": m.edge_id,
                "f1": _fmt_float_opt(m.f1),
                "fn": int(m.fn),
                "fp": int(m.fp),
                "para": m.para,
                "precision": _fmt_float_opt(m.precision),
                "recall": _fmt_float_opt(m.recall),
                "suporte": {
                    "manual": int(m.suporte.manual),
                    "routing_graph": int(m.suporte.routing_graph),
                },
                "tipo": m.tipo,
                "tp": int(m.tp),
                "unparseable": int(m.unparseable),
            }
            for m in diag.por_aresta
        ],
        "resumo": {
            "acuracia_global": round(float(diag.resumo.acuracia_global), 6),
            "cobertura_arestas_golden": round(float(diag.resumo.cobertura_arestas_golden), 6),
            "cobertura_arestas_total": round(float(diag.resumo.cobertura_arestas_total), 6),
            "total_avaliacoes": int(diag.resumo.total_avaliacoes),
        },
        "sugestoes": [
            {
                "alvo_ancora": s.alvo_ancora,
                "alvo_arquivo": s.alvo_arquivo,
                "codigo": s.codigo,
                "evidencias": list(s.evidencias),
                "id": s.id,
                "proposta_texto": s.proposta_texto,
                "severidade": s.severidade,
            }
            for s in diag.sugestoes
        ],
    }
    payload = _payload
    if diag.por_workflow or diag.colisoes_workflow:
        payload["resumo"].update(
            {
                "banner_coverage": _fmt_float_opt(diag.resumo.banner_coverage),
                "workflow_accuracy": _fmt_float_opt(diag.resumo.workflow_accuracy),
                "workflow_macro_f1": _fmt_float_opt(diag.resumo.workflow_macro_f1),
                "workflow_route_consistency_rate": _fmt_float_opt(diag.resumo.workflow_route_consistency_rate),
            }
        )
        payload["workflows"] = {
            "colisoes": [
                {
                    "edges": list(c.edges),
                    "gatilho_norm": c.gatilho_norm,
                    "tipo": c.tipo,
                    "workflows": list(c.workflows),
                }
                for c in diag.colisoes_workflow
            ],
            "matriz_confusao": {
                k: {o: int(v) for o, v in sorted(sub.items())}
                for k, sub in sorted(diag.matriz_confusao_workflow.items())
            },
            "metricas": [
                {
                    "f1": _fmt_float_opt(m.f1),
                    "fn": int(m.fn),
                    "fp": int(m.fp),
                    "precision": _fmt_float_opt(m.precision),
                    "recall": _fmt_float_opt(m.recall),
                    "suporte": int(m.suporte),
                    "tp": int(m.tp),
                    "workflow_id": m.workflow_id,
                }
                for m in diag.por_workflow
            ],
        }
    tem_skill_ab = bool(
        diag.por_skill_ab
        or diag.skill_ab_run_id
        or diag.skills_orfas.sem_cobertura_ab
        or diag.skills_orfas.uncoverable
    )
    if tem_skill_ab:
        payload["resumo"].update(
            {
                "mean_skill_delta_utility": _fmt_float_opt(diag.resumo.mean_skill_delta_utility),
                "skills_avaliadas": int(diag.resumo.skills_avaliadas),
                "skills_redundantes": int(diag.resumo.skills_redundantes),
                "skills_sem_cobertura": int(diag.resumo.skills_sem_cobertura),
            }
        )
        payload["skills_ab"] = {
            "metricas": [
                {
                    "casos": int(m.casos),
                    "mean_baseline_score": round(float(m.mean_baseline_score), 6),
                    "mean_delta_utility": round(float(m.mean_delta_utility), 6),
                    "mean_treatment_score": round(float(m.mean_treatment_score), 6),
                    "min_delta_utility": round(float(m.min_delta_utility), 6),
                    "missing_clauses": list(m.missing_clauses),
                    "passed": int(m.passed),
                    "redundant": bool(m.redundant),
                    "redundant_cases": int(m.redundant_cases),
                    "skill_name": m.skill_name,
                    "triggered_antipatterns": list(m.triggered_antipatterns),
                }
                for m in diag.por_skill_ab
            ],
            "orfas": {
                "sem_cobertura_ab": list(diag.skills_orfas.sem_cobertura_ab),
                "uncoverable": list(diag.skills_orfas.uncoverable),
            },
            "skill_ab_run_id": diag.skill_ab_run_id,
        }
    return payload


def renderizar_diagnostico_yaml(diag: DiagnosticoAssertividade) -> str:
    """Renderiza o diagnostico em YAML deterministico com sort_keys=True e LF."""
    payload = serializar_diagnostico_dict(diag)
    texto = yaml.safe_dump(
        payload,
        sort_keys=True,
        allow_unicode=True,
        default_flow_style=False,
    )
    return texto.replace("\r\n", "\n")


def _fmt_num_md(val: float | None) -> str:
    if val is None:
        return "null"
    return f"{float(val):.6f}"


def renderizar_diagnostico_md(diag: DiagnosticoAssertividade) -> str:
    """Renderiza o diagnostico em Markdown deterministico (mesmo modelo do YAML)."""
    linhas: list[str] = [
        f"# Diagnóstico de Assertividade de Roteamento — `{sanitizar_excerto_md(diag.eval_run_id)}`",
        "",
        f"> **Aviso**: {sanitizar_excerto_md(diag.aviso)}",
        "",
        "## Metadados e Hashes",
        f"- `diagnostic_version`: `{diag.diagnostic_version}`",
        f"- `diagnostic_id`: `{sanitizar_excerto_md(diag.diagnostic_id)}`",
        f"- `eval_run_id`: `{sanitizar_excerto_md(diag.eval_run_id)}`",
        f"- `finished_at`: `{sanitizar_excerto_md(diag.finished_at)}`",
        f"- `routing_graph_sha256`: `{sanitizar_excerto_md(diag.hashes.routing_graph_sha256)}`",
        f"- `router_agent_sha256`: `{sanitizar_excerto_md(diag.hashes.router_agent_sha256)}`",
        f"- `golden_set_sha256`: `{sanitizar_excerto_md(diag.hashes.golden_set_sha256)}`",
        "",
        "## Resumo Executivo",
        f"- **Total de Avaliações**: {diag.resumo.total_avaliacoes}",
        f"- **Acurácia Global**: {_fmt_num_md(diag.resumo.acuracia_global)}",
        f"- **Cobertura de Arestas (Golden)**: {_fmt_num_md(diag.resumo.cobertura_arestas_golden)}",
        f"- **Cobertura de Arestas (Total)**: {_fmt_num_md(diag.resumo.cobertura_arestas_total)}",
        "",
        "## Métricas por Aresta",
        "| edge_id | para | tipo | sup_manual | sup_graph | tp | fp | fn | precision | recall | f1 | unparseable |",
        "| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for m in diag.por_aresta:
        linhas.append(
            f"| {sanitizar_excerto_md(m.edge_id)} | {sanitizar_excerto_md(m.para)} | "
            f"{sanitizar_excerto_md(m.tipo)} | {m.suporte.manual} | {m.suporte.routing_graph} | "
            f"{m.tp} | {m.fp} | {m.fn} | {_fmt_num_md(m.precision)} | "
            f"{_fmt_num_md(m.recall)} | {_fmt_num_md(m.f1)} | {m.unparseable} |"
        )

    linhas.extend(["", "## Rotas Órfãs"])
    linhas.append(f"- `sem_golden`: {list(diag.orfas.sem_golden)}")
    linhas.append(f"- `sem_avaliacao`: {list(diag.orfas.sem_avaliacao)}")
    linhas.append(f"- `uncoverable`: {list(diag.orfas.uncoverable)}")

    linhas.extend(["", "## Colisões Estáticas de Keywords"])
    if not diag.colisoes:
        linhas.append("- Nenhuma colisão detectada.")
    else:
        for col in diag.colisoes:
            kw_s = sanitizar_excerto_md(col.keyword_norm)
            linhas.append(f"- `{kw_s}` ({col.tipo}): {list(col.edges)}")

    if diag.por_workflow or diag.colisoes_workflow:
        linhas.extend(
            [
                "",
                "## Workflows",
                f"- **Macro-F1**: {_fmt_num_md(diag.resumo.workflow_macro_f1)}",
                f"- **Acurácia**: {_fmt_num_md(diag.resumo.workflow_accuracy)}",
                f"- **Consistência workflow×rota**: {_fmt_num_md(diag.resumo.workflow_route_consistency_rate)}",
                f"- **Banner coverage**: {_fmt_num_md(diag.resumo.banner_coverage)}",
                "",
                "| workflow_id | suporte | tp | fp | fn | precision | recall | f1 |",
                "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for m in diag.por_workflow:
            linhas.append(
                f"| {sanitizar_excerto_md(m.workflow_id)} | {m.suporte} | {m.tp} | {m.fp} | {m.fn} | "
                f"{_fmt_num_md(m.precision)} | {_fmt_num_md(m.recall)} | {_fmt_num_md(m.f1)} |"
            )
        linhas.extend(["", "### Colisões de Gatilhos de Workflows"])
        if not diag.colisoes_workflow:
            linhas.append("- Nenhuma colisão detectada.")
        else:
            for c in diag.colisoes_workflow:
                linhas.append(
                    f"- `{sanitizar_excerto_md(c.gatilho_norm)}` ({c.tipo}): {list(c.workflows)} {list(c.edges)}"
                )

    tem_skill_ab = bool(
        diag.por_skill_ab
        or diag.skill_ab_run_id
        or diag.skills_orfas.sem_cobertura_ab
        or diag.skills_orfas.uncoverable
    )
    if tem_skill_ab:
        linhas.extend(
            [
                "",
                "## Avaliação Pareada de Skills (A/B)",
                f"- `skill_ab_run_id`: `{sanitizar_excerto_md(diag.skill_ab_run_id or 'none')}`",
                f"- **Skills Avaliadas**: {diag.resumo.skills_avaliadas}",
                f"- **Skills Redundantes**: {diag.resumo.skills_redundantes}",
                f"- **Skills sem Cobertura A/B**: {diag.resumo.skills_sem_cobertura}",
                f"- **Delta Utility Médio**: {_fmt_num_md(diag.resumo.mean_skill_delta_utility)}",
                f"- `sem_cobertura_ab`: {list(diag.skills_orfas.sem_cobertura_ab)}",
                f"- `uncoverable`: {list(diag.skills_orfas.uncoverable)}",
            ]
        )
        if diag.por_skill_ab:
            linhas.extend(
                [
                    "",
                    "| skill_name | casos | passed | baseline | treatment | delta_utility | min_delta | redundant |",
                    "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |",
                ]
            )
            for m in diag.por_skill_ab:
                linhas.append(
                    f"| {sanitizar_excerto_md(m.skill_name)} | {m.casos} | {m.passed} | "
                    f"{_fmt_num_md(m.mean_baseline_score)} | {_fmt_num_md(m.mean_treatment_score)} | "
                    f"{_fmt_num_md(m.mean_delta_utility)} | {_fmt_num_md(m.min_delta_utility)} | "
                    f"{'sim' if m.redundant else 'nao'} |"
                )

    linhas.extend(["", "## Divergências `routing-graph.yaml` × `agent-router.agent.md`"])
    linhas.append(f"- `nos_nao_citados`: {list(diag.divergencias_router_md.nos_nao_citados)}")
    linhas.append(f"- `citados_fora_do_grafo`: {list(diag.divergencias_router_md.citados_fora_do_grafo)}")
    linhas.append(f"- `rotas_fantasma`: {list(diag.divergencias_router_md.rotas_fantasma)}")

    linhas.extend([
        "",
        "## Sugestões Acionáveis (Consultivas)",
        "| id | codigo | severidade | alvo_arquivo | alvo_ancora | proposta_texto |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ])
    for s in diag.sugestoes:
        linhas.append(
            f"| {sanitizar_excerto_md(s.id)} | {sanitizar_excerto_md(s.codigo)} | "
            f"{sanitizar_excerto_md(s.severidade)} | {sanitizar_excerto_md(s.alvo_arquivo)} | "
            f"{sanitizar_excerto_md(s.alvo_ancora)} | {sanitizar_excerto_md(s.proposta_texto)} |"
        )

    return "\n".join(linhas) + "\n"


def exportar_diagnostico(
        diag: DiagnosticoAssertividade,
        *,
        out_dir: str | Path | None = None,
        formato: FormatoDiagnostico = "both",
        repo_root: Path | None = None,
        allow_root: bool | Path | str = False,
) -> ResultadoExportDiagnostico:
    """Exporta diagnostic-<eval_run_id>.yaml e/ou .md com escrita deterministica LF e guardas de path."""
    if formato not in FORMATOS_DIAGNOSTICO:
        raise ValueError(f"Formato invalido: {formato!r}. Esperado um de {FORMATOS_DIAGNOSTICO}.")

    raiz = (repo_root if repo_root is not None else _REPO_ROOT_PADRAO).resolve(strict=False)
    if out_dir is None:
        if isinstance(allow_root, (Path, str)) and not isinstance(allow_root, bool):
            base_out: Path = Path(allow_root)
        else:
            base_out = raiz / DEFAULT_DIAGNOSTIC_OUT_REL_DIR
    else:
        bruto_out = Path(out_dir)
        if ".." in bruto_out.parts:
            raise SynthDiagnosticPathError("Escrita bloqueada: path traversal em --out.")
        # Se o usuario passou um caminho de arquivo em denylist diretamente em --out, falha imediatamente
        cand_out = bruto_out if bruto_out.is_absolute() else (raiz / bruto_out)
        _verificar_denylist(cand_out.resolve(strict=False), raiz)
        base_out = cand_out

    dir_validado = ensure_allowed_write_path(base_out, repo_root=raiz, allow_root=allow_root)

    nome_base = f"diagnostic-{diag.eval_run_id}"
    alvo_yaml = ensure_allowed_write_path(dir_validado / f"{nome_base}.yaml", repo_root=raiz, allow_root=allow_root)
    alvo_md = ensure_allowed_write_path(dir_validado / f"{nome_base}.md", repo_root=raiz, allow_root=allow_root)

    conteudo_yaml = renderizar_diagnostico_yaml(diag)
    conteudo_md = renderizar_diagnostico_md(diag)

    dir_validado.mkdir(parents=True, exist_ok=True)

    gravado_yaml: Path | None = None
    gravado_md: Path | None = None

    if formato in ("yaml", "both"):
        with open(alvo_yaml, "w", encoding="utf-8", newline="\n") as fh_y:
            fh_y.write(conteudo_yaml)
        gravado_yaml = alvo_yaml

    if formato in ("md", "both"):
        with open(alvo_md, "w", encoding="utf-8", newline="\n") as fh_m:
            fh_m.write(conteudo_md)
        gravado_md = alvo_md

    return ResultadoExportDiagnostico(
        yaml_path=gravado_yaml,
        md_path=gravado_md,
        yaml_content=conteudo_yaml,
        md_content=conteudo_md,
    )
