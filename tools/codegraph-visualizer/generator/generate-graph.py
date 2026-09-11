#!/usr/bin/env python3
"""
Generator de Grafo Unificado Cross-Repo (Material 3 + vis-network + 3D)
======================================================================
Lê os bancos de dados SQLite `.codegraph/graph.db` de qualquer conjunto de
projetos registrados dinamicamente no `catalog.local.yaml` / `catalog.yaml`,
passados via CLI (--db ou --projects) ou detectados no workspace atual.
Aplica taxonomia de acoplamento (Tight/Loose/Eventual), ingestão de OpenAPI e contratos REST,
cálculo de métricas arquiteturais de Martin (Ca/Ce/I/A/D), detecção de ciclos e verificação de fronteiras (CI Gate).

Uso:
  python generate-graph.py                                 # Descoberta automática via catalog.local.yaml
  python generate-graph.py --open                          # Abre no navegador após gerar
  python generate-graph.py --output dist/index.html        # Especifica arquivo de saída
  python generate-graph.py --db /path/proj1 /path/proj2    # Caminhos diretos de projetos/bancos
  python generate-graph.py --openapi api1.json api2.yaml   # Ingestão de specs OpenAPI / Swagger
  python generate-graph.py --diff HEAD~1 --open            # Destaque triplo de diff Git (Verde/Âmbar/Vermelho)
  python generate-graph.py --ci                            # Valida regras de fronteira e retorna exit 1 se violado
"""

import os
import sys
import time
import json
import sqlite3
import argparse
import subprocess
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional, Set, Tuple

# Módulos locais de extensão
try:
    from contract_parser import ContractCorrelator, OpenApiParser, AsyncApiParser
    from metrics_calculator import MetricsCalculator
    from diff_checker import DiffChecker
    from template_bundler import TemplateBundler
except ImportError:
    # Ajuste de path para execução standalone
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from contract_parser import ContractCorrelator, OpenApiParser, AsyncApiParser
    from metrics_calculator import MetricsCalculator
    from diff_checker import DiffChecker
    from template_bundler import TemplateBundler

DEFAULT_PALETTE = [
    {"color": "#1976D2", "bgColor": "#E3F2FD", "borderColor": "#1565C0", "badgeClass": "mat-chip-orc"},
    {"color": "#2E7D32", "bgColor": "#E8F5E9", "borderColor": "#1B5E20", "badgeClass": "mat-chip-vist"},
    {"color": "#E65100", "bgColor": "#FFF3E0", "borderColor": "#BF360C", "badgeClass": "mat-chip-perm"},
    {"color": "#7B1FA2", "bgColor": "#F3E5F5", "borderColor": "#4A148C", "badgeClass": "mat-chip-purple"},
    {"color": "#00838F", "bgColor": "#E0F7FA", "borderColor": "#006064", "badgeClass": "mat-chip-cyan"},
    {"color": "#C2185B", "bgColor": "#FCE4EC", "borderColor": "#880E4F", "badgeClass": "mat-chip-pink"},
    {"color": "#5D4037", "bgColor": "#EFEBE9", "borderColor": "#3E2723", "badgeClass": "mat-chip-brown"},
    {"color": "#455A64", "bgColor": "#ECEFF1", "borderColor": "#263238", "badgeClass": "mat-chip-bluegray"},
]


def find_workspace_root(start_path: Optional[Path] = None) -> Path:
    """Localiza a raiz do repositório/workspace navegando diretórios ancestrais."""
    current = (start_path or Path(__file__)).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs" / "ai-context" / "catalog.yaml").exists() or \
           (parent / "docs" / "ai-context" / "catalog.local.yaml").exists() or \
           (parent / "CLAUDE.md").exists():
            return parent
    return Path.cwd().resolve()


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """Lê arquivo YAML com suporte a PyYAML ou fallback seguro."""
    if not file_path.exists():
        return {}
    try:
        import yaml
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        print("[WARN] Módulo 'yaml' (PyYAML) não disponível. Tentando parse básico.")
        return {}
    except Exception as e:
        print(f"[WARN] Erro ao carregar {file_path}: {e}")
        return {}


