#!/usr/bin/env node
/**
 * Stop-Hook Mecânico de Validação de `receipt` + `step_delta`, `allowed_files` e Micro-Tarefas (R-064 / R-068).
 * Fonte de verdade do contrato: .github/skills/agent-contracts/references/receipt-step-delta-schema.yaml
 */

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { execSync } = require('node:child_process');

const REQUIRED_RECEIPT_FIELDS = [
  'receipt_id',
  'n',
  'agent',
  'banner_ref',
  'handoff_seq',
  'artefato',
  'plan_ref',
  'gate_resolucao',
  'verdict_from_agent',
  'status',
];

const VALID_STATUS = new Set(['done', 'failed', 'blocked']);
const VALID_MODES = new Set(['mutation', 'readonly_analysis']);
const MAX_INLINE_ITEMS = 10;
const HARNESS_IGNORED_PREFIXES = ['.context/', '.worktrees/'];
const BASELINE_REL_PATH = '.context/.subagent-baseline.json';

function normalizeRelPath(p) {
  return String(p || '')
      .trim()
      .replace(/\\/g, '/')
      .replace(/^\.\//, '');
}

function stripInlineComment(line) {
  let quote = null;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if ((ch === '"' || ch === "'") && line[i - 1] !== '\\') {
      quote = quote === ch ? null : quote || ch;
    } else if (!quote && ch === '#' && (i === 0 || /\s/.test(line[i - 1]))) {
      return line.slice(0, i);
    }
  }
  return line;
}

function parseSimpleYaml(yamlText) {
  const lines = yamlText.replace(/\r\n/g, '\n').split('\n');
  const root = {};
  const stack = [{ indent: -1, container: root, key: null }];

  function splitTopLevelCsv(str) {
    const items = [];
    let current = '';
    let depth = 0;
    let quote = null;

    for (let i = 0; i < str.length; i += 1) {
      const ch = str[i];
      if (quote) {
        current += ch;
        if (ch === quote && str[i - 1] !== '\\') quote = null;
        continue;
      }
      if (ch === '"' || ch === "'") {
        quote = ch;
        current += ch;
      } else if (ch === '{' || ch === '[') {
        depth += 1;
        current += ch;
      } else if (ch === '}' || ch === ']') {
        depth = Math.max(0, depth - 1);
        current += ch;
      } else if (ch === ',' && depth === 0) {
        if (current.trim()) items.push(current.trim());
        current = '';
      } else {
        current += ch;
      }
    }
    if (current.trim()) items.push(current.trim());
    return items;
  }

  function parseScalar(raw) {
    const trimmed = raw.trim();
    if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
      const obj = {};
      const pairs = splitTopLevelCsv(trimmed.slice(1, -1));
      for (const pair of pairs) {
        const sep = pair.indexOf(':');
        if (sep !== -1) {
          const k = pair.slice(0, sep).trim().replace(/^["']|["']$/g, '');
          const v = pair.slice(sep + 1).trim();
          obj[k] = parseScalar(v);
        }
      }
      return obj;
    }
    if (trimmed === '' || trimmed === 'null' || trimmed === '~') return null;
    if (trimmed === 'true') return true;
    if (trimmed === 'false') return false;
    if (trimmed === '[]') return [];
    if (trimmed === '{}') return {};
    if (/^-?\d+$/.test(trimmed)) return Number.parseInt(trimmed, 10);
    if (
        (trimmed.startsWith('"') && trimmed.endsWith('"')) ||
        (trimmed.startsWith("'") && trimmed.endsWith("'"))
    ) {
      return trimmed.slice(1, -1);
    }
    if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
      const inner = trimmed.slice(1, -1).trim();
      if (!inner) return [];
      return splitTopLevelCsv(inner).map((item) => parseScalar(item));
    }
    return trimmed;
  }

  for (let i = 0; i < lines.length; i += 1) {
    const rawLine = lines[i];
    const withoutComment = stripInlineComment(rawLine);
    if (!withoutComment.trim() || withoutComment.trim().startsWith('#')) continue;

    const indent = withoutComment.match(/^ */)[0].length;
    const content = withoutComment.trim();

    while (stack.length > 1 && indent <= stack[stack.length - 1].indent) {
      stack.pop();
    }
    const parent = stack[stack.length - 1];

    if (content.startsWith('- ')) {
      const itemText = content.slice(2).trim();
      if (!Array.isArray(parent.container)) {
        const grandParent = stack[stack.length - 2];
        if (grandParent && parent.key) {
          const arr = [];
          grandParent.container[parent.key] = arr;
          parent.container = arr;
        }
      }
      const colonIdx = itemText.indexOf(':');
      if (colonIdx > 0 && !itemText.startsWith('"') && !itemText.startsWith("'")) {
        const k = itemText.slice(0, colonIdx).trim();
        const vRaw = itemText.slice(colonIdx + 1).trim();
        const obj = {};
        obj[k] = vRaw === '' ? {} : parseScalar(vRaw);
        parent.container.push(obj);
        stack.push({ indent, container: obj, key: k });
      } else {
        parent.container.push(parseScalar(itemText));
      }
      continue;
    }

    const colonIdx = content.indexOf(':');
    if (colonIdx > 0) {
      const key = content.slice(0, colonIdx).trim();
      const valRaw = content.slice(colonIdx + 1).trim();

      if (/^[|>][+-]?$/.test(valRaw)) {
        const blockLines = [];
        while (i + 1 < lines.length) {
          const nextLine = lines[i + 1];
          if (!nextLine.trim()) {
            blockLines.push('');
            i += 1;
            continue;
          }
          const nextIndent = nextLine.match(/^ */)[0].length;
          if (nextIndent <= indent) break;
          blockLines.push(nextLine.slice(indent + 2));
          i += 1;
        }
        parent.container[key] = blockLines.join(valRaw.startsWith('>') ? ' ' : '\n').trim();
        continue;
      }

      if (valRaw === '') {
        const nextObj = {};
        parent.container[key] = nextObj;
        stack.push({ indent, container: nextObj, key });
      } else {
        parent.container[key] = parseScalar(valRaw);
      }
    }
  }

  return root;
}

