FROM node:22-bookworm-slim AS web
WORKDIR /src
COPY contracts ./contracts
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN --mount=type=secret,id=build_ca \
    if [ -f /run/secrets/build_ca ]; then export NODE_EXTRA_CA_CERTS=/run/secrets/build_ca; fi; \
    cd frontend && npm ci
COPY frontend ./frontend
RUN cd frontend && VITE_MB_MODE=cloud npm run build

FROM python:3.12.14-slim-bookworm AS app
COPY --from=ghcr.io/astral-sh/uv:0.9.18 /uv /uvx /bin/
WORKDIR /app
COPY python ./python
COPY contracts ./contracts
COPY campaigns ./campaigns
COPY scripts ./scripts
COPY deploy ./deploy
COPY build_info.json ./build_info.json
RUN --mount=type=secret,id=build_ca \
    if [ -f /run/secrets/build_ca ]; then export SSL_CERT_FILE=/run/secrets/build_ca UV_NATIVE_TLS=true; fi; \
    cd python && uv sync --frozen --all-packages --no-dev
COPY --from=web /src/frontend/dist ./frontend/dist
ENV MB_MODE=cloud MB_DATA_DIR=/data/monopolybench RUNS_DIR=/data/monopolybench/runs PATH="/app/python/.venv/bin:$PATH" PYTHONUNBUFFERED=1
CMD ["python", "-m", "monopoly_api.serve"]