def load_catalog_projects(workspace_root: Path, custom_catalog_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Carrega projetos dinamicamente mesclando catalog.yaml e catalog.local.yaml (R-043)."""
    projects_raw = []
    
    if custom_catalog_path:
        cat_file = Path(custom_catalog_path).resolve()
        data = load_yaml_file(cat_file)
        projects_raw.extend(data.get("projetos", []))
    else:
        # Prioridade 1: catalog.local.yaml (overlay local, gitignored, R-043)
        catalog_local_path = workspace_root / ".github" / "projects.local.yaml"
        if not catalog_local_path.exists():
            catalog_local_path = workspace_root / "docs" / "ai-context" / "catalog.local.yaml"
        if catalog_local_path.exists():
            data = load_yaml_file(catalog_local_path)
            for p in data.get("projetos", []):
                projects_raw.append(p)

        # Prioridade 2: catalog.yaml (compartilhado)
        catalog_path = workspace_root / "docs" / "ai-context" / "catalog.yaml"
        if catalog_path.exists():
            data = load_yaml_file(catalog_path)
            for p in data.get("projetos", []):
                p_id = p.get("id") or p.get("name")
                if not any((x.get("id") or x.get("name")) == p_id for x in projects_raw):
                    projects_raw.append(p)

    resolved = []
    for idx, p in enumerate(projects_raw):
        p_id = str(p.get("id") or p.get("name") or f"proj_{idx}")
        p_name = str(p.get("name") or p_id)
        p_disp = str(p.get("name") or p_id)
        p_type = str(p.get("tipo") or p.get("type") or "Module")
        
        path_externo = p.get("path_externo")
        if p.get("db"):
            db_path = Path(p["db"]).resolve()
        elif path_externo:
            ext_path = Path(path_externo)
            if not ext_path.is_absolute():
                ext_path = (workspace_root / ext_path).resolve()
            db_path = ext_path / ".codegraph" / "graph.db"
        else:
            db_path = (workspace_root / p_id / ".codegraph" / "graph.db").resolve()

        resolved.append({
            "id": p_id,
            "name": p_id,
            "displayName": p_disp,
            "type": p_type,
            "path": str(path_externo) if path_externo else "",
            "db": str(db_path),
            "palette": p.get("palette") or DEFAULT_PALETTE[idx % len(DEFAULT_PALETTE)]
        })

    return resolved


def resolve_projects(args: argparse.Namespace, workspace_root: Path) -> List[Dict[str, Any]]:
    """Determina a lista de projetos e seus respectivos bancos SQLite conforme argumentos de CLI."""
    # Opção A: Lista explícita de bancos ou diretórios passados via --db
    if args.db:
        projects_cfg = []
        for idx, item in enumerate(args.db):
            p_path = Path(item).resolve()
            if p_path.is_file() and p_path.name.endswith(".db"):
                db_file = p_path
                proj_name = p_path.parent.parent.name if p_path.parent.name == ".codegraph" else p_path.stem
            elif p_path.is_dir():
                db_file = p_path / ".codegraph" / "graph.db"
                proj_name = p_path.name
            else:
                db_file = p_path
                proj_name = p_path.stem

            projects_cfg.append({
                "id": proj_name,
                "name": proj_name,
                "displayName": proj_name,
                "type": "Module",
                "path": str(p_path if p_path.is_dir() else p_path.parent),
                "db": str(db_file),
                "palette": DEFAULT_PALETTE[idx % len(DEFAULT_PALETTE)]
            })
        return projects_cfg

    # Opção B: Projetos do catálogo (catalog.local.yaml / catalog.yaml)
    projects_cfg = load_catalog_projects(workspace_root, args.catalog)

    # Opção C: Filtro por nomes/IDs específicos se --projects foi passado
    if args.projects:
        filter_keys = set(k.strip() for k in args.projects.split(",") if k.strip())
        projects_cfg = [p for p in projects_cfg if p["id"] in filter_keys or p["name"] in filter_keys or p["displayName"] in filter_keys]

    # Opção D: Fallback standalone — verifica se o diretório atual de execução possui .codegraph/graph.db
    if not projects_cfg:
        cwd_db = Path.cwd() / ".codegraph" / "graph.db"
        if cwd_db.exists():
            proj_name = Path.cwd().name
            projects_cfg.append({
                "id": proj_name,
                "name": proj_name,
                "displayName": proj_name,
                "type": "Standalone",
                "path": str(Path.cwd()),
                "db": str(cwd_db),
                "palette": DEFAULT_PALETTE[0]
            })

    return projects_cfg


def load_bridges_file(bridges_path: Optional[str] = None, workspace_root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Carrega o registro de pontes REST cross-repo de forma desacoplada."""
    # 1. Caminho explícito via argumento CLI
    if bridges_path and os.path.exists(bridges_path):
        try:
            with open(bridges_path, "r", encoding="utf-8") as f:
                return json.load(f) or []
        except Exception as e:
            print(f"[WARN] Erro ao ler arquivo de pontes '{bridges_path}': {e}")

    # 2. Arquivo local bridges.local.json (gitignored, específico do desenvolvedor)
    vis_dir = Path(__file__).resolve().parent.parent
    local_bridges = vis_dir / "bridges.local.json"
    if local_bridges.exists():
        try:
            with open(local_bridges, "r", encoding="utf-8") as f:
                return json.load(f) or []
        except Exception:
            pass

    # 3. Arquivo padrão bridges.json
    default_bridges = vis_dir / "bridges.json"
    if default_bridges.exists():
        try:
            with open(default_bridges, "r", encoding="utf-8") as f:
                return json.load(f) or []
        except Exception:
            pass

    return []


def get_git_diff_changed_files(git_ref: str = "HEAD") -> Set[str]:
    """Identifica arquivos modificados no Git para destacar no modo Diff / Blast Radius."""
    changed_files = set()
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", git_ref],
            text=True,
            stderr=subprocess.DEVNULL
        )
        for line in out.splitlines():
            if line.strip():
                changed_files.add(line.strip().replace("\\", "/"))
    except Exception:
        pass
    return changed_files