function extractReceiptFromText(text) {
  if (!text || typeof text !== 'string') return null;
  const fenceRegex = /```(?:ya?ml)?\s*\n([\s\S]*?)```/gi;
  let match;
  let lastYaml = null;
  while ((match = fenceRegex.exec(text)) !== null) {
    if (/^\s*receipt\s*:/m.test(match[1])) {
      lastYaml = match[1];
    }
  }
  if (!lastYaml) return null;
  const parsed = parseSimpleYaml(lastYaml);
  return parsed && parsed.receipt ? parsed.receipt : null;
}

function readMarkdownFrontmatter(filePath) {
  if (!fs.existsSync(filePath)) return null;
  const raw = fs.readFileSync(filePath, 'utf8').replace(/\r\n/g, '\n');
  if (!raw.startsWith('---\n')) return null;
  const endIdx = raw.indexOf('\n---\n', 4);
  if (endIdx === -1) return null;
  return parseSimpleYaml(raw.slice(4, endIdx));
}

function getGitChangedFiles(cwd) {
  try {
    const out = execSync('git status --porcelain -uall', {
      cwd,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    });
    return out
        .split(/\r?\n/)
        .filter((line) => line.length >= 4)
        .map((line) => {
          let rel = line.slice(3).trim();
          if (rel.includes(' -> ')) {
            rel = rel.split(' -> ').pop().trim();
          }
          return normalizeRelPath(rel.replace(/^"|"$/g, ''));
        })
        .filter(
            (rel) =>
                rel &&
                !HARNESS_IGNORED_PREFIXES.some((prefix) => rel.startsWith(prefix))
        );
  } catch {
    return [];
  }
}

function fingerprintFile(cwd, relPath) {
  try {
    const abs = path.resolve(cwd, relPath);
    if (!fs.existsSync(abs)) return 'DELETED';
    const stat = fs.statSync(abs);
    if (stat.isDirectory()) return 'DIR';
    const buf = fs.readFileSync(abs);
    return crypto.createHash('sha1').update(buf).digest('hex');
  } catch {
    return 'UNREADABLE';
  }
}

