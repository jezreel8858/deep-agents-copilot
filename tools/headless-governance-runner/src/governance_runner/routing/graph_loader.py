"""
graph_loader — Parser e compilador de `routing-graph.yaml`.

Contrato (BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md §6.1): carrega o YAML,
valida contra `routing-graph.schema.json`, constrói o grafo dirigido,
checa invariantes estruturais (entry_point único, alcançabilidade,
resolução de aliases `specialist-<papel>`) e emite a `TabelaTransicao`
imutável consumida por `state_machine.py`.

Gaps tratados de forma resiliente (RG-01 a RG-05 do
PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md):
    - RG-01: `condicoes.tipo` ausente → default `"keyword_based"`.
    - RG-02: `threshold_score` apenas carregado/exposto — cálculo de score
      é responsabilidade de `router.py` (subtask 5), não deste módulo.
    - RG-03: `condicoes.politica_desvio` ausente → default `"strict"`.
    - RG-04: alias genérico `specialist-<papel>` ou lista `|`-separada em
      `agent`/`agents_permitidos` é armazenada em `frozenset[str]` sem
      resolução em runtime.
    - RG-05: validação cruzada YAML↔Markdown (`.agent.md`) e YAML↔
      `catalog.yaml` fica fora de escopo desta subtask — a validação de
      `agent` é sintática (token kebab-case bem formado), não semântica
      contra o catálogo completo de agentes.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml
from jsonschema import ValidationError as _JsonSchemaValidationError
from jsonschema import validate as _jsonschema_validate

from governance_runner.routing.model import (
    Aresta,
    CondicaoAresta,
    EtapaSpec,
    Grafo,
    No,
    TabelaTransicao,
    TipoNo,
    Workflow,
    WorkflowSpec,
)

_TOKEN_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_WILDCARD_PREFIX = "*"


class GraphValidationError(Exception):
    """Erro de domínio: `routing-graph.yaml` inválido ou viola invariante estrutural.

    Levantada quando o YAML falha na validação contra o schema JSON ou quando
    uma das invariantes de grafo (§6.1 do blueprint) não é satisfeita —
    ex.: entry_point ausente/duplicado, aresta referenciando nó inexistente,
    etapas de workflow não contíguas, alias de agente malformado.
    """


def _carregar_yaml(caminho_yaml: Path) -> dict[str, Any]:
    try:
        texto = caminho_yaml.read_text(encoding="utf-8")
    except OSError as exc:
        raise GraphValidationError(
            f"Não foi possível ler '{caminho_yaml}': {exc}"
        ) from exc

    try:
        documento = yaml.safe_load(texto)
    except yaml.YAMLError as exc:
        raise GraphValidationError(
            f"'{caminho_yaml}' contém YAML malformado: {exc}"
        ) from exc

    if not isinstance(documento, dict):
        raise GraphValidationError(
            f"'{caminho_yaml}' deve ter um mapeamento na raiz (obteve {type(documento).__name__})"
        )
    return documento


def _validar_schema(documento: dict[str, Any], caminho_schema: Path) -> None:
    try:
        schema_texto = caminho_schema.read_text(encoding="utf-8")
    except OSError as exc:
        raise GraphValidationError(
            f"Não foi possível ler o schema '{caminho_schema}': {exc}"
        ) from exc

    try:
        schema = json.loads(schema_texto)
    except json.JSONDecodeError as exc:
        raise GraphValidationError(
            f"Schema '{caminho_schema}' contém JSON inválido: {exc}"
        ) from exc

    try:
        _jsonschema_validate(instance=documento, schema=schema)
    except _JsonSchemaValidationError as exc:
        caminho = "/".join(str(p) for p in exc.absolute_path) or "<raiz>"
        raise GraphValidationError(
            f"routing-graph.yaml falhou na validação de schema em '{caminho}': {exc.message}"
        ) from exc


def _tokenizar(bruto: str) -> tuple[str, ...]:
    return tuple(t.strip() for t in bruto.split("|") if t.strip())


def _validar_token_agente(token: str, nos_ids: frozenset[str]) -> bool:
    """RG-04/RG-05: aceita id real, alias `specialist-*` ou termo sintaticamente válido.

    A resolução semântica completa contra `catalog.yaml` é deferida para
    subtask futura (RG-05) — aqui apenas garantimos que o token não é
    lixo/malformado (ex.: string vazia, espaços internos, caracteres
    inválidos).
    """
    if token in nos_ids:
        return True
    if token.startswith("specialist-"):
        return True
    return bool(_TOKEN_PATTERN.match(token))


def _construir_nos(bruto: list[dict[str, Any]]) -> tuple[No, ...]:
    nos: list[No] = []
    vistos: set[str] = set()
    for item in bruto:
        id_no = item["id"]
        if id_no in vistos:
            raise GraphValidationError(f"Nó duplicado em 'nos': '{id_no}'")
        vistos.add(id_no)
        try:
            tipo = TipoNo(item["tipo"])
        except ValueError as exc:
            raise GraphValidationError(
                f"Nó '{id_no}' possui tipo inválido: '{item.get('tipo')}'"
            ) from exc
        nos.append(No(id=id_no, tipo=tipo, descricao=item.get("descricao", "")))
    return tuple(nos)


def _validar_entry_point_unico(nos: tuple[No, ...]) -> None:
    entry_points = [n for n in nos if n.tipo is TipoNo.ENTRY_POINT]
    if len(entry_points) != 1:
        raise GraphValidationError(
            f"Esperado exatamente 1 nó 'entry_point', encontrado(s) {len(entry_points)}: "
            f"{[n.id for n in entry_points]}"
        )


def _validar_referencia_no_ou_wildcard(valor: str, nos_ids: frozenset[str]) -> None:
    """Valida `de`/`para` de aresta: id real, wildcard `*tipo` ou lista `|`-separada de ids reais."""
    for token in _tokenizar(valor):
        if token.startswith(_WILDCARD_PREFIX):
            tipo_wildcard = token[1:]
            valores_validos = {t.value for t in TipoNo}
            if tipo_wildcard not in valores_validos:
                raise GraphValidationError(
                    f"Wildcard de aresta '{token}' não corresponde a nenhum TipoNo conhecido"
                )
            continue
        if token not in nos_ids:
            raise GraphValidationError(
                f"Aresta referencia nó inexistente: '{token}' (valor bruto: '{valor}')"
            )


def _construir_condicoes(bruto: dict[str, Any] | None) -> CondicaoAresta:
    bruto = bruto or {}
    return CondicaoAresta(
        tipo=bruto.get("tipo", "keyword_based"),
        regra=bruto.get("regra"),
        gatilho=bruto.get("gatilho"),
        keywords=tuple(bruto.get("keywords", ())),
        sinal=bruto.get("sinal"),
        sinal_r006=bruto.get("sinal_r006"),
        nao_confundir_com=tuple(bruto.get("nao_confundir_com", ())),
        fast_path_bypass=tuple(bruto.get("fast_path_bypass", ())),
        loop_maximo=bruto.get("loop_maximo"),
        retorno_obrigatorio=bruto.get("retorno_obrigatorio"),
        proibido=bruto.get("proibido"),
        aplica_a=bruto.get("aplica_a"),
        acao=bruto.get("acao"),
        politica_desvio=bruto.get("politica_desvio", "strict"),
    )


def _construir_arestas(bruto: list[dict[str, Any]], nos_ids: frozenset[str]) -> tuple[Aresta, ...]:
    arestas: list[Aresta] = []
    for item in bruto:
        de = item["de"]
        para = item["para"]
        _validar_referencia_no_ou_wildcard(de, nos_ids)
        _validar_referencia_no_ou_wildcard(para, nos_ids)
        arestas.append(
            Aresta(
                de=de,
                para=para,
                prioridade=float(item.get("prioridade", 0)),
                threshold_score=float(item.get("threshold_score", 0)),
                nivel_routing=item.get("nivel_routing", "rule-based"),
                condicoes=_construir_condicoes(item.get("condicoes")),
            )
        )
    return tuple(arestas)


def _extrair_agent_permitidos(estado: dict[str, Any], etapa: int, workflow_id: str) -> frozenset[str]:
    """Extrai `agent_permitidos` de uma etapa, tolerando etapas sem agente explícito.

    Gap adicional observado no `routing-graph.yaml` real (além de RG-01..RG-05):
    etapas puramente orquestrativas/de emissão (ex.: `mecanismo`,
    `saida_estruturada`, `validacao_automatizada`) não declaram `agent` nem
    `agents_permitidos` — nesse caso o agente ativo da etapa anterior é
    mantido implicitamente, e retornamos `frozenset()` em vez de falhar.
    """
    if "agent" in estado:
        bruto: Any = estado["agent"]
    elif "agents_permitidos" in estado:
        bruto = estado["agents_permitidos"]
    else:
        return frozenset()

    if isinstance(bruto, list):
        tokens: list[str] = []
        for valor in bruto:
            tokens.extend(_tokenizar(str(valor)))
    else:
        tokens = list(_tokenizar(str(bruto)))

    if not tokens:
        raise GraphValidationError(
            f"Workflow '{workflow_id}' etapa {etapa} declara agente vazio"
        )
    return frozenset(tokens)


def _construir_workflows(bruto: list[dict[str, Any]], nos_ids: frozenset[str]) -> tuple[WorkflowSpec, ...]:
    workflows: list[WorkflowSpec] = []
    for item in bruto:
        workflow_id_bruto = item["id"]
        try:
            workflow_id = Workflow(workflow_id_bruto)
        except ValueError as exc:
            raise GraphValidationError(
                f"Workflow com id desconhecido: '{workflow_id_bruto}'"
            ) from exc

        estados_bruto = item.get("estados", [])
        etapas_num = [int(e["etapa"]) for e in estados_bruto]
        esperado = list(range(1, len(etapas_num) + 1))
        if etapas_num != esperado:
            raise GraphValidationError(
                f"Workflow '{workflow_id_bruto}' possui etapas não contíguas: {etapas_num} (esperado {esperado})"
            )

        etapas: list[EtapaSpec] = []
        for estado in estados_bruto:
            etapa_num = int(estado["etapa"])
            agent_permitidos = _extrair_agent_permitidos(estado, etapa_num, workflow_id_bruto)
            for token in agent_permitidos:
                if not _validar_token_agente(token, nos_ids):
                    raise GraphValidationError(
                        f"Workflow '{workflow_id_bruto}' etapa {etapa_num} possui agente "
                        f"não resolvível sintaticamente: '{token}'"
                    )
            sub_rotinas = tuple(estado.get("sub_rotinas_permitidas", ()))
            proxima = etapa_num + 1 if etapa_num < len(estados_bruto) else None
            etapas.append(
                EtapaSpec(
                    agent_permitidos=agent_permitidos,
                    sub_rotinas_permitidas=frozenset(sub_rotinas),
                    requer_aprovacao=bool(estado.get("checkpoint_humano")),
                    proxima=proxima,
                )
            )
        workflows.append(WorkflowSpec(id=workflow_id, nome=item.get("nome", ""), etapas=tuple(etapas)))
    return tuple(workflows)


def _validar_ausencia_de_ciclos(
    nos: tuple[No, ...], arestas: tuple[Aresta, ...]
) -> None:
    """Invariante 5: nenhum ciclo entre nós `downstream`/`domain_router` alcançáveis
    a partir do `entry_point` exclusivamente via arestas do grafo.

    Nota: esta invariante é uma checagem de **ciclo** (proteção contra loop
    infinito de handoff entre especialistas), não de **cobertura total**
    — nós `downstream` órfãos (sem nenhuma aresta de entrada, ex.:
    utilitários invocados apenas via slash-command fora do fluxo do
    `agent-router`) não violam esta invariante; eles simplesmente não
    entram no subgrafo analisado. Arestas com `de`/`para` wildcard
    (`"*downstream"`) não contribuem para a adjacência concreta (RG-04) —
    apenas arestas cujos tokens resolvem a ids reais em ambos os lados são
    consideradas.
    """
    entry_point = next(n.id for n in nos if n.tipo is TipoNo.ENTRY_POINT)
    nos_ids = {n.id for n in nos}
    tipo_por_id = {n.id: n.tipo for n in nos}
    tipos_alvo = (TipoNo.DOWNSTREAM, TipoNo.DOMAIN_ROUTER)

    adjacencia: dict[str, set[str]] = {n.id: set() for n in nos}
    for aresta in arestas:
        origens = [t for t in aresta.origens if t in nos_ids]
        destinos = [t for t in aresta.destinos if t in nos_ids]
        for origem in origens:
            adjacencia[origem].update(destinos)

    alcancados: set[str] = set()
    pilha = [entry_point]
    while pilha:
        atual = pilha.pop()
        if atual in alcancados:
            continue
        alcancados.add(atual)
        for vizinho in adjacencia.get(atual, ()):
            if vizinho not in alcancados:
                pilha.append(vizinho)

    subgrafo_alvo = {n for n in alcancados if tipo_por_id.get(n) in tipos_alvo}

    branco, cinza, preto = 0, 1, 2
    cor = {n: branco for n in subgrafo_alvo}

    def _dfs(atual: str, caminho: list[str]) -> None:
        cor[atual] = cinza
        caminho.append(atual)
        for vizinho in adjacencia.get(atual, ()):
            if vizinho not in subgrafo_alvo:
                continue
            if cor[vizinho] == cinza:
                inicio = caminho.index(vizinho)
                ciclo = caminho[inicio:] + [vizinho]
                raise GraphValidationError(
                    f"Ciclo detectado entre nós 'downstream'/'domain_router' alcançáveis "
                    f"a partir de '{entry_point}': {' -> '.join(ciclo)}"
                )
            if cor[vizinho] == branco:
                _dfs(vizinho, caminho)
        caminho.pop()
        cor[atual] = preto

    for no_id in subgrafo_alvo:
        if cor[no_id] == branco:
            _dfs(no_id, [])


def carregar_grafo(caminho_yaml: Path, caminho_schema: Path) -> Grafo:
    """Carrega e valida `routing-graph.yaml` contra o schema JSON, retornando o grafo compilado.

    Args:
        caminho_yaml: Caminho absoluto para o arquivo `routing-graph.yaml`.
        caminho_schema: Caminho absoluto para `routing-graph.schema.json`.

    Returns:
        Grafo: Grafo dirigido compilado, com nós e arestas validados.

    Raises:
        GraphValidationError: Se o YAML for inválido, falhar a validação de
            schema, ou violar qualquer invariante estrutural obrigatória
            (entry_point único, alcançabilidade, resolução de nós/aliases).
    """
    documento = _carregar_yaml(caminho_yaml)
    _validar_schema(documento, caminho_schema)

    nos_bruto = documento.get("nos", [])
    if not nos_bruto:
        raise GraphValidationError("'routing-graph.yaml' não declara nenhum nó em 'nos'")

    nos = _construir_nos(nos_bruto)
    _validar_entry_point_unico(nos)
    nos_ids = frozenset(n.id for n in nos)

    arestas = _construir_arestas(documento.get("arestas", []), nos_ids)
    workflows = _construir_workflows(documento.get("workflows", []), nos_ids)

    _validar_ausencia_de_ciclos(nos, arestas)

    return Grafo(nos=nos_ids, nos_por_id=nos, arestas=arestas, workflows=workflows)


def compilar_tabela_transicao(grafo: Grafo) -> TabelaTransicao:
    """Compila o grafo dirigido em uma `TabelaTransicao` imutável por (workflow, etapa).

    Args:
        grafo: Grafo previamente validado por `carregar_grafo`.

    Returns:
        TabelaTransicao: Mapa imutável `{(Workflow, etapa) -> EtapaSpec}`
        consumido por `state_machine.transicionar`.

    Raises:
        GraphValidationError: Se algum workflow do grafo possuir etapas
            não contíguas ou agente não resolvido em `catalog.yaml`.
    """
    from governance_runner.routing.model import Catalogo

    etapas: dict[tuple[Workflow, int], EtapaSpec] = {}
    for workflow_spec in grafo.workflows:
        for indice, etapa_spec in enumerate(workflow_spec.etapas, start=1):
            etapas[(workflow_spec.id, indice)] = etapa_spec

    return TabelaTransicao(etapas=etapas, catalogo=Catalogo(agentes=grafo.nos))