def classify_coupling(fan_in: int, fan_out: int, is_bridge: bool, is_cycle: bool) -> str:
    """Classifica a força de acoplamento de forma determinística."""
    if is_cycle:
        return "circular"
    if is_bridge or fan_in >= 8:
        return "tight"
    if fan_in <= 3 and fan_out <= 3:
        return "loose"
    return "eventual"


def _process_single_project_db(
    item: Tuple[int, Dict[str, Any]],
    diff_summary: Dict[str, Set[str]],
    has_diff: bool
) -> Dict[str, Any]:
    """Lê e processa nós e arestas de um único banco SQLite de projeto com otimizações em memória."""
    idx, cfg = item
    prefix = f"p{idx}_"
    proj_name = cfg["name"]
    db_path = cfg["db"]

    if not os.path.exists(db_path):
        return {
            "idx": idx,
            "cfg": cfg,
            "status": "not_found",
            "nodes": [],
            "edges": [],
            "name_mappings": [],
            "db_path": db_path
        }

    palette = cfg.get("palette") or DEFAULT_PALETTE[idx % len(DEFAULT_PALETTE)]

    try:
        conn = sqlite3.connect(db_path)
        # Otimizações em memória para SQLite read-only (alto throughput e saturação de CPU)
        conn.execute("PRAGMA query_only = ON")
        conn.execute("PRAGMA cache_size = -64000")   # 64 MB em RAM
        conn.execute("PRAGMA mmap_size = 268435456") # 256 MB memory-mapped I/O
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA synchronous = OFF")
        cur = conn.cursor()

        # Leitura única da tabela edges e cálculo de fan-in/fan-out diretamente em memória
        cur.execute("SELECT id, source_id, target_id, kind FROM edges")
        raw_edges = cur.fetchall()

        fan_in_map = defaultdict(int)
        fan_out_map = defaultdict(int)
        proj_edges = []

        for eid, src, tgt, ekind in raw_edges:
            fan_out_map[src] += 1
            fan_in_map[tgt] += 1
            proj_edges.append({
                "id": f"{prefix}e_{eid}",
                "from": f"{prefix}{src}",
                "to": f"{prefix}{tgt}",
                "kind": ekind,
                "crossRepo": False,
                "color": {"color": "#B0BEC5", "highlight": "#1E88E5", "hover": "#90A4AE"},
                "arrows": {"to": {"enabled": True, "scaleFactor": 0.6}},
                "width": 1
            })

        # Símbolos estruturais
        cur.execute("SELECT id, name, kind, file, line, role, qualified_name FROM nodes WHERE kind in ('class', 'interface', 'enum', 'file', 'function', 'struct', 'trait')")
        rows = cur.fetchall()
        proj_nodes = []
        name_mappings = []

        for r in rows:
            nid, name, kind, file, line, role, qname = r
            full_id = f"{prefix}{nid}"
            name_mappings.append(((proj_name, name), full_id))
            if qname:
                name_mappings.append(((proj_name, qname), full_id))

            fin = fan_in_map[nid]
            fout = fan_out_map[nid]

            is_ctrl = "Controller" in name or "Resource" in name
            is_svc = "Service" in name or "Manager" in name or "Provider" in name
            is_repo = "Repository" in name or "Dao" in name
            is_comp = "Component" in name or "Directive" in name or "Pipe" in name

            node_type_tag = "Controller" if is_ctrl else ("Service" if is_svc else ("Repository" if is_repo else ("Component" if is_comp else kind.capitalize())))
            coupling_tier = classify_coupling(fin, fout, False, False)

            # Fast path de diff: se não há arquivos no diff, ignora comparações de string
            if has_diff:
                norm_file = (file or "").replace("\\", "/")
                is_added = any(cf in norm_file for cf in diff_summary["added"])
                is_modified = any(cf in norm_file for cf in diff_summary["modified"])
                is_deleted = any(cf in norm_file for cf in diff_summary["deleted"])
                is_diff_changed = is_added or is_modified or is_deleted
                diff_tag = "added" if is_added else ("modified" if is_modified else ("deleted" if is_deleted else "unchanged"))
                bg_color = "#D1FAE5" if is_added else ("#FEF3C7" if is_modified else ("#FEE2E2" if is_deleted else palette["bgColor"]))
                border_color = "#10B981" if is_added else ("#F59E0B" if is_modified else ("#DC2626" if is_deleted else palette["borderColor"]))
                highlight_bg = "#059669" if is_added else ("#D97706" if is_modified else ("#DC2626" if is_deleted else palette["color"]))
                font_color = "#065F46" if is_added else ("#92400E" if is_modified else ("#991B1B" if is_deleted else "#1A202C"))
            else:
                is_diff_changed = False
                diff_tag = "unchanged"
                bg_color = palette["bgColor"]
                border_color = palette["borderColor"]
                highlight_bg = palette["color"]
                font_color = "#1A202C"

            node_obj = {
                "id": full_id,
                "label": name,
                "project": proj_name,
                "projectDisplayName": cfg.get("displayName", proj_name),
                "projectType": cfg.get("type", "Module"),
                "kind": kind,
                "typeTag": node_type_tag,
                "file": file,
                "line": line or 1,
                "role": role or "core",
                "coupling": coupling_tier,
                "fanIn": fin,
                "fanOut": fout,
                "isDiffChanged": is_diff_changed,
                "diffStatus": diff_tag,
                "title": f"<b>{name}</b> ({node_type_tag})<br>📁 {file}:{line}<br>📦 {cfg.get('displayName', proj_name)}<br>📊 Fan-In: {fin} | Fan-Out: {fout}<br>⚡ Acoplamento: {coupling_tier.upper()}" + (f"<br>🚩 Diff Git: {diff_tag.upper()}" if is_diff_changed else ""),
                "color": {
                    "background": bg_color,
                    "border": border_color,
                    "highlight": {
                        "background": highlight_bg,
                        "border": "#212121"
                    },
                    "hover": {
                        "background": bg_color,
                        "border": border_color
                    }
                },
                "font": {
                    "color": font_color,
                    "size": 13 if is_ctrl or is_svc else 11,
                    "face": "Roboto, 'Segoe UI', sans-serif"
                },
                "shape": "box",
                "margin": 10 if is_ctrl or is_svc else 6,
                "borderWidth": 3.0 if is_diff_changed else (2.5 if is_ctrl or is_svc else 1.5),
                "borderWidthSelected": 4.0
            }
            proj_nodes.append(node_obj)

        conn.close()
        return {
            "idx": idx,
            "cfg": cfg,
            "status": "ok",
            "nodes": proj_nodes,
            "edges": proj_edges,
            "name_mappings": name_mappings,
            "db_path": db_path
        }
    except Exception as e:
        print(f"[WARN] Falha ao processar banco SQLite '{db_path}': {e}")
        return {
            "idx": idx,
            "cfg": cfg,
            "status": "error",
            "nodes": [],
            "edges": [],
            "name_mappings": [],
            "db_path": db_path
        }


