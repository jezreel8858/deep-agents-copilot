/**
 * PX-08: Mascaramento local de segredos antes de exportar
 */
const PATTERNS = [
  { regex: /(ghp_|gho_|github_pat_)[A-Za-z0-9_]+/g, replace: '***REDACTED_GH***' },
  { regex: /(sk|pk)-lf-[A-Za-z0-9-]+/g, replace: '***REDACTED_LF***' },
  { regex: /sk-[A-Za-z0-9]{20,}/g, replace: '***REDACTED_KEY***' },
  { regex: /Bearer\s+[A-Za-z0-9._~+/=-]+/gi, replace: 'Bearer ***REDACTED***' },
  { regex: /AKIA[0-9A-Z]{16}/g, replace: '***REDACTED_AWS***' },
  { regex: /-----BEGIN [A-Z ]+ PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+ PRIVATE KEY-----/g, replace: '***REDACTED_PRIVATE_KEY***' }
];

function redact(text) {
  if (typeof text !== 'string') return text;
  let result = text;
  for (const { regex, replace } of PATTERNS) {
    result = result.replace(regex, replace);
  }
  return result;
}

function truncateAndRedact(value, maxBytes = 16384) {
  if (value === undefined || value === null) return '';
  let str = typeof value === 'string' ? value : JSON.stringify(value);
  str = redact(str);
  const buf = Buffer.from(str, 'utf8');
  if (buf.length > maxBytes) {
    const truncated = buf.subarray(0, maxBytes).toString('utf8');
    return truncated + `…[truncated ${buf.length - maxBytes} bytes]`;
  }
  return str;
}

module.exports = { redact, truncateAndRedact };
