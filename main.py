import os
import logging
import uvicorn

from pathlib import Path
from fastapi import FastAPI, HTTPException, File, UploadFile, Request
from pydantic import BaseModel, Field
from fastapi.templating import Jinja2Templates

from utils.save_file import save_file_in_local, read_file
from utils.cookbook_chunker import chunk_recipe
from utils.chunk_embedding import embedding_chunks
from utils.vector_db import ChromaDB
from utils.llm_model import call_llm

logger = logging.getLogger(__name__)

db_obj = ChromaDB()

app = FastAPI(title="Cookbook Application")

# Configure templates
templates = Jinja2Templates(directory="templates")


class DeleteDocument(BaseModel):
    document_name: str = Field(min_length=10, max_length=200)

class Search(BaseModel):
    query: str = Field(min_length=10, max_length=5000)
    top_k: int = Field(default=3)


FILE_DIRECTORY = Path(f"./files")
if not Path.exists(FILE_DIRECTORY):
    os.makedirs(FILE_DIRECTORY)

@app.post("/add-document")
def add_document(file: UploadFile = File(...)):

    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file."
        )
    file_path = FILE_DIRECTORY / file.filename
    try:
        save_file_in_local(file, file_path)
        pages = read_file(file_path)
        chunks = chunk_recipe(pages)
        embeddings = embedding_chunks(chunks)
        result = db_obj.upsert_to_db(chunks, embeddings)
        return {
            "message": result,
            "filename": file.filename
        }
    except Exception:
        logger.exception("PDF upload failed")
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to upload PDF."
        )
    finally:
        file.file.close()


@app.post("/search")
async def search(request: Search):
    query = request.query
    embeddings = embedding_chunks([query])
    results = db_obj.search_cookbook(embeddings.embeddings)
    response = await call_llm(results, query)
    return response

@app.delete("/delete-document")
def delete_file(request: DeleteDocument):
    filename = request.document_name
    file = FILE_DIRECTORY / filename
    try:
        if Path.exists(file):
            os.remove(file)
        else:
            logger.error(f"The file {request.document_name} is not found in the server")
            return {"message": "File doesn't exists in server.", "filename": filename}
        return {"message": "File is deleted successfully.", "filename": filename}
    except Exception as e:
        logger.exception(f"Delete operation failed with exception {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete PDF {filename}."
        )


@app.get("/")
async def read_root(request: Request):
    """Serve the main UI page"""
    return templates.TemplateResponse(request,"index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


