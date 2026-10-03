"use client";

export type MentionOption = {
  id: string;
  label: string;
  description?: string;
};

type MentionPopoverProps = {
  trigger: "#" | "@" | "/";
  options: MentionOption[];
  activeIndex: number;
  loading?: boolean;
  onHoverIndex: (index: number) => void;
  onSelect: (option: MentionOption) => void;
};

/**
 * MentionPopover — lista flutuante renderizada acima do composer quando o
 * usuario digita `#` (arquivos) ou `@` (agents), paridade visual com
 * "Select File, Folder or Tool" / listagem de agents do plugin Copilot da
 * IDE. Navegacao por teclado (Arrow Up/Down, Enter, Esc) e tratada pelo
 * `MentionTextArea` pai -- este componente e apenas apresentacional
 * (recebe `activeIndex` e dispara `onSelect`/`onHoverIndex`).
 */
export function MentionPopover({
  trigger,
  options,
  activeIndex,
  loading,
  onHoverIndex,
  onSelect,
}: MentionPopoverProps) {
  return (
    <div className="mention-popover" role="listbox">
      <div className="mention-popover__header">
        {trigger === "#"
          ? "Arquivos do workspace"
          : trigger === "@"
            ? "Agents disponiveis"
            : "Prompts e skills"}
        {loading ? <span className="mention-popover__loading">buscando…</span> : null}
      </div>
      <ul className="mention-popover__list">
        {options.map((option, index) => (
          <li key={option.id}>
            <button
              type="button"
              role="option"
              aria-selected={index === activeIndex}
              className="mention-popover__item"
              data-active={index === activeIndex}
              onMouseEnter={() => onHoverIndex(index)}
              // onMouseDown (nao onClick): dispara ANTES do blur do textarea,
              // preservando a selecao de cursor usada por `insertMention`.
              onMouseDown={(event) => {
                event.preventDefault();
                onSelect(option);
              }}
            >
              <span className="mention-popover__row">
                <span className="mention-popover__trigger">{trigger}</span>
                <span className="mention-popover__label">{option.label}</span>
              </span>
              {option.description ? (
                <span className="mention-popover__description">{option.description}</span>
              ) : null}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

