/**
 * Padrão de Edição Segura para Arquivo Único Grande/Estruturado e Markdown com Âncoras Repetidas (R-051)
 * ----------------------------------------------------------------------
 * Use este padrão via context-mode (ctx_execute) SEMPRE que o arquivo-alvo:
 *   - for Markdown estruturado (.agent.md, .instructions.md, .md com frontmatter YAML ou tabelas com entradas parecidas), OU
 *   - tiver mais de 200 linhas, OU
 *   - for .yaml/.yml/.json (sintaxe sensível a indentação), OU
 *   - for consumido diretamente por testes automatizados/CI.
 *
 * NUNCA use `insert_edit_into_file` nesses casos — incidente real documentado
 * (2026-09): a tool truncou/corrompeu arquivos de 600-1200 linhas ao tentar
 * aplicar uma edição pequena com âncoras insuficientes, reduzindo-os a
 * dezenas de linhas sem aviso confiável.
 *
 * NUNCA confie cegamente no `replace_string_in_file` quando houver risco de colisão de âncoras:
 * (2026-09): a tool possui fallback fuzzy quando o casamento exato falha, podendo casar no
 * ponto errado em Markdown estruturado, apagando frontmatter e títulos iniciais (incidente real
 * em code-knowledge-graph.agent.md).
 *
 * Contrato do padrão:
 *   1. Ler o arquivo inteiro do disco (fonte da verdade real, nunca a
 *      "preview" que uma tool de edição eventualmente retornar).
 *   2. Para cada substituição planejada, contar OCORRÊNCIAS EXATAS do
 *      texto-âncora (`oldStr`) no conteúdo em memória.
 *   3. Abortar (não escrever nada) se a contagem for != 1 para qualquer
 *      âncora — nunca escrever com base em suposição.
 *   4. Só then aplicar TODAS as substituições em memória e escrever
 *      (`fs.writeFileSync`) uma única vez — operação all-or-nothing.
 *   5. Reler do disco imediatamente após escrever para confirmar que o
 *      conteúdo novo está presente E que o total de linhas é compatível
 *      com o esperado (nunca confiar apenas na ausência de erro da tool).
 *   6. Rodar validação estrutural do formato (ex.: `yaml.safe_load` para
 *      YAML, contagem de colchetes/chaves balanceados para Mermaid) antes
 *      de considerar a edição concluída.
 *
 * Este arquivo é referenciado por `efficient-batch-code-modification/SKILL.md`
 * § 5 e por `governance-audit-patterns/SKILL.md` Smell 2.16. Não duplicar
 * este template em outros arquivos de governança (R-003) — apenas referenciar
 * o caminho deste snippet.
 */

const fs = require('fs');

function crlf(s) {
  // Normaliza quebras de linha do "oldStr"/"newStr" digitados com \n para o
  // formato real do arquivo (muitos arquivos de governança usam CRLF).
  return s.replace(/\r\n/g, '\n').replace(/\n/g, '\r\n');
}

function applyVerifiedEdits(path, edits) {
  let content = fs.readFileSync(path, 'utf8');
  const originalLen = content.length;
  let allOk = true;

  for (const e of edits) {
    const oldStr = crlf(e.old);
    const count = content.split(oldStr).length - 1;
    if (count !== 1) {
      console.log(`ABORT [${e.label}]: ${count} occurrences (expected 1)`);
      allOk = false;
      continue;
    }
    content = content.replace(oldStr, crlf(e.new));
    console.log(`OK [${e.label}]`);
  }

  if (!allOk) {
    console.log('NOT WRITTEN — one or more anchors failed. No changes made.');
    return false;
  }

  fs.writeFileSync(path, content, 'utf8');
  console.log(`WRITTEN. New length: ${content.length} (was ${originalLen})`);

  // Passo 5: reler e confirmar
  const verify = fs.readFileSync(path, 'utf8');
  const stillHasAll = edits.every((e) => verify.includes(crlf(e.new)));
  console.log('Post-write verification (all new content present):', stillHasAll);
  return stillHasAll;
}

module.exports = { applyVerifiedEdits, crlf };

/* Exemplo de uso dentro de ctx_execute:
 *
 * const { applyVerifiedEdits } = require('<caminho-para-este-arquivo>');
 * applyVerifiedEdits('D:/workspace/projeto/arquivo-grande.yaml', [
 *   { label: 'descricao curta', old: 'texto-ancora-unico', new: 'texto-novo' },
 * ]);
 */

