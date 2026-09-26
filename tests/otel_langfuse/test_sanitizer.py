"""
Testes unitários para o sanitizador de PII e segredos (sanitizer.py).
"""

from otel_langfuse.sanitizer import scrub_string, scrub_data


def test_deve_redigir_segredos_github_quando_presentes():
    texto = "Token de acesso ghp_1234567890abcdefghijklmnopqrstuvwxyz no header"
    resultado = scrub_string(texto)
    assert "ghp_1234567890abcdefghijklmnopqrstuvwxyz" not in resultado
    assert "***REDACTED_GH***" in resultado


def test_deve_redigir_chaves_langfuse_quando_presentes():
    texto = "Public: pk-lf-12345-abcdef e Secret: sk-lf-67890-ghijkl"
    resultado = scrub_string(texto)
    assert "pk-lf-12345-abcdef" not in resultado
    assert "sk-lf-67890-ghijkl" not in resultado
    assert "***REDACTED_LF***" in resultado


def test_deve_redigir_bearer_token_quando_presente():
    texto = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.token.signature"
    resultado = scrub_string(texto)
    assert "Bearer ***REDACTED***" in resultado
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in resultado


def test_deve_redigir_aws_e_google_keys_quando_presentes():
    texto = "AWS AKIAIOSFODNN7EXAMPLE e Google AIzaSyD-1234567890abcdef_ghijklmn"
    resultado = scrub_string(texto)
    assert "AKIAIOSFODNN7EXAMPLE" not in resultado
    assert "***REDACTED_AWS***" in resultado
    assert "AIzaSyD-1234567890abcdef_ghijklmn" not in resultado
    assert "***REDACTED_GOOGLE***" in resultado


def test_deve_redigir_emails_quando_presentes():
    texto = "Contato do usuario dev.privado@empresa.com.br para suporte"
    resultado = scrub_string(texto)
    assert "dev.privado@empresa.com.br" not in resultado
    assert "***REDACTED_EMAIL***" in resultado


def test_deve_sanitizar_estruturas_aninhadas_em_dicionarios_e_listas():
    payload = {
        "user": {
            "email": "teste@exemplo.com",
            "detalhes": ["Chave sk-lf-99999-secreta", "normal"]
        },
        "status": "ok"
    }
    sanitizado = scrub_data(payload)
    assert sanitizado["user"]["email"] == "***REDACTED_EMAIL***"
    assert "***REDACTED_LF***" in sanitizado["user"]["detalhes"][0]
    assert sanitizado["user"]["detalhes"][1] == "normal"
    assert sanitizado["status"] == "ok"


def test_deve_mascarar_campos_com_nomes_sensiveis():
    payload = {
        "password": "minhasenhasecreta123",
        "api_key": "qualquer_chave_livre",
        "access_token": "token123"
    }
    sanitizado = scrub_data(payload)
    assert sanitizado["password"] == "***REDACTED***"
    assert sanitizado["api_key"] == "***REDACTED***"
    assert sanitizado["access_token"] == "***REDACTED***"
