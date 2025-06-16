FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime AS runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY . .

RUN uv venv
RUN uv sync

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]