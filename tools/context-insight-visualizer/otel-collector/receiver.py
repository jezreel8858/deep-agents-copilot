#!/usr/bin/env python3
"""
receiver.py — Receptor OTLP local mínimo (http/json) para telemetria nativa
do GitHub Copilot / Claude Code (JetBrains > Settings > Tools > GitHub Copilot > Chat > Open Telemetry).

Uso:
    python tools/context-insight-visualizer/otel-collector/receiver.py [--port 4318]

Configuração na IDE (Open Telemetry):
    Enable OpenTelemetry export: ON
    Exporter type: otlp-http
    OTLP protocol: http/json
    OTLP endpoint: http://localhost:4318
    Capture prompt/response content: OFF (obrigatório — R-044, evita PII em logs/)

Saída: tools/context-insight-visualizer/logs/otel-spans.jsonl (1 linha JSON por span,
com atributos já achatados — sem estrutura AnyValue do protocolo OTLP).
"""
import argparse
import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

OUT_PATH = Path(__file__).resolve().parent.parent / "logs" / "otel-spans.jsonl"
DEBUG_RAW_PATH = Path(__file__).resolve().parent.parent / "logs" / "otel-debug-raw.jsonl"
DEBUG_MODE = False  # ativado via --debug


def _unwrap_anyvalue(value: dict) -> object:
    """Achata o formato OTLP AnyValue ({"stringValue": "x"}) em valor Python nativo."""
    if not isinstance(value, dict):
        return value
    for key in ("stringValue", "intValue", "doubleValue", "boolValue"):
        if key in value:
            return value[key]
    if "arrayValue" in value:
        return [_unwrap_anyvalue(v) for v in value["arrayValue"].get("values", [])]
    return value


def _flatten_attrs(attr_list: list) -> dict:
    return {a["key"]: _unwrap_anyvalue(a.get("value", {})) for a in (attr_list or [])}


class OTLPHandler(BaseHTTPRequestHandler):
    def _capture_debug(self, raw_body: bytes, matched: bool, note: str = ""):
        """Grava TODA requisição recebida, sem filtro — usado apenas para diagnóstico (--debug)."""
        if not DEBUG_MODE:
            return
        try:
            DEBUG_RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
            body_preview = raw_body[:3000].decode("utf-8", errors="replace")
            with open(DEBUG_RAW_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "capturedAt": datetime.now(timezone.utc).isoformat(),
                    "method": self.command,
                    "path": self.path,
                    "headers": dict(self.headers.items()),
                    "pathMatched": matched,
                    "note": note,
                    "bodyPreview": body_preview,
                }) + "\n")
        except Exception:
            pass

    def do_GET(self):
        self._capture_debug(b"", matched=False, note="GET recebido (provável health-check da IDE)")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"{}")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        matched = self.path.rstrip("/").endswith("/v1/traces")

        if not matched:
            self._capture_debug(raw, matched=False, note="Path não bateu com /v1/traces")
            self.send_response(404)
            self.end_headers()
            return

        try:
            payload = json.loads(raw)  # http/json: ExportTraceServiceRequest em JSON
            OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            lines = []
            for resource_span in payload.get("resourceSpans", []):
                resource_attrs = _flatten_attrs(resource_span.get("resource", {}).get("attributes", []))
                for scope_span in resource_span.get("scopeSpans", []):
                    for span in scope_span.get("spans", []):
                        span_attrs = _flatten_attrs(span.get("attributes", []))
                        lines.append(json.dumps({
                            "capturedAt": datetime.now(timezone.utc).isoformat(),
                            "spanName": span.get("name"),
                            "startTimeUnixNano": span.get("startTimeUnixNano"),
                            "endTimeUnixNano": span.get("endTimeUnixNano"),
                            "resource": resource_attrs,
                            "attributes": span_attrs,
                        }))
            if lines:
                with open(OUT_PATH, "a", encoding="utf-8") as f:
                    f.write("\n".join(lines) + "\n")
            self._capture_debug(raw, matched=True, note=f"OK — {len(lines)} span(s) processado(s)")
        except Exception as ex:
            self._capture_debug(raw, matched=True, note=f"ERRO ao parsear JSON: {ex}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *args):
        if DEBUG_MODE:
            print("[otel-receiver]", self.address_string(), "-", args[0] % args[1:] if len(args) > 1 else args[0])


def main():
    global DEBUG_MODE
    parser = argparse.ArgumentParser(description="Receptor OTLP local (http/json) — Context Insight Visualizer")
    parser.add_argument("--port", type=int, default=4318)
    parser.add_argument("--debug", action="store_true", help="Grava TODA requisição recebida (raw) em otel-debug-raw.jsonl, sem filtro de path/parsing.")
    args = parser.parse_args()
    DEBUG_MODE = args.debug
    print(f"[otel-receiver] Ouvindo em http://localhost:{args.port}/v1/traces")
    print(f"[otel-receiver] Gravando em: {OUT_PATH}")
    if DEBUG_MODE:
        print(f"[otel-receiver] MODO DEBUG ativo — capturando tudo em: {DEBUG_RAW_PATH}")
    HTTPServer(("0.0.0.0", args.port), OTLPHandler).serve_forever()


if __name__ == "__main__":
    main()

