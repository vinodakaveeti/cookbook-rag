import ollama

from constants import EMBEDDING_MODEL

def embedding_chunks(chunks: list[str]):
    return ollama.embed(
        model=EMBEDDING_MODEL,
        input=chunks,
    )