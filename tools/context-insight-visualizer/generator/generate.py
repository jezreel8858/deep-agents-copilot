#!/usr/bin/env python3
"""
generate.py — CLI Principal do Context Insight Visualizer
=========================================================
Gera o dashboard standalone em HTML a partir dos dados locais do Context Mode.

Uso:
    python generate.py
    python generate.py --output dist/context-insight.html --serve --port 4747 --open
    python generate.py --sessions-dir ~/.claude/context-mode/sessions
"""

import argparse
import http.server
import os
import socket
import socketserver
import sys
import threading
import webbrowser
from pathlib import Path

# Garante importação dos módulos irmãos
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from extractor import ContextDataExtractor
from insights_engine import InsightsEngine
from template_bundler import TemplateBundler


def find_available_port(start_port: int, max_attempts: int = 20) -> int:
    """Encontra uma porta TCP livre a partir de start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                continue
    return start_port


def serve_file(html_file_path: Path, port: int, open_browser: bool = True):
    """Inicia um servidor HTTP estático local para servir o dashboard gerado."""
    web_dir = html_file_path.parent
    file_name = html_file_path.name
    actual_port = find_available_port(port)

    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(web_dir), **kwargs)

        def log_message(self, format, *args):
            # Silencia logs verbosos de requests
            pass

    server_address = ("", actual_port)
    url = f"http://localhost:{actual_port}/{file_name}"
    print(f"\n[INFO] Servidor local iniciado em: {url}")
    print("       Pressione Ctrl+C para encerrar o servidor.\n")

    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    with socketserver.TCPServer(server_address, CustomHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[INFO] Servidor local encerrado pelo usuario.")


def main():
    parser = argparse.ArgumentParser(
        description="Gera o dashboard standalone Context Insight Visualizer a partir de telemetria local."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Diretorio raiz do context-mode v2.1.10 (contendo projects/<key>/context.db). Tambem aceita CONTEXT_MODE_DATA_DIR.",
    )
    parser.add_argument(
        "--legacy-v1",
        action="store_true",
        help="Forca modo legado v1 (sessions/*.db, content/*.db e stats-pid-*.json).",
    )
    parser.add_argument(
        "--sessions-dir",
        type=str,
        default=None,
        help="Caminho personalizado para a pasta sessions/ do context-mode.",
    )
    parser.add_argument(
        "--content-dir",
        type=str,
        default=None,
        help="Caminho personalizado para a pasta content/ do context-mode.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Caminho do arquivo HTML standalone gerado (padrao: dist/context-insight.html).",
    )
    parser.add_argument(
        "--serve",
        "-s",
        action="store_true",
        help="Inicia um servidor web local para visualizar o dashboard.",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=4747,
        help="Porta para o servidor web local (padrao: 4747).",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Abre o navegador padrao automaticamente apos gerar/iniciar.",
    )

    args = parser.parse_args()

    # Caminho do módulo raiz (tools/context-insight-visualizer)
    root_module_dir = current_dir.parent
    template_dir = root_module_dir / "template"

    if args.output:
        out_path = Path(args.output).resolve()
    else:
        out_path = root_module_dir / "dist" / "context-insight.html"

    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("==========================================================")
    print("   Context Insight Visualizer — Gerador Standalone Local  ")
    print("==========================================================")

    # 1. Extracao
    print("[1/4] Extraindo dados de telemetria local...")
    extractor = ContextDataExtractor(
        sessions_dir=args.sessions_dir,
        content_dir=args.content_dir,
        data_dir=args.data_dir,
        legacy_v1=args.legacy_v1,
    )
    extracted_data = extractor.extract_all()

    meta = extracted_data.get("meta", {})
    print(f"      - Bancos de sessoes encontrados: {meta.get('sessionDbsCount', 0)}")
    print(f"      - Arquivos de processo stats-pid: {meta.get('statsPidCount', 0)}")
    print(f"      - Bancos de conteudo encontrados: {meta.get('contentDbsCount', 0)}")
    if meta.get("warnings"):
        for w in meta["warnings"]:
            print(f"      [AVISO] {w}")

    # 2. Motor de Insights e KPIs
    print("[2/4] Calculando KPIs e avaliando regras de insight...")
    engine = InsightsEngine(extracted_data)
    payload = engine.build_payload()
    kpis = payload["kpis"]
    print(f"      - Total de sessoes: {kpis['totalSessions']}")
    print(f"      - Relacao Leitura/Escrita: {kpis['readWriteRatio']}:1")
    print(f"      - Taxa de compactacao: {kpis['compactRate']}%")
    print(f"      - Taxa de erro: {kpis['errorRatePct']}%")
    print(f"      - Prompts por sessao: {kpis['promptsPerSession']}")
    print(f"      - Cards de Insights avaliados: {len(payload['insightsActions'])}")

    # 3. Empacotamento Standalone
    print(f"[3/4] Compilando template modular de: {template_dir}...")
    bundler = TemplateBundler()
    html_bundled = bundler.bundle_standalone_html(template_dir, payload)

    # 4. Escrita no disco
    print(f"[4/4] Gravando arquivo standalone em: {out_path}...")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_bundled)

    file_size_kb = out_path.stat().st_size / 1024.0
    print(f"\n[SUCESSO] Dashboard gerado com sucesso ({file_size_kb:.1f} KB)!")
    print(f"          Caminho: {out_path}")
    print(f"          Execucao direta offline: file:///{str(out_path).replace(os.sep, '/')}\n")

    # Servir ou abrir navegador se solicitado
    if args.serve:
        serve_file(out_path, args.port, open_browser=args.open)
    elif args.open:
        webbrowser.open(f"file:///{str(out_path).replace(os.sep, '/')}")


if __name__ == "__main__":
    main()

