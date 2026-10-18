import shutil
import fitz

from fastapi import HTTPException


def save_file_in_local(file, file_path):

    try:
        with file_path.open("wb") as destination:
            shutil.copyfileobj(file.file, destination)

            # Basic PDF signature validation
        with file_path.open("rb") as uploaded_file:
            if not uploaded_file.read(5).startswith(b"%PDF-"):
                file_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=400,
                    detail="The uploaded file is not a valid PDF."
                )
    except Exception as e:
        raise Exception(f"Failed while copying the file {file.filename} to the server.")


def read_file(file_path):
    try:
        with fitz.open(file_path) as fp:
            pages = [page.get_text("text") for page in fp]
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a readable PDF.",
        ) from exc

    # text = "\n".join(pages).strip()

    if not pages:
        raise HTTPException(
            status_code=400,
            detail="No text found. This PDF may require OCR.",
        )
    return pages

