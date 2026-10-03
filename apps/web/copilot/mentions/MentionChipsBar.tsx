"use client";

import type { MentionChip } from "./types";

type MentionChipsBarProps = {
  chips: MentionChip[];
  onRemove: (index: number) => void;
};

/**
 * MentionChipsBar — fileira de chips removiveis acima do composer, paridade
 * visual com o plugin Copilot da IDE ("📎 pyproject.toml ✕  🐙 copilot-
 * instructions.md ✕"). Renderizada por `MentionChatInput` ANTES do
 * `<CopilotChatInput>` real -- os chips substituem o texto cru `#caminho`/
 * `@agent` que antes era inserido dentro do textarea.
 */
export function MentionChipsBar({ chips, onRemove }: MentionChipsBarProps) {
  if (chips.length === 0) return null;
  return (
    <div className="mention-chips-bar">
      {chips.map((chip, index) => (
        <span key={`${chip.kind}-${chip.id}-${index}`} className="mention-chip" data-kind={chip.kind}>
          <span className="mention-chip__icon">{chip.kind === "file" ? "#" : "@"}</span>
          <span className="mention-chip__label" title={chip.description ?? chip.id}>
            {chip.label}
          </span>
          <button
            type="button"
            className="mention-chip__remove"
            aria-label={`Remover mencao ${chip.label}`}
            onClick={() => onRemove(index)}
          >
            ×
          </button>
        </span>
      ))}
    </div>
  );
}

