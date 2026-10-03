import type { NextConfig } from "next";

/**
 * next.config.ts — Deep Agents Chat
 *
 * `output: "standalone"` gera um bundle de servidor autocontido (usado pelo
 * Dockerfile multi-stage, sem precisar de `node_modules` completo em
 * runtime). Ver docker-compose.yml do gateway (servico `web`).
 */
const nextConfig: NextConfig = {
  output: "standalone",
  reactStrictMode: true,
  // Painel flutuante "N" (Dev Tools) do Next.js 15+/16 — botao canto
  // inferior esquerdo. Suas preferencias (tema/posicao/tamanho) afetam
  // apenas o proprio painel de debug do framework, nunca a aplicacao em si
  // — comportamento esperado do Next.js, nao um bug. Mantido habilitado
  // (decisao do usuario, 2026-10-01) apesar dos textos hardcoded em ingles
  // (sem i18n oficial do Next.js).
};

export default nextConfig;

