/**
 * toolLabels — dicionario de rotulos amigaveis (PT-BR) + icone por tool,
 * usado pelo renderer generico (`useDefaultRenderTool` em `actions.tsx`)
 * para traduzir nomes tecnicos de tool calls (`glob`, `view`,
 * `context-mode/ctx_search`, `github-mcp-server-get_file_contents`, etc.)
 * em algo que o usuario final entende sem saber o nome interno da tool.
 *
 * Padrao de mercado pesquisado (2026): Cursor/Claude Code/ChatGPT
 * "humanizam" tool calls com verbo no gerundio + alvo ("Reading
 * file.tsx", "Searching workspace") em vez do nome tecnico cru; CopilotKit
 * v2 (`docs.copilotkit.ai/generative-ui/tool-rendering`,
 * `useDefaultRenderTool`) devolve `{name, args, status, result}` prontos
 * para este tipo de mapeamento, sem exigir 1 renderer por tool
 * (`useRenderTool`) -- usamos o catch-all (`useDefaultRenderTool`) + este
 * dicionario para cobrir TODAS as tools do catalogo de uma vez.
 *
 * Fontes dos nomes reais: `.github/agents/**\/*.agent.md` (`tools:`
 * frontmatter, ver `agent_catalog.py`) + tools nativas do Copilot CLI
 * confirmadas por introspecao ao vivo da wheel (`view`, `glob`, `bash`,
 * `edit`, `grep`, `git`, `gh`, `task`, `ask_user`, `read_agent`,
 * `write_agent`, `list_agents`, `send_inbox`, `context_board`, `skill`,
 * `exit_plan_mode`, `task_complete` -- ver nota RT-05 em
 * `sdk_session.stream_chat_ag_ui`).
 */

interface RotuloTool {
  /** Emoji exibido antes do rotulo. */
  icone: string;
  /** Rotulo amigavel em PT-BR (usado tanto em execucao quanto concluido). */
  rotulo: string;
}

const ROTULOS_TOOLS: Record<string, RotuloTool> = {
  // --- Leitura/busca de codigo e arquivos ---
  read_file: { icone: "📄", rotulo: "Lendo arquivo" },
  view: { icone: "📄", rotulo: "Visualizando arquivo" },
  file_search: { icone: "🔍", rotulo: "Procurando arquivos" },
  glob: { icone: "🔍", rotulo: "Procurando arquivos" },
  grep_search: { icone: "🔎", rotulo: "Buscando texto no código" },
  grep: { icone: "🔎", rotulo: "Buscando texto no código" },
  list_dir: { icone: "📁", rotulo: "Listando pasta" },
  get_errors: { icone: "🩺", rotulo: "Verificando erros" },

  // --- Edicao/execucao ---
  edit: { icone: "✏️", rotulo: "Editando arquivo" },
  insert_edit_into_file: { icone: "✏️", rotulo: "Editando arquivo" },
  replace_string_in_file: { icone: "✏️", rotulo: "Editando arquivo" },
  create_file: { icone: "🆕", rotulo: "Criando arquivo" },
  run_in_terminal: { icone: "💻", rotulo: "Executando comando" },
  bash: { icone: "💻", rotulo: "Executando comando" },
  git: { icone: "🌿", rotulo: "Operação Git" },
  gh: { icone: "🐙", rotulo: "Operação GitHub" },

  // --- Orquestracao de agents / governanca ---
  run_subagent: { icone: "🤖", rotulo: "Delegando para especialista" },
  task: { icone: "🤖", rotulo: "Executando sub-tarefa" },
  task_complete: { icone: "✅", rotulo: "Finalizando tarefa" },
  exit_plan_mode: { icone: "📋", rotulo: "Saindo do modo de planejamento" },
  read_agent: { icone: "📖", rotulo: "Consultando definição de agente" },
  write_agent: { icone: "📝", rotulo: "Atualizando definição de agente" },
  list_agents: { icone: "🗂️", rotulo: "Listando agentes disponíveis" },
  send_inbox: { icone: "📨", rotulo: "Enviando mensagem interna" },
  context_board: { icone: "🗒️", rotulo: "Atualizando quadro de contexto" },
  skill: { icone: "🧠", rotulo: "Consultando skill" },
  ask_user: { icone: "❓", rotulo: "Perguntando ao usuário" },
  ask_questions: { icone: "❓", rotulo: "Perguntando ao usuário" },

  // --- context-mode (sandbox/indexacao) ---
  "context-mode/ctx_search": { icone: "🧭", rotulo: "Buscando no contexto indexado" },
  "context-mode/ctx_execute": { icone: "🧪", rotulo: "Executando no sandbox" },
  "context-mode/ctx_execute_file": { icone: "🧪", rotulo: "Analisando arquivo no sandbox" },
  "context-mode/ctx_index": { icone: "🗃️", rotulo: "Indexando conteúdo" },
  "context-mode/ctx_batch_execute": { icone: "🧪", rotulo: "Executando lote no sandbox" },
  "context-mode/ctx_fetch_and_index": { icone: "🌐", rotulo: "Buscando e indexando página web" },
  "context-mode/ctx_stats": { icone: "📊", rotulo: "Consultando estatísticas de contexto" },
  "context-mode/ctx_doctor": { icone: "🩺", rotulo: "Diagnosticando context-mode" },
  "context-mode/ctx_upgrade": { icone: "⬆️", rotulo: "Atualizando context-mode" },
  "context-mode/ctx_purge": { icone: "🗑️", rotulo: "Limpando contexto indexado" },
  "context-mode/ctx_insight": { icone: "📈", rotulo: "Abrindo painel de insights" },

  // --- codegraph ---
  "codegraph/query": { icone: "🕸️", rotulo: "Consultando grafo de código" },
  "codegraph/module_map": { icone: "🗺️", rotulo: "Mapeando módulos" },
  "codegraph/fn_impact": { icone: "💥", rotulo: "Analisando impacto da função" },
  "codegraph/find_cycles": { icone: "🔄", rotulo: "Detectando dependências circulares" },
  "codegraph/context": { icone: "🕸️", rotulo: "Obtendo contexto de função" },

  // --- Tavily (pesquisa externa) ---
  "tavily/tavily_search": { icone: "🌐", rotulo: "Pesquisando na web" },
  "tavily/tavily_extract": { icone: "🌐", rotulo: "Extraindo conteúdo da página" },
  "tavily/tavily_crawl": { icone: "🌐", rotulo: "Navegando no site" },
  "tavily/tavily_map": { icone: "🌐", rotulo: "Mapeando site" },
  "tavily/tavily_research": { icone: "🌐", rotulo: "Pesquisando em profundidade" },
};

