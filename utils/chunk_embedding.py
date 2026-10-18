import ollama

def embedding_chunks(chunks: list[str]):
    # texts = [chunk["text"] for chunk in chunks]
    return ollama.embed(
        model="nomic-embed-text",
        input=chunks,
    )