function captureTurnBaseline(cwd) {
  const changed = getGitChangedFiles(cwd);
  const files = {};
  for (const rel of changed) {
    files[rel] = fingerprintFile(cwd, rel);
  }
  const baselinePath = path.resolve(cwd, BASELINE_REL_PATH);
  fs.mkdirSync(path.dirname(baselinePath), { recursive: true });
  fs.writeFileSync(
      baselinePath,
      JSON.stringify({ captured_at: new Date().toISOString(), files }, null, 2),
      'utf8'
  );
}

function removeTurnBaseline(cwd) {
  const baselinePath = path.resolve(cwd, BASELINE_REL_PATH);
  try {
    if (fs.existsSync(baselinePath)) {
      fs.unlinkSync(baselinePath);
    }
  } catch {
    // ignore cleanup error
  }
}

function getTurnChangedFiles(cwd, options = {}) {
  const { consumeBaseline = true } = options;
  const currentChanged = getGitChangedFiles(cwd);
  const baselinePath = path.resolve(cwd, BASELINE_REL_PATH);
  if (!fs.existsSync(baselinePath)) {
    return currentChanged;
  }

  let baselineFiles = {};
  try {
    const parsed = JSON.parse(fs.readFileSync(baselinePath, 'utf8'));
    baselineFiles = (parsed && parsed.files) || {};
  } catch {
    baselineFiles = {};
  } finally {
    if (consumeBaseline) {
      removeTurnBaseline(cwd);
    }
  }

  return currentChanged.filter((rel) => {
    if (!(rel in baselineFiles)) return true;
    return fingerprintFile(cwd, rel) !== baselineFiles[rel];
  });
}

