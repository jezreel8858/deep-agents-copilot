import { z } from "zod";

/**
 * env — validacao estrita de variaveis de ambiente SOMENTE de servidor.
 *
 * Nenhuma variavel aqui deve ter prefixo `NEXT_PUBLIC_`: o segredo
 * `GATEWAY_API_KEY` nunca pode ser embutido no bundle do browser (R7 do
 * blueprint de migracao LobeChat -> CopilotKit). Este modulo so deve ser
 * importado por codigo que roda em Route Handlers / Server Components
 * (`app/api/**`, `middleware.ts`).
 */
const envSchema = z.object({
  GATEWAY_BASE_URL: z
    .string()
    .url()
    .default("http://127.0.0.1:8080"),
  GATEWAY_API_KEY: z.string().min(1, "GATEWAY_API_KEY e obrigatoria"),
  GATEWAY_MODEL: z.string().default("deep-agents/router"),
  WEB_ACCESS_CODE: z.string().min(1, "WEB_ACCESS_CODE e obrigatoria"),
});

export type Env = z.infer<typeof envSchema>;

let cached: Env | null = null;

/** Valida (uma unica vez, com cache em memoria do processo) e retorna o ambiente. */
export function getEnv(): Env {
  if (cached) return cached;
  const parsed = envSchema.safeParse(process.env);
  if (!parsed.success) {
    const motivo = parsed.error.issues
      .map((i) => `${i.path.join(".")}: ${i.message}`)
      .join("; ");
    throw new Error(`Configuracao de ambiente invalida (Deep Agents Chat): ${motivo}`);
  }
  if (parsed.data.WEB_ACCESS_CODE === "change-me" || parsed.data.GATEWAY_API_KEY === "change-me") {
    throw new Error(
      "WEB_ACCESS_CODE/GATEWAY_API_KEY nao podem ser 'change-me' — defina valores reais no .env"
    );
  }
  cached = parsed.data;
  return cached;
}

