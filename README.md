# Cookbook RAG System

A Retrieval-Augmented Generation (RAG) system for searching cookbook recipes using local LLMs via Ollama.

## Overview

This project provides a simple API to:
- Upload PDF cookbooks (processed, chunked, embedded, and stored in a vector database)
- Search for recipes using natural language queries
- Retrieve AI-generated answers based on the uploaded cookbook content

The UI was built with vibe coding and focuses solely on searching/retrieving recipes.

## Models & Technologies Used

| Component | Technology / Model | Details |
|-----------|-------------------|---------|
| **LLM (Language Model)** | `qwen3:4b` (via Ollama) | Default; override via `MODEL_NAME` env var |
| **Embedding Model** | `nomic-embed-text` (via Ollama) | Generates vector embeddings for text chunks |
| **Vector Database** | ChromaDB | Local persistent store (`./chroma_data`) |
| **Text Chunking** | LangChain's `RecursiveCharacterTextSplitter` | ~1800 chars with 200 overlap |
| **PDF Processing** | PyMuPDF (`fitz`) | Extracts text from uploaded PDFs |
| **Backend Framework** | FastAPI | REST endpoints: `/add-document`, `/search` |

Environment variables (`constants.py`):
- `OLLAMA_URL`: Base URL for Ollama API (default: `http://localhost:11434`)
- `MODEL_NAME`: LLM model to use (default: `qwen3:4b`)

## How to Run

### Prerequisites
1. **Ollama** installed and running locally with the required models:
   ```bash
   ollama pull qwen3:4b
   ollama pull nomic-embed-text
   ```
2. **Python 3.9+** and required packages (see imports or install via):
   ```bash
   pip install fastapi uvicorn ollama langchain-text-splitters chromadb pymupdf
   ```

### Backend API
1. Ensure you have the project files.
2. (Optional) Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt   # or install packages manually
   ```
4. Start the FastAPI server:
   ```bash
   python main.py
   ```
   API available at `http://127.0.0.1:8000`:
   - **Upload**: `POST /add-document` (multipart/form-data, file field `file`, PDF only)
   - **Search**: `POST /search` (JSON `{ "query": "...", "top_k": 3 }`)

## Usage
1. Start the backend (`python main.py`).
2. Use the UI to:
   - Enter a natural language query (e.g., `"How to make tiramisu?"`).
   - Set desired number of results (1‑10).
   - Click **Search Recipes**.
3. The backend embeds the query, searches ChromaDB, and asks the LLM to answer using only the retrieved cookbook context.
4. The UI displays the answer as a formatted recipe card (when JSON matches expected structure) or as plain text/pretty‑printed JSON otherwise.

## Notes
- The UI does not expose an upload form; to add new cookbooks call `/add-document` directly, e.g.:
  ```bash
  curl -X POST "http://127.0.0.1:8000/add-document" -F "file=@/path/to/cookbook.pdf"
  ```
- Data storage:
  - Uploaded PDFs: `./files/`
  - ChromaDB: `./chroma_data/`
- To change models, set environment variables before starting the backend (no code changes needed).

## Troubleshooting
- **Backend not responding**: Verify `python main.py` shows `Uvicorn running on http://127.0.0.1:8000`.
- **Ollama model errors**: Run `ollama list` to confirm `qwen3:4b` and `nomic-embed-text` are present.
- **CORS issues**: Always serve the UI via a static server as described; do not modify the backend to serve static files.
- **Empty results**: Ensure at least one PDF has been uploaded and processed successfully.

---
*Readme generated based on the current state of the repository (2026-10-18).*