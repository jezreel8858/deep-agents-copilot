"""ORCAMENTO DE TEMPO (suite tests/model_profiles): pasta inteira <= 60 s e nenhum teste > 3 s
em maquina com spawn de processo normal (~50 ms). Custo medido no Windows c/ antivirus: ~0,4 s
por spawn de git/python => minimize spawns. Tecnicas: `git init --template=` (sem hooks),
`fast_clone` (worktree + metadados + objects via alternates, sem copytree de .git/objects),
template `applied` (apply 1x/sessao), `dead_pid()` cacheado, 1 spawn por commit de fixture.
Testes acima de 3 s geram um aviso (nao falham) via conftest. Comando recomendado:
    python -m pytest -q --tb=short -p no:cacheprovider tests/model_profiles --durations=10
Testes (TDD, estado red) do gerador de perfis de modelos - Emenda E1 / D4' do plano
docs/implementation-plans/20261010-feature-development-model-profiles-allowlist.md (secao 14).

CONTRATO DE API/CLI ESPERADO (tools/model_profiles/, reusando resolver.py sem duplicar logica)
================================================================================================
cli.py
    main(argv: list[str]) -> int
        Opcao global `--repo <raiz>` (default: `git rev-parse --show-toplevel` do cwd).
        Subcomandos: list | status | apply <perfil> [--dry-run] [--yes] | restore [--force-line]
                     | doctor [--repair] | init.
        Exit codes: 0 ok; 1 recusa/erro/drift/conflito; 2 uso invalido (argparse).
        Nunca lanca Exception ao usuario (BaseException de crash propaga). Saida em stdout/stderr.
        Mensagens carregam CODIGOS estaveis entre colchetes (assertados pelos testes):
        [DIRTY] [IN_PROGRESS] [LOCKED] [STALE_LOCK] [CONFLICT] [DRIFT] [ORPHAN_JOURNAL]
        [PATH_TRAVERSAL] [SKIP_WORKTREE] [HOOKS_PATH] [ALLOWLIST_STALE] [NOT_PINNABLE] [RETIRED]
        [UNKNOWN_MODEL] [DEPRECATED] [RETIREMENT_SOON] [COST_HIERARCHY] [COST_RANK_NULL].
        apply: resolve o perfil -> valida allowlist + D6 -> imprime resumo (perfil, N arquivos,
        modelo antigo->novo, `quality_warning` do perfil e aviso "nao commitar") -> confirma.
        Confirmacao: `builtins.input()`; aceita "s|sim|y|yes"; EOFError/outro = recusa (exit 1,
        nada gravado). `--yes` pula a confirmacao (EXCETO com [COST_RANK_NULL]: exige digitar
        exatamente "CONFIRMAR"). `--dry-run`: so resumo, exit 0, nada gravado (nem state.json).
        Perfil `default`/inexistente: inexistente => exit 1.
        status: exit 0 sem drift; exit 1 com [DRIFT] ou [ORPHAN_JOURNAL]. Mostra perfil ativo,
        phase e [ALLOWLIST_STALE]. list: um perfil por linha (marca o ativo com `*` ou `ativo`).
        init: cria `.model-profiles/` e, se nao ignorado, acrescenta a entrada em
        `.git/info/exclude` (idempotente; nunca edita arquivos versionados).
        doctor: diagnostico (allowlist, frescor, D6 de TODOS os perfis, skip-worktree, core.hooksPath,
        journal orfao, lock obsoleto); `--repair` conclui/reverte journal orfao e remove lock stale.
writer.py   (InPlaceWriter - R1/R5)
    read_model(data: bytes) -> str | None        # valor sem aspas do `model:` top-level do frontmatter
    set_model(data: bytes, new_model: str) -> bytes   # altera SOMENTE os bytes do valor; preserva
        BOM, EOL de cada linha, aspas ('/"/nenhuma) e espacamento; ignora `model:` no corpo e
        indentado; levanta WriterError sem frontmatter/sem linha model:.
    atomic_write(path: Path, data: bytes) -> None   # tmp + os.replace, retry em PermissionError
        (via time.sleep); apos esgotar relanca PermissionError; sem tmp residual.
        TODA escrita em alvo (apply/restore/repair) passa por `writer.atomic_write` acessado como
        atributo do modulo (permite spy/crash nos testes).
state.py
    STATE_DIR = ".model-profiles"; state.json v1 (R6):
    {schema_version:1, profile, profile_hash(sha256 hex), phase: pending|applied|restored,
     head_commit, applied_at, files:[{path, head_blob, original_model, variant_model, eol,
     sha256_after}]}; escrita write-ahead (phase `pending` com a lista completa ANTES da 1a
     escrita em alvo; `applied` ao final; `restored` apos restore/repair). `files` so lista
     arquivos cujo modelo MUDA.
lock.py
    LockError; exclusive_lock(repo: Path) -> context manager sobre `.model-profiles/lock`
    (JSON {"pid", "timestamp"(epoch)}); stale = PID morto OU idade > STALE_AFTER_SECONDS (retoma);
    removido ao sair. Instancia viva e recente => LockError / exit 1 [LOCKED].
apply.py / restore.py / doctor.py
    Usam `from tools.model_profiles import resolver` e chamam resolver.resolve_profile,
    resolver.get_canonical_key, resolver.resolve_target_model, resolver.get_tier_for_key por
    atributo do modulo (sem redefinir essas funcoes). restore usa `git show HEAD:<path>`.
allowlist.py / hierarchy.py (T-B2.2)
    hierarchy.load_edges(routing_graph: Path) -> list[tuple[str, str]]   # (de, para) de `arestas`
    hierarchy.find_violations(edges, model_by_key: Mapping[str,str],
        cost_rank_by_model: Mapping[str,int|None], exceptions: Collection[str] = ())
        -> list[Violation]  (Violation: parent, child, kind in {"cost_hierarchy",
        "cost_rank_unverifiable"}); child.rank > parent.rank viola (igual NAO viola); filho em
        `exceptions` (model_exception_reason) e isento; rank None => "cost_rank_unverifiable".
Escopo de escrita: apenas a linha `model:` de .github/agents/**/*.agent.md e
.github/prompts/**/*.prompt.md; catalog.yaml e routing-graph.yaml NUNCA sao escritos.
Alvos sujos / merge|rebase|cherry-pick|revert em andamento => apply recusado (R2).
Restore (R1): linha `model:` volta ao valor de `git show HEAD:<path>`; se a linha atual !=
variant_model => [CONFLICT], arquivo intocado (exit 1) salvo `--force-line`; edicoes de CORPO
feitas com perfil ativo sobrevivem.
"""
