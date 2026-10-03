"use client";

import { useCallback, useEffect, useMemo, useRef, useState, type ComponentProps } from "react";
import { CopilotChatInput } from "@copilotkit/react-core/v2";
import { MentionTextArea } from "./MentionTextArea";
import { MentionChipsBar } from "./MentionChipsBar";
import { MentionProvider } from "./MentionContext";
import type { MentionChip } from "./types";

type CopilotChatInputProps = ComponentProps<typeof CopilotChatInput>;

function formatarChipParaTexto(chip: MentionChip): string {
  const marcador = chip.kind === "file" ? "#" : "@";
  return `${marcador}${chip.id}`;
}

/**
 * MentionChatInput — substitui o slot `input` COMPLETO de `<CopilotChat>`
 * (nao apenas o sub-slot `textArea`), paridade visual com o composer do
 * plugin Copilot da IDE: arquivos/agents mencionados viram CHIPS removiveis
 * acima do campo de texto (ver screenshot "📎 pyproject.toml ✕  🐙 copilot-
 * instructions.md ✕"), em vez do texto cru `#caminho/arquivo.md` dentro do
 * proprio textarea.
 *
 * So e possivel sobrescrever `onSubmitMessage` (para injetar os chips como
 * texto antes do valor digitado) e exibir os chips ACIMA do composer
 * sobrescrevendo o slot RAIZ `input` inteiro -- o sub-slot `textArea`
 * (usado na 1a versao desta feature) so recebe `TextareaHTMLAttributes`
 * puros, sem acesso a `onSubmitMessage` nem espaco para UI adicional fora
 * do proprio `<textarea>`.
 *
 * 100% das props recebidas (`value`/`onChange`/`onAddFile`/`toolsMenu`/
 * `isRunning`/`positioning`/`containerRef`/etc.) sao repassadas ao
 * `<CopilotChatInput>` REAL sem alteracao, exceto:
 * - `textArea`: `MentionTextArea` (deteccao de `#`/`@` + popover).
 * - `onSubmitMessage`: injeta os chips pendentes como texto (`#id`/`@id`)
 *   antes do valor digitado, limpa os chips e repassa ao handler real.
 *
 * `Object.assign(MentionChatInputBase, CopilotChatInput)` ao final do
 * arquivo copia os subcomponentes estaticos (`SendButton`, `ToolbarButton`,
 * `StartTranscribeButton` etc.) do `CopilotChatInput` original -- o tipo do
 * slot `input` (`SlotValue<typeof CopilotChatInput>`) exige essa mesma
 * forma estatica para aceitar uma funcao como substituicao completa do
 * componente (confirmado por `tsc --noEmit`).
 */
function MentionChatInputBase(props: CopilotChatInputProps) {
  const [chips, setChips] = useState<MentionChip[]>([]);
  const chipsRef = useRef<MentionChip[]>([]);
  // Sincroniza o ref em um efeito (nunca durante o render -- regra
  // `react-hooks/refs`/React Compiler proibe mutar ref no corpo do
  // componente). `handleSubmitMessage` precisa do valor mais recente de
  // forma SINCRONA no momento do submit (nao pode esperar o proximo
  // render), entao o ref continua sendo a fonte de leitura ali.
  useEffect(() => {
    chipsRef.current = chips;
  }, [chips]);

  const adicionarChip = useCallback((chip: MentionChip) => {
    setChips((atual) => {
      const jaExiste = atual.some((c) => c.kind === chip.kind && c.id === chip.id);
      return jaExiste ? atual : [...atual, chip];
    });
  }, []);

  const removerChip = useCallback((indice: number) => {
    setChips((atual) => atual.filter((_, i) => i !== indice));
  }, []);

  const handleSubmitMessage = useCallback(
    (valor: string) => {
      const chipsPendentes = chipsRef.current;
      const textoFinal =
        chipsPendentes.length > 0
          ? `${chipsPendentes.map(formatarChipParaTexto).join(" ")} ${valor}`.trim()
          : valor;
      setChips([]);
      props.onSubmitMessage?.(textoFinal);
    },
    [props]
  );

  const contextValue = useMemo(() => ({ onMention: adicionarChip }), [adicionarChip]);

  return (
    <MentionProvider value={contextValue}>
      <div className="mention-chat-input">
        <MentionChipsBar chips={chips} onRemove={removerChip} />
        <CopilotChatInput
          {...props}
          textArea={MentionTextArea}
          onSubmitMessage={handleSubmitMessage}
        />
      </div>
    </MentionProvider>
  );
}

export const MentionChatInput = Object.assign(MentionChatInputBase, CopilotChatInput);

