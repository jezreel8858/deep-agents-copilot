"""Unitarios do InPlaceWriter (contrato: ver tests/model_profiles/__init__.py)."""
from __future__ import annotations

import os
import time

import pytest

from ._helpers import BOM, load


@pytest.mark.parametrize("bom", [b"", BOM], ids=["sem-bom", "bom"])
@pytest.mark.parametrize("eol", [b"\n", b"\r\n"], ids=["LF", "CRLF"])
def test_set_model_altera_somente_o_valor_preservando_bytes(eol, bom):
    w = load("writer")
    data = bom + eol.join([b"---", b"name: x", b'model: "A"', b"tools: []", b"---",
                           b"corpo", b""])
    assert w.set_model(data, "B") == data.replace(b'model: "A"', b'model: "B"')


def test_set_model_preserva_eol_misto_por_linha():
    w = load("writer")
    data = b'---\nname: x\nmodel: "A"\r\ntools: []\n---\r\ncorpo\r\n'
    assert w.set_model(data, "B") == data.replace(b'"A"', b'"B"')


@pytest.mark.parametrize("old,new", [
    ('model: "A"', 'model: "B"'), ("model: A", "model: B"), ("model: 'A'", "model: 'B'"),
    ('model:  "A"', 'model:  "B"'),
])
def test_set_model_preserva_estilo_de_aspas_e_espacamento(old, new):
    w = load("writer")
    data = f"---\nname: x\n{old}\n---\ncorpo\n".encode()
    assert w.set_model(data, "B") == data.replace(old.encode(), new.encode())


def test_set_model_ignora_model_no_corpo_e_indentado():
    w = load("writer")
    data = (b'---\nname: x\nhandoffs:\n  - model: "nested"\nmodel: "A"\n---\n'
            b'model: "corpo"\n---\nmodel: "hr"\n')
    out = w.set_model(data, "B")
    assert out == data.replace(b'model: "A"', b'model: "B"')
    assert out.count(b'model: "nested"') == 1 and out.count(b'model: "corpo"') == 1


def test_set_model_linha_model_e_a_ultima_do_frontmatter():
    w = load("writer")
    data = b'---\nname: x\nmodel: "A"\n---\ncorpo'
    assert w.set_model(data, "B") == b'---\nname: x\nmodel: "B"\n---\ncorpo'


def test_set_model_insere_valor_literal_sem_interpretar_backrefs():
    w = load("writer")
    weird = r"Modelo \1 $x \g<0>"
    data = b'---\nname: x\nmodel: "A"\n---\ncorpo\n'
    assert w.set_model(data, weird) == data.replace(b'"A"', f'"{weird}"'.encode())


def test_set_model_diferenca_e_de_exatamente_uma_linha():
    w = load("writer")
    data = b'---\nname: x\nmodel: "A"\ntools: []\n---\ncorpo\nmais\n'
    out = w.set_model(data, "B")
    diff = [i for i, (a, b) in enumerate(zip(data.splitlines(True), out.splitlines(True)))
            if a != b]
    assert diff == [2] and len(out.splitlines()) == len(data.splitlines())


def test_set_model_e_reversivel():
    w = load("writer")
    data = b'---\r\nname: x\r\nmodel: "A"\r\n---\r\ncorpo\r\n'
    assert w.set_model(w.set_model(data, "B"), "A") == data


@pytest.mark.parametrize("data", [
    b"sem frontmatter\nmodel: A\n",
    b"---\nname: x\n---\nmodel: A\n",
    b"---\nname: x\nhandoffs:\n  model: A\n---\ncorpo\n",
    b"",
], ids=["sem-fm", "model-so-no-corpo", "model-so-indentado", "vazio"])
def test_set_model_recusa_quando_nao_ha_linha_model_no_frontmatter(data):
    w = load("writer")
    with pytest.raises(w.WriterError):
        w.set_model(data, "B")
    assert w.read_model(data) is None


@pytest.mark.parametrize("line,expected", [('model: "A B"', "A B"), ("model: A", "A"),
                                           ("model: 'A'", "A")])
def test_read_model(line, expected):
    w = load("writer")
    assert w.read_model(f"---\n{line}\n---\n".encode()) == expected


def test_atomic_write_substitui_sem_residuo(tmp_path):
    w = load("writer")
    target = tmp_path / "a.md"
    target.write_bytes(b"old")
    w.atomic_write(target, b"new\r\n")
    assert target.read_bytes() == b"new\r\n"
    assert [p.name for p in tmp_path.iterdir()] == ["a.md"]


def test_atomic_write_retenta_em_permission_error(tmp_path, monkeypatch):
    w = load("writer")
    target = tmp_path / "a.md"
    target.write_bytes(b"old")
    real, calls = os.replace, {"n": 0}

    def flaky(src, dst):
        calls["n"] += 1
        if calls["n"] <= 2:
            raise PermissionError("locked")
        return real(src, dst)

    monkeypatch.setattr(os, "replace", flaky)
    monkeypatch.setattr(time, "sleep", lambda s: None)
    w.atomic_write(target, b"new")
    assert target.read_bytes() == b"new" and calls["n"] == 3


def test_atomic_write_relata_permission_error_e_preserva_original(tmp_path, monkeypatch):
    w = load("writer")
    target = tmp_path / "a.md"
    target.write_bytes(b"old")
    monkeypatch.setattr(os, "replace", lambda s, d: (_ for _ in ()).throw(PermissionError("x")))
    monkeypatch.setattr(time, "sleep", lambda s: None)
    with pytest.raises(PermissionError):
        w.atomic_write(target, b"new")
    assert target.read_bytes() == b"old"
    assert [p.name for p in tmp_path.iterdir()] == ["a.md"]
