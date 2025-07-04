# ──────────────────────────────────────────────────────────────────────────────
# Stage 1: pull in uv (and uvx) from Astral's slim image
# ──────────────────────────────────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS uv-binaries

# ──────────────────────────────────────────────────────────────────────────────
# Stage 2: build our actual application image
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS final

# 1. Copy both /usr/local/bin/uv and /usr/local/bin/uvx (so uv & uvx are on PATH)
COPY --from=uv-binaries /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

# 2. Set the working directory to /app
WORKDIR /app

# 3. Copy requirements file
COPY pyproject.toml ./

# 4. Use uv to create a `.venv` with dependencies
RUN uv sync

# 5. Copy the rest of your application code
COPY . .

# 6. Prepend the venv's bin directory
ENV PATH="/app/.venv/bin:$PATH"

# 7. Run the client
CMD ["uv", "run", "client.py"] 