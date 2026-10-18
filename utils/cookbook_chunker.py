from langchain_text_splitters import RecursiveCharacterTextSplitter


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1800, # measured as characters
    chunk_overlap=200,
    separators=["\n\n", "\n", "", " ", ". "],
    add_start_index=True
)

def chunk_recipe(text:list[str]):
    documents = text_splitter.create_documents(text)

    return [
        doc.page_content
        for doc in documents
    ]