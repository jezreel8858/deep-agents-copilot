/**
 * diffParser — parsing minimo de unified diff (formato `--- a/...`, `+++ b/...`,
 * `@@ -l,n +l,n @@`) para linhas renderizaveis no `FileEditBridge.tsx`.
 *
 * O texto do `diff` ja chega PRONTO do Copilot SDK (campo `diff: str` de
 * `PermissionRequestWrite`, confirmado por introspeccao real da wheel
 * instalada, 2026-10-02) -- este modulo so faz o parsing estrutural para
 * exibicao linha-a-linha (numero de linha antiga/nova + tipo), sem gerar
 * diff algum (zero dependencia de libs de diffing como `diff`/`jsdiff`).
 */

export type TipoLinhaDiff = "contexto" | "adicionada" | "removida" | "cabecalho";

export interface LinhaDiff {
  tipo: TipoLinhaDiff;
  /** Numero da linha no arquivo ORIGINAL (antes da mudanca); `null` se a linha nao existe no original (adicionada). */
  numeroAntigo: number | null;
  /** Numero da linha no arquivo NOVO (depois da mudanca); `null` se a linha nao existe no novo (removida). */
  numeroNovo: number | null;
  /** Conteudo da linha, sem o prefixo `+`/`-`/` ` do unified diff. */
  conteudo: string;
}

const REGEX_HUNK = /^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*$/;

/**
 * Converte um texto em unified diff em uma lista de `LinhaDiff` prontas
 * para renderizacao (ex.: tabela com coluna de numero de linha antiga/nova
 * + fundo colorido por tipo), ignorando linhas de metadado de arquivo
 * (`--- a/...`, `+++ b/...`, `diff --git ...`, `index ...`) que ja sao
 * exibidas separadamente (nome do arquivo no cabecalho do componente).
 *
 * @param diffTexto Texto bruto do campo `diff` de `PermissionRequestWrite`.
 * @returns Lista de linhas classificadas, na ordem do diff original.
 */
export function parsearDiff(diffTexto: string): LinhaDiff[] {
  if (!diffTexto) return [];

  const linhasBrutas = diffTexto.split("\n");
  const resultado: LinhaDiff[] = [];
  let linhaAntigaAtual = 0;
  let linhaNovaAtual = 0;

  for (const linhaBruta of linhasBrutas) {
    if (
      linhaBruta.startsWith("--- ") ||
      linhaBruta.startsWith("+++ ") ||
      linhaBruta.startsWith("diff --git") ||
      linhaBruta.startsWith("index ")
    ) {
      continue; // Metadado de arquivo -- ja exibido no cabecalho do componente.
    }

    const matchHunk = REGEX_HUNK.exec(linhaBruta);
    if (matchHunk) {
      linhaAntigaAtual = parseInt(matchHunk[1] ?? "0", 10);
      linhaNovaAtual = parseInt(matchHunk[3] ?? "0", 10);
      resultado.push({
        tipo: "cabecalho",
        numeroAntigo: null,
        numeroNovo: null,
        conteudo: linhaBruta,
      });
      continue;
    }

    if (linhaBruta.startsWith("\\")) {
      continue; // Ex.: "\ No newline at end of file" -- metadado, nao conteudo.
    }

    if (linhaBruta.startsWith("-")) {
      resultado.push({
        tipo: "removida",
        numeroAntigo: linhaAntigaAtual,
        numeroNovo: null,
        conteudo: linhaBruta.slice(1),
      });
      linhaAntigaAtual += 1;
      continue;
    }

    if (linhaBruta.startsWith("+")) {
      resultado.push({
        tipo: "adicionada",
        numeroAntigo: null,
        numeroNovo: linhaNovaAtual,
        conteudo: linhaBruta.slice(1),
      });
      linhaNovaAtual += 1;
      continue;
    }

    // Linha de contexto (prefixo " " ou vazia) -- existe em ambas as versoes.
    resultado.push({
      tipo: "contexto",
      numeroAntigo: linhaAntigaAtual,
      numeroNovo: linhaNovaAtual,
      conteudo: linhaBruta.startsWith(" ") ? linhaBruta.slice(1) : linhaBruta,
    });
    linhaAntigaAtual += 1;
    linhaNovaAtual += 1;
  }

  return resultado;
}

/** Resumo rapido (`+N -M`) para exibir no cabecalho sem renderizar o diff inteiro. */
export function resumirDiff(linhas: LinhaDiff[]): { adicionadas: number; removidas: number } {
  let adicionadas = 0;
  let removidas = 0;
  for (const linha of linhas) {
    if (linha.tipo === "adicionada") adicionadas += 1;
    else if (linha.tipo === "removida") removidas += 1;
  }
  return { adicionadas, removidas };
}

/** Formato cru (snake_case) de 1 linha do diff COMPLETO calculado pelo
 * backend (`sdk_session._gerar_linhas_diff_completo`, serializado via JSON
 * no `CustomEvent(name="file_edit_requested")`). */
export interface LinhaDiffBruta {
  tipo: "contexto" | "adicionada" | "removida";
  numero_antigo: number | null;
  numero_novo: number | null;
  conteudo: string;
}

/**
 * Converte as `lines` ja estruturadas vindas do backend (diff COMPLETO --
 * TODAS as linhas do arquivo, nao apenas os hunks truncados do unified
 * diff, pedido explicito do usuario 2026-10-02) para o mesmo formato
 * `LinhaDiff` usado pela renderizacao, sem nenhum parsing de texto --
 * o backend ja faz a comparacao linha-a-linha via `difflib`.
 *
 * @param linhasBrutas Array `value.lines` do `CustomEvent`.
 * @returns Lista de `LinhaDiff` prontas para renderizacao.
 */
export function converterLinhasBackend(linhasBrutas: LinhaDiffBruta[]): LinhaDiff[] {
  return linhasBrutas.map((linha) => ({
    tipo: linha.tipo,
    numeroAntigo: linha.numero_antigo,
    numeroNovo: linha.numero_novo,
    conteudo: linha.conteudo,
  }));
}

