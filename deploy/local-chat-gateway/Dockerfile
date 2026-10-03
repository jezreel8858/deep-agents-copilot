# syntax=docker/dockerfile:1
# ==============================================================================
# Deep Agents Gateway - Dockerfile multi-stage (nao-root, imagem minima)
#
# IMPORTANTE: o build context DEVE ser a RAIZ DO REPOSITORIO (nao este
# diretorio), pois e necessario instalar a dependencia editavel local
# "governance-runner" (tools/headless-governance-runner) ANTES do pacote
# "Deep Agents Gateway". Ver docs/architecture/BLUEPRINT_LOCAL_CHAT_GATEWAY.md
# Secao 3.1.
#
# Build (a partir da raiz do repo):
#   docker build -f deploy/local-chat-gateway/Dockerfile -t deep-agents-gateway:local .
# Ou via docker-compose.yml deste diretorio (ja configurado com o context correto):
#   docker compose build gateway
# ==============================================================================

FROM python:3.12-slim AS builder
WORKDIR /build

# Copia apenas os artefatos necessarios para o build (evita invalidar cache de
# camada com o restante do monorepo; o .dockerignore/Dockerfile.dockerignore
# neste diretorio ja restringe o que chega ao contexto de build).
COPY tools/headless-governance-runner /build/tools/headless-governance-runner
COPY deploy/local-chat-gateway /build/deploy/local-chat-gateway

# Instala em --prefix isolado para copiar apenas os artefatos resultantes
# (sem cache de build, sem toolchain de compilacao) para o estagio de runtime.
#
# IMPORTANTE: os dois pacotes locais (governance-runner e deep-agents-gateway)
# DEVEM ser instalados na MESMA invocacao de "pip install". Se forem
# instalados em comandos separados (mesmo com o mesmo --prefix), o resolver
# de dependencias do segundo comando NAO enxerga o pacote instalado pelo
# primeiro (o caminho --prefix=/install nao esta no sys.path usado pela
# resolucao de dependencias) e tenta buscar "governance-runner" no indice
# publico do PyPI, onde o pacote nao existe -> "No matching distribution
# found for governance-runner". Instalando ambos juntos, o pip resolve as
# duas arvores de dependencia em conjunto e satisfaz "governance-runner"
# diretamente a partir do diretorio local, sem tocar a rede para ele.
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install --upgrade pip \
    && pip install --prefix=/install \
       /build/tools/headless-governance-runner \
       "/build/deploy/local-chat-gateway[sdk]"

# Nota: nao ha pre-download do runtime bundled do Copilot CLI aqui de
# proposito -- o pacote Python "github-copilot-sdk" ja baixa/empacota o
# runtime automaticamente no 1o uso (confirmado pelo spike RT-01), e o
# diretorio de cache desse download nao seria copiado para o estagio
# "runtime" abaixo (so copiamos /install). Antecipar o download aqui
# seria apenas trabalho de build desperdicado sem beneficio real.

# ------------------------------------------------------------------------------
FROM python:3.12-slim AS runtime
WORKDIR /app

# Usuario/grupo nao-root dedicados, com home writable (necessario -- o SDK
# real do Copilot grava, no primeiro uso real de uma sessao, tanto o cache
# do binario do runtime CLI ("$HOME/.cache/github-copilot-sdk/...") quanto
# logs/estado do processo nativo em OUTROS subdiretorios de "$HOME"
# (confirmado via teste real: montar volume so em "$HOME/.cache" nao e
# suficiente -- "session construction failed: EROFS" ocorre ao gravar fora
# dele). O diretorio em si fica no filesystem raiz (read-only em runtime);
# a escrita real so e possivel porque o docker-compose.yml monta um volume
# nomeado cobrindo TODO o "$HOME" ("gateway-home:/home/gateway").
RUN groupadd --gid 10001 gateway \
    && useradd --uid 10001 --gid gateway --create-home --shell /usr/sbin/nologin gateway

# Copia somente os pacotes Python instalados no estagio builder (nenhum
# toolchain de build, nenhum codigo-fonte adicional).
COPY --from=builder /install /usr/local

# Diretorio de dados (SQLite do SessionStore), /tmp e o mountpoint do HOME
# do usuario gateway (o volume em si e declarado no docker-compose.yml;
# aqui so garantimos que o mountpoint exista com o dono certo antes do
# volume ser montado por cima).
RUN mkdir -p /app/data /tmp/gateway /home/gateway/.cache \
    && chown -R gateway:gateway /app /tmp/gateway /home/gateway

USER 10001
ENV HOME=/home/gateway

EXPOSE 8080

# Healthcheck sem dependencia de curl/wget (nao instalados na imagem slim):
# usa a stdlib do proprio Python ja presente na imagem.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=3)" || exit 1

ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["local_chat_gateway.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080"]
