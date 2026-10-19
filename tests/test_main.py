from http.client import responses

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from main import app

client = TestClient(app)


@patch("main.call_llm")
@patch("main.ChromaDB.search_cookbook")
@patch("main.embedding_chunks")
def test_search_api(mock_embedding_chunks, mock_search_cookbook, mock_call_llm):
    # Mock embedding_chunks to return an object with .embeddings attribute
    mock_embedding = Mock()
    mock_embedding.embeddings = [0.1, 0.2, 0.3]  # dummy embedding
    mock_embedding_chunks.return_value = mock_embedding

    # Mock search_cookbook to return a list of retrieved document strings
    mock_search_cookbook.return_value = ["Retrieved chunk about idli recipe"]

    # Mock call_llm to return a recipe string (as the endpoint returns the content string)
    mock_call_llm.return_value = (
        "Idli\n"
        "Cuisine: Indian\n"
        "Preparation time: 2 hours\n"
        "Ingredients: rice, urad dal, water, salt\n"
        "Instructions: Soak rice and dal... Steam..."
    )

    response = client.post(
        "/search",
        json={"query": "How is idli made", "top_k": 3},
    )

    # Print for debugging (optional)
    # print(f"Status: {response.status_code}")
    # print(f"Text: {response.text}")

    assert response.status_code == 200
    # The endpoint returns the plain string from call_llm
    assert response.json() == mock_call_llm.return_value


@patch("main.ChromaDB.upsert_to_db")
@patch("main.embedding_chunks")
@patch("main.chunk_recipe")
@patch("main.read_file")
def test_upload_api(mock_read_file, mock_chunk_recipe, mock_embedding_chunks, mock_chroma_upsert):
    mock_read = Mock()
    mock_read.return_value = ["page1", "page2"]  # read_file returns pages
    mock_chunk_recipe.return_value = ["chunk1", "chunk2"]  # chunk_recipe returns chunks
    mock_embedding_chunks.return_value = Mock()
    mock_embedding_chunks.return_value.embeddings = [1.0, 2.4]  # embedding_chunks returns object with embeddings
    mock_chroma_upsert.return_value = "Total of 2 chunks have been added to DB"

    # Create a dummy PDF file content for testing
    dummy_pdf_content = b"%PDF-1.4\n%Dummy PDF content for testing\n%%EOF"

    response = client.post(
        "/add-documents",
        files={"file": ("test-recipe.pdf", dummy_pdf_content, "application/pdf")}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Total of 2 chunks have been added to DB", "filename": "test-recipe.pdf"}