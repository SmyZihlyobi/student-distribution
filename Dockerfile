FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime AS runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY . .

RUN uv venv
RUN uv sync

CMD ["uv", "run", "python", "src/main.py"]