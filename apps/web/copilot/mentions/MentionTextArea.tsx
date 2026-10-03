"use client";

import {
  forwardRef,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ChangeEvent,
  type KeyboardEvent,
  type TextareaHTMLAttributes,
} from "react";
import { useAgent } from "@copilotkit/react-core/v2";
import { useWorkspaceFiles } from "./useWorkspaceFiles";
import { useAgentCatalog } from "./useAgentCatalog";
import { useCommandCatalog } from "./useCommandCatalog";
import { useMentionContext } from "./MentionContext";
import { MentionPopover, type MentionOption } from "./MentionPopover";

type Gatilho = "#" | "@" | "/";


type EstadoGatilho = {
  trigger: Gatilho;
  query: string;
  /** indice (no `value` do textarea) onde o caractere gatilho comeca */
  start: number;
} | null;

// Reconhece "#" ou "@" seguido de 0+ caracteres sem espaco, no fim do texto
// ANTES do cursor -- precedido por inicio de string ou espaco (evita
// disparar no meio de um e-mail ou hashtag ja "fechados" por espaco).
const REGEX_GATILHO = /(?:^|\s)([@#])([^\s]*)$/;

// "/" (slash commands/prompts, pedido explicito do usuario, 2026-10-02)
// SO dispara quando e literalmente o PRIMEIRO caractere de TODO o texto
// (nao apos espaco/meio de frase) -- paridade com o picker de slash
// commands da IDE, que so reconhece "/" como 1o token da mensagem.
const REGEX_GATILHO_SLASH = /^\/([^\s]*)$/;

function detectarGatilho(valor: string, cursor: number): EstadoGatilho {
  const antesDoCursor = valor.slice(0, cursor);
  const matchSlash = REGEX_GATILHO_SLASH.exec(antesDoCursor);
  if (matchSlash) {
    return { trigger: "/", query: matchSlash[1] ?? "", start: 0 };
  }
  const match = REGEX_GATILHO.exec(antesDoCursor);
  if (!match) return null;
  const trigger = (match[1] ?? "") as Gatilho;
  const query = match[2] ?? "";
  if (trigger !== "#" && trigger !== "@") return null;
  const start = antesDoCursor.length - (trigger.length + query.length);
  return { trigger, query, start };
}

function obterSetterNativo(): ((el: HTMLTextAreaElement, valor: string) => void) | null {
  if (typeof window === "undefined") return null;
  const descriptor = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value");
  const setter = descriptor?.set;
  if (!setter) return null;
  return (el, valor) => setter.call(el, valor);
}

/** `true` se o cursor esta na PRIMEIRA linha visual do texto (sem `\n` antes
 * dele) -- numa textarea de 1 linha isso e sempre `true`, independente da
 * coluna. Usado para so disparar o historico de prompts (ArrowUp) quando
 * nao ha "linha acima" real para o cursor navegar nativamente. */
function estaNaPrimeiraLinha(valor: string, cursor: number): boolean {
  return !valor.slice(0, cursor).includes("\n");
}

/** Espelho de `estaNaPrimeiraLinha` para ArrowDown (sem `\n` DEPOIS do
 * cursor -- esta na ULTIMA linha visual). */
function estaNaUltimaLinha(valor: string, cursor: number): boolean {
  return !valor.slice(cursor).includes("\n");
}

/** Extrai o texto puro de uma mensagem do agent (`agent.messages`, tipo
 * `Message` do AG-UI) -- `content` pode ser `string` (caso comum) ou um
 * array de `ContentPart` multimodal (anexos); nesse caso, concatena so as
 * partes do tipo `"text"` (ignora imagens/documentos/audio). */
function extrairTextoDeMensagem(mensagem: { content?: unknown }): string {
  const conteudo = mensagem.content;
  if (typeof conteudo === "string") return conteudo;
  if (Array.isArray(conteudo)) {
    return conteudo
      .filter(
        (parte): parte is { type: string; text?: unknown } =>
          !!parte && typeof parte === "object" && "type" in parte
      )
      .filter((parte) => parte.type === "text" && typeof parte.text === "string")
      .map((parte) => parte.text as string)
      .join("\n");
  }
  return "";
}

/**
 * MentionTextArea — slot `textArea` usado por `MentionChatInput` (slot
 * `input` COMPLETO de `<CopilotChat>`, ver `docs.copilotkit.ai/custom-look-
 * and-feel/slots` -- o slot recebe exatamente
 * `React.TextareaHTMLAttributes<HTMLTextAreaElement>` + `ref`, confirmado
 * por introspeccao do `.d.mts` instalado em
 * `node_modules/@copilotkit/react-core`).
 *
 * Implementa paridade com o composer do plugin Copilot da IDE:
 * - `#` abre o picker de arquivos do workspace (`useWorkspaceFiles`,
 *   busca incremental no gateway).
 * - `@` abre o picker de agents disponiveis (`useAgentCatalog`, catalogo
 *   carregado 1x e filtrado localmente).
 *
 * Ao escolher uma opcao, o texto digitado do gatilho (`#query`/`@query`) e
 * REMOVIDO do textarea (via setter nativo de `HTMLTextAreaElement.value` +
 * `dispatchEvent(new Event("input"))` -- unica forma de atualizar um
 * textarea CONTROLADO pelo componente pai sem acesso direto ao seu estado
 * interno) e a mencao vira um CHIP visual acima do composer
 * (`useMentionContext().onMention`, consumido por `MentionChatInput`) --
 * paridade com o picker nativo da IDE, em vez de texto cru no meio da
 * mensagem.
 *
 * Historico de prompts com ArrowUp/ArrowDown (pedido do usuario,
 * 2026-10-02, paridade com o chat do Copilot na IDE): com o cursor na
 * PRIMEIRA linha do texto (sempre verdadeiro em textarea de 1 linha),
 * ArrowUp preenche o composer com a ultima mensagem de usuario enviada
 * nesta thread (`agent.messages`, via `useAgent()`), e repetir ArrowUp
 * continua voltando ate a primeira mensagem do inicio do chat. ArrowDown
 * (com o cursor na ULTIMA linha) percorre de volta em direcao ao rascunho
 * original (preservado antes da 1a navegacao), restaurando-o ao fim do
 * historico. Editar o texto manualmente durante a navegacao "solta" o
 * historico (o texto editado vira o novo rascunho).
 */
export const MentionTextArea = forwardRef<
  HTMLTextAreaElement,
  TextareaHTMLAttributes<HTMLTextAreaElement>
>(function MentionTextArea(props, forwardedRef) {
  const { onChange, onKeyDown, onSelect, onBlur, value, ...resto } = props;
  const innerRef = useRef<HTMLTextAreaElement | null>(null);
  const [gatilho, setGatilho] = useState<EstadoGatilho>(null);
  const [indiceAtivo, setIndiceAtivo] = useState(0);

  const { onMention } = useMentionContext();
  const { arquivos, carregando: carregandoArquivos, buscar: buscarArquivos } = useWorkspaceFiles();
  const { agentes, carregando: carregandoAgentes } = useAgentCatalog();
  const { comandos, carregando: carregandoComandos } = useCommandCatalog();

  // Historico de prompts (ArrowUp/ArrowDown): `indiceHistorico` null =
  // navegacao inativa (textarea mostra o rascunho vivo do usuario);
  // 0 = mensagem mais recente enviada; N = N-esima mais antiga. O rascunho
  // digitado ANTES da 1a navegacao fica em `rascunhoRef` para ser
  // restaurado ao sair do historico via ArrowDown. `ignorarProximaMudancaRef`
  // distingue um `input` event SINTETICO (disparado por nos ao navegar) de
  // uma edicao REAL do usuario (que deve encerrar a navegacao).
  const { agent } = useAgent();
  const [indiceHistorico, setIndiceHistorico] = useState<number | null>(null);
  const rascunhoRef = useRef<string>("");
  const ignorarProximaMudancaRef = useRef(false);

  const atribuirRefs = useCallback(
    (node: HTMLTextAreaElement | null) => {
      innerRef.current = node;
      if (typeof forwardedRef === "function") forwardedRef(node);
      else if (forwardedRef) (forwardedRef as React.MutableRefObject<HTMLTextAreaElement | null>).current = node;
    },
    [forwardedRef]
  );

  // Composer esvaziado pelo componente pai (ex.: apos enviar a mensagem) --
  // encerra qualquer navegacao de historico pendente, para a proxima
  // mensagem comecar do zero (sem herdar indice/rascunho da anterior).
  useEffect(() => {
    if (value === "") {
      setIndiceHistorico(null);
      rascunhoRef.current = "";
    }
  }, [value]);

  const obterHistoricoPrompts = useCallback((): string[] => {
    const mensagens = (agent.messages ?? []) as Array<{ role?: string; content?: unknown }>;
    const textos: string[] = [];
    for (const mensagem of mensagens) {
      if (mensagem.role !== "user") continue;
      const texto = extrairTextoDeMensagem(mensagem).trim();
      if (texto.length > 0) textos.push(texto);
    }
    return textos; // ordem cronologica: [0] = mais antiga, [length-1] = mais recente.
  }, [agent]);

  const definirValorTextarea = useCallback((valor: string) => {
    const el = innerRef.current;
    const setarValorNativo = obterSetterNativo();
    if (!el || !setarValorNativo) return;
    ignorarProximaMudancaRef.current = true;
    setarValorNativo(el, valor);
    el.dispatchEvent(new Event("input", { bubbles: true }));
    requestAnimationFrame(() => {
      el.focus();
      el.setSelectionRange(valor.length, valor.length); // cursor no final do texto recuperado.
    });
  }, []);

  const navegarHistorico = useCallback(
    (direcao: "cima" | "baixo") => {
      const el = innerRef.current;
      if (!el) return false;
      const cursor = el.selectionStart ?? el.value.length;

      if (direcao === "cima") {
        if (!estaNaPrimeiraLinha(el.value, cursor)) return false;
        const historico = obterHistoricoPrompts();
        if (historico.length === 0) return false;
        if (indiceHistorico === null) rascunhoRef.current = el.value;
        const novoIndice = indiceHistorico === null ? 0 : Math.min(indiceHistorico + 1, historico.length - 1);
        const valorHistorico = historico[historico.length - 1 - novoIndice];
        if (valorHistorico === undefined) return false;
        setIndiceHistorico(novoIndice);
        definirValorTextarea(valorHistorico);
        return true;
      }

      // direcao === "baixo"
      if (indiceHistorico === null || !estaNaUltimaLinha(el.value, cursor)) return false;
      if (indiceHistorico === 0) {
        setIndiceHistorico(null);
        definirValorTextarea(rascunhoRef.current);
        return true;
      }
      const historico = obterHistoricoPrompts();
      const novoIndice = indiceHistorico - 1;
      const valorHistorico = historico[historico.length - 1 - novoIndice];
      if (valorHistorico === undefined) return false;
      setIndiceHistorico(novoIndice);
      definirValorTextarea(valorHistorico);
      return true;
    },
    [indiceHistorico, obterHistoricoPrompts, definirValorTextarea]
  );

  const opcoes: MentionOption[] = useMemo(() => {
    if (!gatilho) return [];
    if (gatilho.trigger === "#") {
      return arquivos.map((arquivo) => ({
        id: arquivo.path,
        label: arquivo.name,
        description: `${arquivo.project} · /${arquivo.path}`,
      }));
    }
    const queryNormalizada = gatilho.query.toLowerCase();
    if (gatilho.trigger === "/") {
      // Prompts (.github/prompts/*.prompt.md) + skills (.github/skills/**/
      // SKILL.md), paridade com o picker de slash commands da IDE --
      // filtra por substring no nome OU na descricao (mesmo criterio do
      // picker de agents `@` abaixo).
      return comandos
        .filter(
          (comando) =>
            comando.name.toLowerCase().includes(queryNormalizada) ||
            (comando.description ?? "").toLowerCase().includes(queryNormalizada)
        )
        .slice(0, 30)
        .map((comando) => ({
          id: comando.name,
          label: comando.name,
          description: comando.description
            ? `${comando.description} · ${comando.kind === "skill" ? "skill" : "prompt"}`
            : comando.kind === "skill"
              ? "skill"
              : "prompt",
        }));
    }
    return agentes
      .filter(
        (agente) =>
          agente.name.toLowerCase().includes(queryNormalizada) ||
          (agente.display_name ?? "").toLowerCase().includes(queryNormalizada)
      )
      .slice(0, 30)
      .map((agente) => ({
        id: agente.name,
        label: agente.display_name ?? agente.name,
        description: agente.description ?? undefined,
      }));
  }, [gatilho, arquivos, agentes, comandos]);

  useEffect(() => {
    setIndiceAtivo(0);
  }, [gatilho?.trigger, gatilho?.query, opcoes.length]);

  const recalcularGatilho = useCallback(() => {
    const el = innerRef.current;
    if (!el) return;
    const proximo = detectarGatilho(el.value, el.selectionStart ?? el.value.length);
    setGatilho(proximo);
    if (proximo?.trigger === "#") buscarArquivos(proximo.query);
  }, [buscarArquivos]);

  const inserirMencao = useCallback(
    (opcao: MentionOption) => {
      const el = innerRef.current;
      const setarValorNativo = obterSetterNativo();
      if (!el || !gatilho || !setarValorNativo) return;
      const valorAtual = el.value;
      const cursor = el.selectionStart ?? valorAtual.length;
      const antes = valorAtual.slice(0, gatilho.start);
      const depois = valorAtual.slice(cursor);

      if (gatilho.trigger === "/") {
        // Slash command/prompt: insere o nome como TEXTO LITERAL (nao
        // chip) -- paridade com o picker de slash commands da IDE, onde
        // "/nome" continua fazendo parte da mensagem enviada ao agent.
        const textoComando = `/${opcao.id} `;
        const proximoCursorSlash = antes.length + textoComando.length;
        setarValorNativo(el, `${antes}${textoComando}${depois}`);
        el.dispatchEvent(new Event("input", { bubbles: true }));
        setGatilho(null);
        requestAnimationFrame(() => {
          el.focus();
          el.setSelectionRange(proximoCursorSlash, proximoCursorSlash);
        });
        return;
      }

      // Remove apenas o texto digitado do gatilho (#query/@query) -- a
      // mencao vira um chip visual acima do composer (via `onMention`),
      // nunca texto cru dentro do textarea (paridade com a IDE).
      const proximoCursor = antes.length;

      setarValorNativo(el, `${antes}${depois}`);
      el.dispatchEvent(new Event("input", { bubbles: true }));
      setGatilho(null);
      onMention({
        kind: gatilho.trigger === "#" ? "file" : "agent",
        id: opcao.id,
        label: opcao.label,
        description: opcao.description,
      });
      requestAnimationFrame(() => {
        el.focus();
        el.setSelectionRange(proximoCursor, proximoCursor);
      });
    },
    [gatilho, onMention]
  );

  const handleChange = useCallback(
    (event: ChangeEvent<HTMLTextAreaElement>) => {
      onChange?.(event);
      recalcularGatilho();
      if (ignorarProximaMudancaRef.current) {
        // `input` event sintetico disparado por `definirValorTextarea` (nos
        // mesmos, ao navegar o historico) -- consome a flag e MANTEM
        // `indiceHistorico` (nao e uma edicao real do usuario).
        ignorarProximaMudancaRef.current = false;
      } else if (indiceHistorico !== null) {
        // Edicao manual durante a navegacao: "solta" o historico -- o texto
        // atual (ja editado pelo usuario) vira o novo rascunho vivo.
        setIndiceHistorico(null);
      }
    },
    [onChange, recalcularGatilho, indiceHistorico]
  );

  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLTextAreaElement>) => {
      if (gatilho && opcoes.length > 0) {
        if (event.key === "ArrowDown") {
          event.preventDefault();
          setIndiceAtivo((indice) => (indice + 1) % opcoes.length);
          return;
        }
        if (event.key === "ArrowUp") {
          event.preventDefault();
          setIndiceAtivo((indice) => (indice - 1 + opcoes.length) % opcoes.length);
          return;
        }
        if (event.key === "Enter" || event.key === "Tab") {
          event.preventDefault();
          const opcaoSelecionada = opcoes[indiceAtivo];
          if (opcaoSelecionada) inserirMencao(opcaoSelecionada);
          return;
        }
        if (event.key === "Escape") {
          event.preventDefault();
          setGatilho(null);
          return;
        }
      } else if (event.key === "ArrowUp" || event.key === "ArrowDown") {
        // Sem popover de mencao ativo: ArrowUp/ArrowDown navegam o
        // historico de prompts enviados nesta thread (pedido do usuario,
        // 2026-10-02). `navegarHistorico` so intercepta a tecla quando o
        // cursor esta na 1a linha (ArrowUp) ou ultima linha (ArrowDown) do
        // texto -- caso contrario, o navegador move o cursor normalmente.
        const tratado = navegarHistorico(event.key === "ArrowUp" ? "cima" : "baixo");
        if (tratado) {
          event.preventDefault();
          return;
        }
      }
      onKeyDown?.(event);
    },
    [gatilho, opcoes, indiceAtivo, inserirMencao, onKeyDown, navegarHistorico]
  );


  const handleSelect = useCallback(
    (event: React.SyntheticEvent<HTMLTextAreaElement>) => {
      onSelect?.(event);
      recalcularGatilho();
    },
    [onSelect, recalcularGatilho]
  );

  const handleBlur = useCallback(
    (event: React.FocusEvent<HTMLTextAreaElement>) => {
      onBlur?.(event);
      // Delay curto: permite que o `onMouseDown` do item do popover (que
      // chama `preventDefault`) seja processado antes do popover fechar.
      window.setTimeout(() => setGatilho(null), 120);
    },
    [onBlur]
  );

  return (
    <div className="mention-textarea-wrapper">
      <textarea
        {...resto}
        value={value}
        ref={atribuirRefs}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        onSelect={handleSelect}
        onBlur={handleBlur}
        // Bug real corrigido: o CopilotChatInput da biblioteca aplica
        // `cpk:py-3 cpk:pr-5` ao textarea padrao mas NENHUM padding-left
        // (confirmado por inspecao do DOM renderizado) -- o texto ficava
        // colado na borda esquerda. `style` (inline) tem prioridade
        // garantida sobre as classes utilitarias da lib, independente de
        // ordem de carregamento do CSS -- mais seguro que tentar sobrepor
        // via className/CSS cascade. Mescla com qualquer `style` que a lib
        // ja repasse (ex.: `maxHeight`/`height` do auto-grow).
        style={{ ...resto.style, paddingLeft: "1.25rem" }}
      />
      {gatilho && opcoes.length > 0 ? (
        <MentionPopover
          trigger={gatilho.trigger}
          options={opcoes}
          activeIndex={indiceAtivo}
          loading={
            gatilho.trigger === "#"
              ? carregandoArquivos
              : gatilho.trigger === "@"
                ? carregandoAgentes
                : carregandoComandos
          }
          onHoverIndex={setIndiceAtivo}
          onSelect={inserirMencao}
        />
      ) : null}
    </div>
  );
});