def build_unified_visualization(
    projects_cfg: List[Dict[str, Any]],
    cross_bridges: List[Dict[str, Any]],
    output_html_path: str,
    diff_ref: Optional[str] = None,
    openapi_specs: Optional[List[Any]] = None,
    workspace_root: Optional[Path] = None,
    is_ci_mode: bool = False,
    workers: Optional[int] = None
) -> None:
    """Processa nós e arestas de todos os bancos de dados configurados em paralelo e renderiza o HTML."""
    start_time = time.time()
    all_nodes = []
    all_edges = []
    node_name_to_id = {}
    valid_classes = []
    ws_root = workspace_root or find_workspace_root()
    
    # Extração de Diff Git Triplo (Adicionados, Modificados, Removidos)
    diff_summary = DiffChecker.get_detailed_git_diff(diff_ref, ws_root) if diff_ref else {"added": set(), "modified": set(), "deleted": set()}
    has_diff = bool(diff_summary["added"] or diff_summary["modified"] or diff_summary["deleted"])
    changed_files = diff_summary["added"] | diff_summary["modified"] | diff_summary["deleted"]

    max_workers = workers or min(32, (os.cpu_count() or 4) * 2)

    # Processamento paralelo de todos os bancos SQLite de projetos utilizando ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        process_func = lambda item: _process_single_project_db(item, diff_summary, has_diff)
        results = list(executor.map(process_func, enumerate(projects_cfg)))

    # Ordenação determinística por índice original do catálogo
    results.sort(key=lambda r: r["idx"])

    processed_count = 0
    for r in results:
        cfg = r["cfg"]
        proj_name = cfg["name"]
        if r["status"] == "not_found":
            print(f"[INFO] Banco de dados não encontrado para '{cfg.get('displayName', proj_name)}':")
            print(f"       Caminho: {r['db_path']}")
            print(f"       Execute 'codegraph build .' no repositório para gerar o grafo.")
            continue
        if r["status"] == "ok":
            processed_count += 1
            all_nodes.extend(r["nodes"])
            valid_classes.extend(r["nodes"])
            all_edges.extend(r["edges"])
            for key, val in r["name_mappings"]:
                node_name_to_id[key] = val

    if processed_count == 0:
        print("\n[ERRO] Nenhum banco de dados '.codegraph/graph.db' válido pôde ser lido.")
        print("Instruções de resolução:")
        print("  1. Gere o grafo de conhecimento no repositório desejado com:")
        print("     codegraph build .")
        print("  2. Registre os caminhos dos projetos em 'docs/ai-context/catalog.local.yaml'.")
        print("  3. Ou passe diretamente o caminho do banco/projeto via CLI:")
        print("     python generate-graph.py --db /caminho/do/projeto\n")
        sys.exit(1)

    # Ingestão Automática de Contratos OpenAPI / Swagger / AsyncAPI (concorrente multi-thread)
    auto_bridges = ContractCorrelator.correlate_projects(projects_cfg, openapi_specs, max_workers=max_workers)
    all_bridges_to_apply = list(cross_bridges)
    
    # Adiciona pontes auto-detectadas sem duplicar
    existing_pairs = set((b.get("src_proj"), b.get("src_symbol"), b.get("tgt_proj"), b.get("tgt_symbol")) for b in cross_bridges)
    for ab in auto_bridges:
        pair = (ab.get("src_proj"), ab.get("src_symbol"), ab.get("tgt_proj"), ab.get("tgt_symbol"))
        if pair not in existing_pairs:
            all_bridges_to_apply.append(ab)
            existing_pairs.add(pair)

    # Injeção das Pontes REST Cross-Repo
    bridge_node_ids = set()
    for idx, b in enumerate(all_bridges_to_apply):
        src_id = node_name_to_id.get((b.get("src_proj"), b.get("src_symbol")))
        tgt_id = node_name_to_id.get((b.get("tgt_proj"), b.get("tgt_symbol")))
        if src_id and tgt_id:
            bridge_edge = {
                "id": f"bridge_{idx}",
                "from": src_id,
                "to": tgt_id,
                "kind": "cross_repo_rest",
                "crossRepo": True,
                "label": b.get("label", "REST Call"),
                "description": b.get("description", ""),
                "protocol": b.get("protocol", "HTTP REST"),
                "status": b.get("status", "COMPATIBLE"),
                "color": {"color": "#E91E63", "highlight": "#C2185B", "hover": "#FF4081"},
                "width": 3.5,
                "dashes": True,
                "arrows": {"to": {"enabled": True, "scaleFactor": 1.1}},
                "font": {
                    "color": "#C2185B",
                    "size": 11,
                    "face": "Roboto, sans-serif",
                    "strokeWidth": 3,
                    "strokeColor": "#FFFFFF",
                    "align": "horizontal"
                }
            }
            all_edges.append(bridge_edge)
            bridge_node_ids.add(src_id)
            bridge_node_ids.add(tgt_id)

    valid_node_ids = set(n["id"] for n in valid_classes)
    final_edges = [e for e in all_edges if e["from"] in valid_node_ids and e["to"] in valid_node_ids]

    # Cálculo de Métricas Arquiteturais de Martin (Ca/Ce/I/A/D)
    module_metrics = MetricsCalculator.calculate_module_metrics(valid_classes, final_edges)

    # Detecção de Ciclos de Dependência (SCC Tarjan)
    detected_cycles, cycle_node_ids, cycle_edge_ids = MetricsCalculator.detect_dependency_cycles(valid_classes, final_edges)
    for e in final_edges:
        if e.get("id") in cycle_edge_ids:
            e["isCycle"] = True
            e["color"] = {"color": "#DC2626", "highlight": "#991B1B", "hover": "#EF4444"}
            e["width"] = 2.5
            e["dashes"] = [4, 4]

    # Verificação de Violações de Fronteiras Arquiteturais (CI Gate)
    boundary_violations = DiffChecker.check_boundary_violations(valid_classes, final_edges, ws_root)

    # Renderizar template HTML modularmente via TemplateBundler
    template_dir = Path(__file__).resolve().parent.parent / "template"
    if not template_dir.exists():
        print(f"[ERRO] Diretório de template não encontrado em: {template_dir}")
        sys.exit(1)

    active_projects = [p for p in projects_cfg if os.path.exists(p["db"])]
    filled_html = TemplateBundler.bundle_standalone_html(
        template_dir=template_dir,
        active_projects=active_projects,
        valid_classes=valid_classes,
        final_edges=final_edges,
        module_metrics=module_metrics,
        detected_cycles=detected_cycles,
        boundary_violations=boundary_violations
    )

    out_file = Path(output_html_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(filled_html)

    elapsed_time = time.time() - start_time
    print(f"\n[OK] Grafo Unificado Material 3 (2D + 3D) gerado com sucesso em {elapsed_time:.2f}s!")
    print(f"     Arquivo: {out_file}")
    print(f"     Projetos processados: {processed_count} (Workers/Threads: {max_workers})")
    print(f"     Nós: {len(valid_classes)} | Arestas: {len(final_edges)} | Pontes REST: {len(bridge_node_ids)}")
    print(f"     Métricas de Módulos (Martin): {len(module_metrics)} pacotes calculados")
    print(f"     Ciclos Detectados: {len(detected_cycles)} | Violações de Boundary: {len(boundary_violations)}")
    if auto_bridges:
        print(f"     Pontes REST Auto-Detectadas (OpenAPI/Código): {len(auto_bridges)}")
    if changed_files:
        print(f"     Diff Ativo ({diff_ref}): {len(changed_files)} arquivos destacados.")

    # CI Gate Check
    if is_ci_mode:
        if boundary_violations:
            print("\n❌ [CI GATE FAILED] Violações de fronteiras arquiteturais detectadas:")
            for idx, v in enumerate(boundary_violations, 1):
                print(f"   {idx}. {v['rule']} (Origem: {v['source_node']} ➔ Destino: {v['target_node']})")
            sys.exit(1)
        else:
            print("\n✅ [CI GATE PASSED] Todas as regras de fronteira arquitetural foram atendidas com sucesso.")


if __name__ == "__main__":
    workspace_root = find_workspace_root()
    default_output = str(Path(__file__).resolve().parent.parent / "dist" / "index.html")

    parser = argparse.ArgumentParser(description="Gerar visualização unificada de grafos cross-repo de forma desacoplada.")
    parser.add_argument("--output", "-o", default=default_output, help="Caminho do arquivo HTML de saída (padrão: tools/codegraph-visualizer/dist/index.html)")
    parser.add_argument("--workspace", "-w", default=None, help="Caminho raiz do workspace de governança")
    parser.add_argument("--catalog", "-c", default=None, help="Caminho explícito de arquivo catalog.yaml / catalog.local.yaml")
    parser.add_argument("--projects", "-p", default=None, help="Filtro de IDs de projetos separados por vírgula (ex: projA,projB)")
    parser.add_argument("--db", nargs="+", default=None, help="Caminho(s) explícito(s) de banco(s) .codegraph/graph.db ou pastas de projeto")
    parser.add_argument("--openapi", nargs="+", default=None, help="Arquivo(s) OpenAPI / Swagger / AsyncAPI (.json/.yaml) para ingestão automática de contratos")
    parser.add_argument("--bridges", "-b", default=None, help="Caminho do arquivo JSON de pontes cross-repo")
    parser.add_argument("--diff", "-d", default=None, help="Git ref (ex: HEAD~1, master) para destacar blast radius do diff")
    parser.add_argument("--ci", "--check-boundaries", action="store_true", dest="ci", help="Modo CI Gate: falha com exit code 1 se houver violações de manifesto.boundaries")
    parser.add_argument("--workers", "-j", type=int, default=None, help="Número de threads/workers paralelos para processar projetos e I/O (padrão: auto baseado em CPU cores)")
    parser.add_argument("--open", action="store_true", help="Abrir visualizador no navegador automaticamente após geração")

    args = parser.parse_args()

    if args.workspace:
        workspace_root = Path(args.workspace).resolve()

    projects_cfg = resolve_projects(args, workspace_root)
    loaded_bridges = load_bridges_file(args.bridges, workspace_root)
    openapi_specs = [Path(p).resolve() for p in args.openapi] if args.openapi else None

    build_unified_visualization(
        projects_cfg,
        loaded_bridges,
        args.output,
        diff_ref=args.diff,
        openapi_specs=openapi_specs,
        workspace_root=workspace_root,
        is_ci_mode=args.ci,
        workers=args.workers
    )

    if args.open:
        out_path = Path(args.output).resolve()
        if sys.platform.startswith("win"):
            os.system(f'start "" "{out_path}"')
        elif sys.platform.startswith("darwin"):
            os.system(f'open "{out_path}"')
        else:
            os.system(f'xdg-open "{out_path}"')