function matchesAllowedPattern(filePath, pattern) {
  const normFile = normalizeRelPath(filePath);
  const normPat = normalizeRelPath(pattern);
  if (!normPat) return false;
  if (normFile === normPat) return true;
  if (normPat.endsWith('/') && normFile.startsWith(normPat)) return true;
  if (normPat.includes('*')) {
    const escaped = normPat
        .replace(/[.+^${}()|[\]\\]/g, '\\$&')
        .replace(/\*\*\//g, '.__GLOBSTAR_DIR__.')
        .replace(/\*\*/g, '.__GLOBSTAR__.')
        .replace(/\*/g, '[^/]*')
        .replace(/\.__GLOBSTAR_DIR__\./g, '(?:.+/)?')
        .replace(/\.__GLOBSTAR__\./g, '.*');
    return new RegExp(`^${escaped}$`).test(normFile);
  }
  return false;
}

function checkAllowedFiles(touchedFiles, allowedFiles) {
  if (!Array.isArray(allowedFiles)) {
    return { within_allowed_files: true, out_of_scope_files: [] };
  }
  if (allowedFiles.length === 0) {
    return {
      within_allowed_files: touchedFiles.length === 0,
      out_of_scope_files: [...touchedFiles],
    };
  }
  const outOfScope = touchedFiles.filter(
      (f) => !allowedFiles.some((pat) => matchesAllowedPattern(f, pat))
  );
  return {
    within_allowed_files: outOfScope.length === 0,
    out_of_scope_files: outOfScope,
  };
}

function validateReceiptPayload({ receipt, cwd, gitChangedFiles }) {
  const errors = [];

  if (!receipt || typeof receipt !== 'object') {
    errors.push(
        'R-068: Bloco YAML `receipt:` obrigatório ausente na conclusão da etapa.'
    );
    return { valid: false, errors, driftDetected: false };
  }

  for (const field of REQUIRED_RECEIPT_FIELDS) {
    if (
        receipt[field] === undefined ||
        receipt[field] === null ||
        receipt[field] === ''
    ) {
      errors.push(`R-068: Campo obrigatório 'receipt.${field}' ausente ou vazio.`);
    }
  }

  if (typeof receipt.agent === 'string') {
    if (!/^@[a-z0-9-]+$/.test(receipt.agent)) {
      errors.push(
          `R-068: 'receipt.agent' inválido ('${receipt.agent}'); esperado padrão '^@[a-z0-9-]+$'.`
      );
    }
    if (receipt.agent.startsWith('@specialist-')) {
      errors.push(
          `Invariante 7: Slug genérico proibido em 'receipt.agent' ('${receipt.agent}'). Use o nome concreto do catálogo.`
      );
    }
  }

  if (receipt.status && !VALID_STATUS.has(receipt.status)) {
    errors.push(
        `R-068: 'receipt.status' inválido ('${receipt.status}'); valores permitidos: done, failed, blocked.`
    );
  }

  let driftDetected = false;
  const hasDeltaObj = receipt.step_delta && typeof receipt.step_delta === 'object';
  const delta = hasDeltaObj ? receipt.step_delta : {};

  if (receipt.status === 'done') {
    if (!hasDeltaObj) {
      errors.push(
          "R-068: 'receipt.step_delta' é obrigatório quando 'status == done'."
      );
      return { valid: false, errors, driftDetected };
    }

    if (!VALID_MODES.has(delta.mode)) {
      errors.push(
          `R-068: 'step_delta.mode' inválido ('${delta.mode}'); esperado 'mutation' ou 'readonly_analysis'.`
      );
    }

    if (
        delta.notes_for_next_step === undefined ||
        delta.notes_for_next_step === null ||
        String(delta.notes_for_next_step).trim() === ''
    ) {
      errors.push("R-068: 'step_delta.notes_for_next_step' é obrigatório.");
    }

    const listFields = [
      'files_modified',
      'files_created',
      'exports_and_signatures',
    ];
    for (const lf of listFields) {
      const arr = Array.isArray(delta[lf]) ? delta[lf] : [];
      if (arr.length > MAX_INLINE_ITEMS) {
        errors.push(
            `R-068: 'step_delta.${lf}' excedeu o teto de ${MAX_INLINE_ITEMS} itens inline (${arr.length}). Use overflow_ref.`
        );
      }
    }

    const conformance = delta.plan_conformance;
    if (!conformance || typeof conformance !== 'object') {
      errors.push("R-064/R-068: 'step_delta.plan_conformance' é obrigatório.");
    } else {
      if (conformance.within_allowed_files === false) {
        driftDetected = true;
        errors.push(
            'R-064 (plan_drift_detected): step_delta.plan_conformance.within_allowed_files == false.'
        );
      }
      if (
          Array.isArray(conformance.out_of_scope_files) &&
          conformance.out_of_scope_files.length > 0
      ) {
        driftDetected = true;
        errors.push(
            `R-064 (plan_drift_detected): Arquivos fora de escopo declarados: ${conformance.out_of_scope_files.join(', ')}`
        );
      }
    }
  }

  const declaredModified = Array.isArray(delta.files_modified)
      ? delta.files_modified.map((item) =>
          typeof item === 'string' ? item : item && item.path
      )
      : [];
  const declaredCreated = Array.isArray(delta.files_created)
      ? delta.files_created.map((item) =>
          typeof item === 'string' ? item : item && item.path
      )
      : [];

  const allTouched = Array.from(
      new Set(
          [...declaredModified, ...declaredCreated, ...(gitChangedFiles || [])]
              .map(normalizeRelPath)
              .filter(Boolean)
      )
  );

  if (delta.mode === 'readonly_analysis' && allTouched.length > 0) {
    errors.push(
        `R-056/R-068: Agente 'readonly_analysis' não pode mutar arquivos (${allTouched.join(', ')}).`
    );
  }

  if (Array.isArray(delta.target_files) && delta.target_files.length > 0 && allTouched.length > 0) {
    const taskScopeCheck = checkAllowedFiles(allTouched, delta.target_files);
    if (!taskScopeCheck.within_allowed_files) {
      driftDetected = true;
      errors.push(
          `R-068 (micro_task_scope_violation): Mutação fora de target_files da micro-tarefa${delta.task_id ? ` '${delta.task_id}'` : ''}: ${taskScopeCheck.out_of_scope_files.join(', ')}`
      );
    }
  }

  if (receipt.plan_ref && receipt.plan_ref !== 'N/A') {
    const planAbsPath = path.resolve(cwd, receipt.plan_ref);
    const fm = readMarkdownFrontmatter(planAbsPath);
    if (!fm) {
      errors.push(
          `R-064: Plano referenciado não encontrado ou sem frontmatter válido: '${receipt.plan_ref}'.`
      );
    } else {
      const VALID_PLAN_EXEC_STATUS = new Set(['APPROVED', 'IN_PROGRESS']);
      if (
          (receipt.status === 'done' || allTouched.length > 0) &&
          (!fm.status || !VALID_PLAN_EXEC_STATUS.has(fm.status))
      ) {
        errors.push(
            `R-064: Plano '${receipt.plan_ref}' está com status '${fm.status || 'AUSENTE'}' (exigido: 'APPROVED' ou 'IN_PROGRESS').`
        );
      }
      if (Array.isArray(fm.allowed_files) && allTouched.length > 0) {
        const scopeCheck = checkAllowedFiles(allTouched, fm.allowed_files);
        if (!scopeCheck.within_allowed_files) {
          driftDetected = true;
          errors.push(
              `R-064 (plan_drift_detected): Mutação detectada fora de allowed_files do plano '${receipt.plan_ref}': ${scopeCheck.out_of_scope_files.join(', ')}`
          );
        }
      }
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    driftDetected,
  };
}

function extractAssistantText(hookInput) {
  if (!hookInput || typeof hookInput !== 'object') return '';
  const candidates = [
    hookInput.last_assistant_message,
    hookInput.lastAssistantMessage,
    hookInput.assistant_message,
    hookInput.output,
    hookInput.response,
    hookInput.message && hookInput.message.content,
  ];
  for (const c of candidates) {
    if (typeof c === 'string' && c.trim()) return c;
  }
  return '';
}

function runHook(rawStdin, defaultCwd = process.cwd()) {
  let hookInput = {};
  if (rawStdin && rawStdin.trim()) {
    try {
      hookInput = JSON.parse(rawStdin);
    } catch {
      hookInput = {};
    }
  }

  const cwd = hookInput.cwd ? path.resolve(hookInput.cwd) : defaultCwd;
  const eventLower = String(hookInput.hook_event_name || hookInput.hookEventName || '').toLowerCase();
  const isSubagentStop = eventLower === 'subagentstop';

  if (eventLower === 'subagentstart') {
    captureTurnBaseline(cwd);
    return {
      exitCode: 0,
      output: { decision: 'approve' },
    };
  }

  if (hookInput.stop_hook_active === true || hookInput.stopHookActive === true) {
    return {
      exitCode: 0,
      output: { decision: 'approve' },
    };
  }

  const assistantText = extractAssistantText(hookInput);
  const receipt = extractReceiptFromText(assistantText);

  if (eventLower === 'stop' && !receipt && /^\s*workflow_tracking\s*:/m.test(assistantText)) {
    removeTurnBaseline(cwd);
    return {
      exitCode: 0,
      output: { decision: 'approve' },
    };
  }

  const gitChangedFiles = getTurnChangedFiles(cwd, { consumeBaseline: false });

  if (!receipt && gitChangedFiles.length === 0) {
    if (!isSubagentStop) {
      removeTurnBaseline(cwd);
    }
    return {
      exitCode: 0,
      output: { decision: 'approve' },
    };
  }

  const result = validateReceiptPayload({
    receipt,
    cwd,
    gitChangedFiles,
  });

  if (result.valid) {
    if (isSubagentStop) {
      captureTurnBaseline(cwd);
    } else {
      removeTurnBaseline(cwd);
    }
    return {
      exitCode: 0,
      output: { decision: 'approve' },
    };
  }

  const prefix = result.driftDetected
      ? 'PLAN_DRIFT_DETECTED (R-064)'
      : 'RECEIPT_VALIDATION_FAILED (R-068)';
  const reason = `${prefix}: ${result.errors.join(' | ')}`;

  return {
    exitCode: 2,
    output: {
      decision: 'block',
      reason,
      drift_detected: result.driftDetected,
      errors: result.errors,
    },
  };
}

if (require.main === module) {
  let stdinData = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (chunk) => {
    stdinData += chunk;
  });
  process.stdin.on('end', () => {
    const res = runHook(stdinData, process.cwd());
    process.stdout.write(`${JSON.stringify(res.output)}\n`);
    process.exit(res.exitCode);
  });
}

module.exports = {
  parseSimpleYaml,
  extractReceiptFromText,
  readMarkdownFrontmatter,
  getGitChangedFiles,
  captureTurnBaseline,
  getTurnChangedFiles,
  checkAllowedFiles,
  validateReceiptPayload,
  runHook,
};
