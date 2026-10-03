# syntax=docker/dockerfile:1
# apps/web/Dockerfile — build context = RAIZ DO REPOSITORIO (ver
# docker-compose.yml do gateway, servico "web": context: ../..).
#
# Cache mounts do BuildKit (--mount=type=cache): persistem o cache de
# download do npm e o cache incremental do Next.js ENTRE builds,
# independente do cache de camada do Docker -- redownload/recompilacao
# minima mesmo quando a camada de `npm install`/`npm run build` precisa
# ser reexecutada (ex.: package.json mudou, mas a maioria dos pacotes
# permanece igual). O cache de camada padrao do Docker (baseado no hash
# do COPY package.json/package-lock.json) ja evita reexecutar `npm
# install` quando nada muda; o cache mount cobre o caso de MUDANCA
# parcial (evita rebaixar a internet inteira por causa de 1 dependencia).

FROM node:22-alpine AS deps
WORKDIR /app
COPY apps/web/package.json apps/web/package-lock.json* ./apps/web/
WORKDIR /app/apps/web
RUN --mount=type=cache,target=/root/.npm,sharing=locked \
    npm install --no-audit --no-fund --prefer-offline

FROM node:22-alpine AS builder
WORKDIR /app
COPY apps/web ./apps/web
COPY --from=deps /app/apps/web/node_modules ./apps/web/node_modules
WORKDIR /app/apps/web
ENV NEXT_TELEMETRY_DISABLED=1
RUN --mount=type=cache,target=/app/apps/web/.next/cache,sharing=locked \
    npm run build

FROM node:22-alpine AS runtime
RUN addgroup -g 10001 webgroup && adduser -D -u 10001 -G webgroup webuser
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV COPILOTKIT_TELEMETRY_DISABLED=true
# Next `output: "standalone"` traca a partir de apps/web (nao ha lockfile
# na raiz do monorepo) -- server.js fica direto em .next/standalone/,
# sem prefixo "apps/web/".
COPY --from=builder --chown=webuser:webgroup /app/apps/web/.next/standalone ./
COPY --from=builder --chown=webuser:webgroup /app/apps/web/.next/static ./.next/static
COPY --from=builder --chown=webuser:webgroup /app/apps/web/public ./public
USER webuser:webgroup
EXPOSE 3000
CMD ["node", "server.js"]

