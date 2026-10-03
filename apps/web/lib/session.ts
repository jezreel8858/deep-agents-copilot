const THREAD_ID_PATTERN = /^[A-Za-z0-9_-]{1,64}$/;

/**
 * Valida um `threadId`/`X-Thread-Id` recebido do CopilotKit antes de
 * repassa-lo ao gateway como `X-Session-Id`. Retorna `null` se invalido
 * (o header e simplesmente omitido — o gateway deriva a sessao pelo hash
 * da 1a mensagem nesse caso).
 */
export function sanitizeThreadId(raw: string | null | undefined): string | null {
  if (!raw) return null;
  return THREAD_ID_PATTERN.test(raw) ? raw : null;
}

