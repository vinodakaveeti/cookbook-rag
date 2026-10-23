FROM python:3.14-slim

Workdir /app

# Build tools are useful for Python packages with native extensions.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl zstd \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | sh

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /data/chroma /data/uploads

ENV OLLAMA_URL=http://127.0.0.1:11434 \
    OLLAMA_MODELS=/data/ollama \
    MODEL_NAME=qwen3:4b \
    EMBEDDING_MODEL=nomic-embed-text

RUN chmod +x /app/script.sh

EXPOSE 8080
CMD ["sh", "/app/script.sh"]