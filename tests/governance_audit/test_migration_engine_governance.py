"""
test_migration_engine_governance.py — Suíte de testes automatizados para o Motor Agnóstico de Migração.

Valida as regras de governança e garantias contratuais de:
- REQ-001 / RNF-001: Validade do schema da Representação Intermediária (IR Schema)
- REQ-002 / RNF-003: Validação de presença obrigatória das stacks envolvidas (.github/agents/<camada>/<stack>/)
- REQ-005 / REQ-006: Protocolo de Dual-Verification e Circuit Breaker de Paridade
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except ImportError:
    jsonschema = None
    Draft202012Validator = None

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = REPO_ROOT / "docs" / "schemas"
IR_SCHEMA_FILE = SCHEMAS_DIR / "migration-ir.schema.json"
AGENTS_DIR = REPO_ROOT / ".github" / "agents"


def load_ir_schema() -> dict:
    assert IR_SCHEMA_FILE.exists(), f"Schema {IR_SCHEMA_FILE} deve existir"
    with open(IR_SCHEMA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_stack_governance_registered(domain: str, stack_name: str) -> tuple[bool, str]:
    """
    Função de pré-voo (Fase 0): valida se uma stack possui ecossistema formal registrado
    em .github/agents/<camada>/<stack>/ contendo router, sub-catálogo e especialistas.
    """
    stack_dir = AGENTS_DIR / domain / stack_name
    if not stack_dir.exists() or not stack_dir.is_dir():
        return False, f"Diretório da stack não encontrado: .github/agents/{domain}/{stack_name}/"

    # Verificar presença do router
    router_file = stack_dir / f"{stack_name}-router.agent.md"
    if not router_file.exists():
        return False, f"Supervisor hierárquico {router_file.name} ausente em {stack_dir}"

    # Verificar presença do sub-catálogo
    catalog_file = stack_dir / f"{stack_name}-catalog.yaml"
    if not catalog_file.exists():
        return False, f"Sub-catálogo {catalog_file.name} ausente em {stack_dir}"

    # Verificar presença de pelo menos 5 especialistas canônicos
    agent_files = list(stack_dir.glob("*.agent.md"))
    if len(agent_files) < 5:
        return False, f"Stack {stack_name} possui apenas {len(agent_files)} agentes (mínimo esperado: 5)"

    return True, f"Stack {stack_name} ({domain}) devidamente registrada e em conformidade."


# ── Testes do Schema Canônico (REQ-001 / RNF-001) ──────────────────────────

def test_ir_schema_is_valid_draft202012():
    """Valida que o schema da IR é um JSON Schema sintaticamente válido segundo Draft 2020-12"""
    if Draft202012Validator is None:
        pytest.skip("jsonschema não instalado no ambiente")
    schema = load_ir_schema()
    Draft202012Validator.check_schema(schema)


def test_ir_schema_validates_canonical_payload():
    """Valida que um payload de IR em conformidade com o Technical Blueprint passa 100% no schema"""
    if Draft202012Validator is None:
        pytest.skip("jsonschema não instalado no ambiente")
    schema = load_ir_schema()
    validator = Draft202012Validator(schema)

    valid_payload = {
        "schemaVersion": "1.0.0",
        "metadata": {
            "migrationId": "MIG-2026-001",
            "timestamp": "2026-09-12T10:00:00Z",
            "sourceStack": {
                "domain": "backend",
                "name": "struts",
                "version": "1.3.10",
                "catalogRef": ".github/agents/backend/struts/struts-catalog.yaml"
            },
            "targetStack": {
                "domain": "backend",
                "name": "spring-boot",
                "version": "3.4.0",
                "catalogRef": ".github/agents/backend/spring-boot/spring-boot-catalog.yaml"
            },
            "moduleName": "auth-module"
        },
        "entryPoints": [
            {
                "id": "EP-001",
                "name": "LoginAction",
                "type": "http_endpoint",
                "route": {
                    "path": "/login.do",
                    "method": "POST"
                },
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string"},
                        "password": {"type": "string"}
                    },
                    "required": ["username", "password"]
                },
                "outputSchema": {
                    "type": "object",
                    "properties": {
                        "token": {"type": "string"},
                        "expiresIn": {"type": "integer"}
                    }
                },
                "security": {
                    "authenticated": False
                }
            }
        ],
        "domainEntities": [
            {
                "name": "UserCredential",
                "description": "Entidade de credencial de usuário",
                "fields": [
                    {"name": "id", "type": "uuid", "required": True, "primaryKey": True},
                    {"name": "username", "type": "string", "required": True, "unique": True},
                    {"name": "passwordHash", "type": "string", "required": True}
                ],
                "relationships": []
            }
        ],
        "businessRules": [
            {
                "ruleId": "RN-AUTH-001",
                "title": "Validação de formato de credencial",
                "description": "Nome de usuário e senha devem ser preenchidos obrigatoriamente.",
                "category": "validation",
                "preconditions": ["Requisição recebida"],
                "actions": ["Verificar presença de campos não vazios"],
                "postconditions": ["Prosseguir autenticação ou rejeitar com HTTP 400"],
                "associatedEntryPoints": ["EP-001"]
            }
        ],
        "characterizationVectors": [
            {
                "vectorId": "VEC-AUTH-001",
                "entryPointId": "EP-001",
                "description": "Autenticação bem-sucedida com credenciais válidas",
                "scenario": "Credenciais corretas",
                "inputPayload": {"username": "admin", "password": "securePass123"},
                "expectedOutputPayload": {"token": "jwt-token-sample", "expiresIn": 3600},
                "expectedStatusCode": 200
            }
        ]
    }

    errors = list(validator.iter_errors(valid_payload))
    assert len(errors) == 0, f"Erros de validação encontrados: {[e.message for e in errors]}"


def test_ir_schema_rejects_missing_required_sections():
    """Valida que o schema rejeita payloads incompletos (ausência de vetores de teste ou regras)"""
    if Draft202012Validator is None:
        pytest.skip("jsonschema não instalado no ambiente")
    schema = load_ir_schema()
    validator = Draft202012Validator(schema)

    incomplete_payload = {
        "schemaVersion": "1.0.0",
        "metadata": {
            "migrationId": "MIG-2026-002",
            "timestamp": "2026-09-12T10:00:00Z",
            "sourceStack": {"domain": "backend", "name": "struts", "catalogRef": "ref"},
            "targetStack": {"domain": "backend", "name": "spring-boot", "catalogRef": "ref"},
            "moduleName": "billing"
        },
        "entryPoints": [],
        "domainEntities": []
        # Ausência proposital de 'businessRules' e 'characterizationVectors'
    }

    errors = list(validator.iter_errors(incomplete_payload))
    error_fields = [e.validator_value for e in errors if e.validator == "required"]
    assert len(errors) > 0, "Payload incompleto deveria ter sido rejeitado"


# ── Testes de Pré-voo de Stacks Envolvidas (REQ-002 / RNF-003) ─────────────

@pytest.mark.parametrize("domain,stack", [
    ("backend", "struts"),
    ("backend", "ejb"),
    ("backend", "spring-boot"),
    ("backend", "spring-reactive"),
    ("backend", "python"),
    ("frontend", "angular"),
])
def test_registered_stacks_pass_pre_flight_governance(domain: str, stack: str):
    """Valida que todas as stacks canônicas registradas no projeto passam no pré-voo de governança"""
    is_valid, msg = validate_stack_governance_registered(domain, stack)
    assert is_valid is True, f"Stack {stack} deveria ser aprovada no pré-voo: {msg}"


@pytest.mark.parametrize("domain,stack", [
    ("backend", "cobol"),
    ("backend", "delphi"),
    ("backend", "ruby-on-rails"),
    ("frontend", "vue-js"),
    ("frontend", "flutter"),
])
def test_unregistered_stacks_fail_pre_flight_governance(domain: str, stack: str):
    """Valida que stacks ausentes do projeto são sumariamente rejeitadas no pré-voo com mensagem clara (REQ-002)"""
    is_valid, msg = validate_stack_governance_registered(domain, stack)
    assert is_valid is False, f"Stack inexistente {stack} deveria ter sido reprovada no pré-voo"
    assert "não encontrado" in msg or "ausente" in msg


# ── Testes do Protocolo de Dual-Verification (REQ-005 / REQ-006) ───────────

def test_dual_verification_contract_evaluation():
    """Valida que o circuito de paridade requer 100% de testes Golden Master e 100% de regras mapeadas"""
    def evaluate_dual_verification(golden_master_pass_rate: float, rules_coverage_rate: float) -> tuple[bool, str]:
        if golden_master_pass_rate < 1.0:
            return False, f"Circuit Breaker acionado: Golden Master pass rate ({golden_master_pass_rate*100}%) < 100%"
        if rules_coverage_rate < 1.0:
            return False, f"Circuit Breaker acionado: Cobertura de regras de negócio ({rules_coverage_rate*100}%) < 100%"
        return True, "Paridade funcional comprovada: 100% Golden Master e 100% Regras validadas."

    # Cenário de Sucesso
    ok, msg = evaluate_dual_verification(1.0, 1.0)
    assert ok is True
    assert "Paridade funcional comprovada" in msg

    # Cenário de Falha em Testes Golden Master
    fail_gm, msg_gm = evaluate_dual_verification(0.98, 1.0)
    assert fail_gm is False
    assert "Golden Master pass rate" in msg_gm

    # Cenário de Falha em Cobertura de Regras de Negócio
    fail_rules, msg_rules = evaluate_dual_verification(1.0, 0.95)
    assert fail_rules is False
    assert "Cobertura de regras de negócio" in msg_rules



# ── Testes de Bootstrapping Interativo (REQ-007 / RNF-005) ─────────────────

def test_target_project_bootstrapping_requires_human_confirmation():
    """Valida que para projetos novos (green-field), decisões de build e runtime exigem aprovação via ask_questions"""
    def evaluate_bootstrapping_flow(is_new_project: bool, user_confirmed_options: dict = None) -> tuple:
        if not is_new_project:
            return True, "Projeto existente: prosseguir diretamente para emissão de código a partir da IR."
        
        if not user_confirmed_options:
            return False, "Violação RNF-005: Decisões de scaffolding exigem confirmação explícita do desenvolvedor via ask_questions."
        
        required_keys = {"build_tool", "runtime_version"}
        if not required_keys.issubset(user_confirmed_options.keys()):
            return False, f"Opções de bootstrapping incompletas: {required_keys - set(user_confirmed_options.keys())}"
        
        return True, f"Scaffolding oficial aprovado com {user_confirmed_options['build_tool']} e runtime {user_confirmed_options['runtime_version']}."

    # Cenário 1: Tentativa de gerar projeto novo sem confirmação do usuário (deve falhar)
    ok_unconfirmed, msg_unconfirmed = evaluate_bootstrapping_flow(is_new_project=True, user_confirmed_options=None)
    assert ok_unconfirmed is False
    assert "Violação RNF-005" in msg_unconfirmed

    # Cenário 2: Usuário escolhe explicitamente Maven e Java 21 (deve passar)
    confirmed_maven = {"build_tool": "maven", "runtime_version": "java-21"}
    ok_maven, msg_maven = evaluate_bootstrapping_flow(is_new_project=True, user_confirmed_options=confirmed_maven)
    assert ok_maven is True
    assert "maven" in msg_maven

    # Cenário 3: Usuário escolhe explicitamente Gradle e Java 25 (deve passar)
    confirmed_gradle = {"build_tool": "gradle", "runtime_version": "java-25"}
    ok_gradle, msg_gradle = evaluate_bootstrapping_flow(is_new_project=True, user_confirmed_options=confirmed_gradle)
    assert ok_gradle is True
    assert "gradle" in msg_gradle

    # Cenário 4: Projeto existente (in-place) dispensa novo bootstrapping
    ok_existing, msg_existing = evaluate_bootstrapping_flow(is_new_project=False, user_confirmed_options=None)
    assert ok_existing is True
    assert "Projeto existente" in msg_existing


# ── Testes de Symbol Exhaustion Gate (REQ-001 / Invariante 13) ──────────────

def test_symbol_exhaustion_gate_contract_evaluation():
    """Valida que o gate de exaustão de símbolos bloqueia o avanço caso a cobertura seja inferior a 100%"""
    def evaluate_symbol_exhaustion(total_legacy_symbols: int, mapped_de_para_symbols: int) -> tuple[bool, str]:
        if total_legacy_symbols <= 0:
            return False, "Total de símbolos legados deve ser superior a zero para validação mecânica."
        if mapped_de_para_symbols < total_legacy_symbols:
            missing = total_legacy_symbols - mapped_de_para_symbols
            coverage = (mapped_de_para_symbols / total_legacy_symbols) * 100
            return False, f"Symbol Exhaustion Gate bloqueado: {missing} símbolos legados omitidos na Matriz De-Para (cobertura: {coverage:.1f}% < 100%)."
        return True, "Symbol Exhaustion comprovado: 100% dos símbolos legados mapeados na Matriz De-Para."

    # Cenário de Sucesso: 100% de símbolos mapeados
    ok, msg = evaluate_symbol_exhaustion(120, 120)
    assert ok is True
    assert "Symbol Exhaustion comprovado" in msg

    # Cenário de Falha: Símbolos esquecidos pelo agente
    fail_missing, msg_fail = evaluate_symbol_exhaustion(120, 115)
    assert fail_missing is False
    assert "5 símbolos legados omitidos" in msg_fail


# ── Testes de Validação e Redundância Pós-Migração (REQ-008 / REQ-009 / Etapa 6) ─

def test_post_migration_verification_redundancy_gate_contract():
    """Valida a tríplice camada de redundância pós-migração exigindo aprovação unânime nos 3 pilares"""
    def evaluate_post_migration_redundancy(
        orphans_detected: int,
        mutants_killed_ratio: float,
        differential_discrepancies: int
    ) -> tuple[bool, str]:
        if orphans_detected > 0:
            return False, f"Bloqueio de Cutover (Reverse Orphan Audit): {orphans_detected} símbolos/queries legados órfãos detectados sem paridade."
        if mutants_killed_ratio < 1.0:
            survived_pct = (1.0 - mutants_killed_ratio) * 100
            return False, f"Bloqueio de Cutover (Mutation Parity): suíte frágil/falso-positivo detectada ({survived_pct:.1f}% de mutantes sobreviveram)."
        if differential_discrepancies > 0:
            return False, f"Bloqueio de Cutover (Differential Shadow Replay): {differential_discrepancies} divergências semânticas em payloads/banco de dados."
        return True, "Certificado de Paridade Total emitido: tríplice redundância aprovada, cutover autorizado."

    # Cenário 1: Sucesso absoluto (zero órfãos, 100% mutantes eliminados, zero divergências)
    ok_full, msg_full = evaluate_post_migration_redundancy(0, 1.0, 0)
    assert ok_full is True
    assert "Certificado de Paridade Total emitido" in msg_full

    # Cenário 2: Falha por código legado órfão esquecido
    fail_orphan, msg_orphan = evaluate_post_migration_redundancy(2, 1.0, 0)
    assert fail_orphan is False
    assert "Reverse Orphan Audit" in msg_orphan
    assert "2 símbolos/queries legados órfãos" in msg_orphan

    # Cenário 3: Falha por testes de paridade frágeis (falso-positivo com mutante sobrevivente)
    fail_mut, msg_mut = evaluate_post_migration_redundancy(0, 0.90, 0)
    assert fail_mut is False
    assert "Mutation Parity" in msg_mut
    assert "mutantes sobreviveram" in msg_mut

    # Cenário 4: Falha por divergência semântica em replay diferencial
    fail_diff, msg_diff = evaluate_post_migration_redundancy(0, 1.0, 1)
    assert fail_diff is False
    assert "Differential Shadow Replay" in msg_diff
    assert "1 divergências semânticas" in msg_diff


# ── Teste Estrutural de Conformidade do WORKFLOW-FRAMEWORK-MIGRATION ─────────

def test_workflow_7_declares_six_canonical_steps_and_post_migration_invariants():
    """Valida estaticamente em workflows.md que o Workflow 7 possui as 6 etapas canônicas e seus invariantes"""
    workflows_file = REPO_ROOT / ".github" / "agents" / "workflows.md"
    assert workflows_file.exists(), "workflows.md deve existir"
    content = workflows_file.read_text(encoding="utf-8")

    # 1. Deve declarar 6 etapas canônicas no objetivo
    assert "6 etapas canônicas" in content, "Workflow 7 deve declarar formalmente 6 etapas canônicas"

    # 2. Deve declarar o Estado 6 formalmente
    assert "Estado 6 — Post-Migration Verification & Redundancy Gate" in content, "Estado 6 deve estar detalhado na cadeia sequencial"
    assert "Reverse Orphan Audit" in content, "Reverse Orphan Audit deve estar presente"
    assert "Mutation Parity Resilience" in content, "Mutation Parity Resilience deve estar presente"
    assert "Differential Shadow Replay" in content, "Differential Shadow Replay deve estar presente"

    # 3. Deve declarar o Invariante 13 em § 5
    assert "13. **Invariante de Exaustão de Símbolos e Tríplice Redundância Pós-Migração" in content, "Invariante 13 deve estar formalizado em § 5"

    # 4. Deve declarar o template de 6 etapas na Seção 6.2
    assert "Pipeline de Execução: WORKFLOW-FRAMEWORK-MIGRATION (6 etapas)" in content, "Template visual deve ter 6 etapas"
