from __future__ import annotations
import re
import pytest
from pathlib import Path
import yaml

def test_scn_trac_01_otel_semconv_v141_compliance(otel_skill_content):
    """SCN-TRAC-01: Garante conformidade com OTel GenAI Semconv v1.41+ (gen_ai.provider.name, execute_tool)."""
    assert "gen_ai.provider.name" in otel_skill_content, (
        "A skill agent-observability-otel deve especificar o atributo gen_ai.provider.name (substituindo gen_ai.system)."
    )
    assert "execute_tool" in otel_skill_content, (
        "A skill deve especificar a operação execute_tool para spans de ferramentas."
    )
    assert 'gen_ai.tool.type = "mcp"' in otel_skill_content or 'gen_ai.tool.type' in otel_skill_content, (
        "A skill deve cobrir o atributo gen_ai.tool.type para ferramentas MCP."
    )

def test_scn_trac_02_collector_transform_migrates_legacy_semconv(collector_config_content):
    """SCN-TRAC-01/02: Garante que o OpenTelemetry Collector possui transform processor para migrar gen_ai.system legado."""
    config = yaml.safe_load(collector_config_content)
    processors = config.get("processors", {})
    assert "transform/semconv" in processors, "Collector config deve possuir transform/semconv processor."
    
    semconv_rules = str(processors["transform/semconv"])
    assert "gen_ai.provider.name" in semconv_rules, "transform/semconv deve normalizar para gen_ai.provider.name."
    assert "gen_ai.system" in semconv_rules, "transform/semconv deve mapear o campo legado gen_ai.system."
    assert "gen_ai.tool.type" in semconv_rules, "transform/semconv deve marcar gen_ai.tool.type como mcp."

def test_scn_trac_03_collector_redacts_sensitive_secrets(collector_config_content):
    """SCN-TRAC-03: Garante que o OpenTelemetry Collector possui regras estritas de mascaramento de credenciais."""
    config = yaml.safe_load(collector_config_content)
    processors = config.get("processors", {})
    assert "transform/redact-secrets" in processors, "Collector config deve possuir transform/redact-secrets processor."

    redact_rules = str(processors["transform/redact-secrets"])
    assert "ghp_" in redact_rules or "github_pat_" in redact_rules, "Deve mascarar tokens GitHub."
    assert "Bearer" in redact_rules, "Deve mascarar tokens Bearer."
    assert "sk-" in redact_rules or "pk-lf-" in redact_rules, "Deve mascarar chaves de API."

def test_mcp_otel_proxy_components_exist(repo_root):
    """SCN-TRAC-02: Garante a existência física e integridade do proxy MCP OTel stdio."""
    proxy_dir = repo_root / "tools" / "mcp-otel-proxy"
    assert (proxy_dir / "bin" / "mcp-otel-proxy.js").exists(), "Binário bin/mcp-otel-proxy.js deve existir."
    assert (proxy_dir / "src" / "proxy.js").exists(), "Módulo src/proxy.js deve existir."
    assert (proxy_dir / "src" / "tracer.js").exists(), "Módulo src/tracer.js deve existir."
    assert (proxy_dir / "src" / "redact.js").exists(), "Módulo src/redact.js deve existir."
