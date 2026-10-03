export type MentionChip = {
  /** "file" -> picker `#` (arquivos do workspace); "agent" -> picker `@`. */
  kind: "file" | "agent";
  /** identificador usado como texto embutido na mensagem (path ou nome do agent). */
  id: string;
  /** rotulo curto exibido no chip (nome do arquivo ou display_name do agent). */
  label: string;
  description?: string;
};

