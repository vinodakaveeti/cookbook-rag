#!/bin/sh
set -eu

export OLLAMA_HOST="${OLLAMA_HOST:-http://127.0.0.1:11434}"
export OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"
export OLLAMA_MODELS="${OLLAMA_MODELS:-/data/ollama}"
export MODEL_NAME="${MODEL_NAME:-qwen3:4b}"
export EMBEDDING_MODEL="${EMBEDDING_MODEL:-nomic-embed-text}"

mkdir -p "$OLLAMA_MODELS"

ollama serve &
OLLAMA_PID=$!

cleanup() {
  kill "$OLLAMA_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Wait for Ollama to start, and fail with a useful message if it exits.
attempt=0
until curl -fsS http://127.0.0.1:11434/api/tags >/dev/null; do
  if ! kill -0 "$OLLAMA_PID" 2>/dev/null; then
    echo "Ollama stopped before becoming ready."
    exit 1
  fi

  attempt=$((attempt + 1))
  if [ "$attempt" -ge 90 ]; then
    echo "Timed out waiting for Ollama."
    exit 1
  fi
  sleep 1
done

# These are safe to run at startup; already-downloaded models are reused.
ollama pull "$MODEL_NAME"
ollama pull "$EMBEDDING_MODEL"

uvicorn main:app --host 0.0.0.0 --port "${PORT:-8080}" &
API_PID=$!
wait "$API_PID"