/** Prefixos reconhecidos de tools MCP externas (ex.: `github-mcp-server-*`). */
const PREFIXOS_MCP: Array<{ prefixo: string; icone: string; rotuloServidor: string }> = [
  { prefixo: "github-mcp-server-", icone: "🐙", rotuloServidor: "GitHub" },
  { prefixo: "mcp_tavily_", icone: "🌐", rotuloServidor: "Tavily" },
  { prefixo: "mcp_context-mode_", icone: "🧭", rotuloServidor: "context-mode" },
  { prefixo: "mcp_codegraph_", icone: "🕸️", rotuloServidor: "codegraph" },
];

/** Converte `snake_case`/`kebab-case` em "Texto Legível" (fallback final). */
function humanizarNomeBruto(nome: string): string {
  const semPrefixoCaminho = nome.includes("/") ? nome.split("/").pop()! : nome;
  const comEspacos = semPrefixoCaminho.replace(/[_-]+/g, " ").trim();
  return comEspacos.charAt(0).toUpperCase() + comEspacos.slice(1);
}

/**
 * rotularTool — resolve `{icone, rotulo}` amigavel para um nome de tool cru.
 *
 * Ordem de resolucao:
 * 1. Match exato no dicionario `ROTULOS_TOOLS`.
 * 2. Prefixo MCP conhecido (`PREFIXOS_MCP`) -> `"🐙 GitHub: get file contents"`.
 * 3. Fallback: humaniza o nome cru (`snake_case` -> `"Nome Legível"`) com
 *    icone genérico de ferramenta (🔧) -- nunca deixa a tool sem rotulo
 *    algum, mesmo para tools futuras ainda nao catalogadas aqui.
 */
export function rotularTool(nomeBruto: string): RotuloTool {
  const exato = ROTULOS_TOOLS[nomeBruto];
  if (exato) return exato;

  for (const { prefixo, icone, rotuloServidor } of PREFIXOS_MCP) {
    if (nomeBruto.startsWith(prefixo)) {
      const resto = nomeBruto.slice(prefixo.length);
      return { icone, rotulo: `${rotuloServidor}: ${humanizarNomeBruto(resto)}` };
    }
  }

  return { icone: "🔧", rotulo: humanizarNomeBruto(nomeBruto) };
}

