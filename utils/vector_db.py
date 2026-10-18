import chromadb
import logging

logger = logging.getLogger(__name__)

class ChromaDB:
    _clinet = None

    def __new__(cls, *args, **kwargs):
        if cls._clinet is None:
            cls._clinet = super().__new__(cls)
        return cls._clinet

    def __init__(self):
        self._client = chromadb.PersistentClient(
            path="./chroma_data"
        )
        self.collection = self._client.get_or_create_collection(
            name="cookbook_chunks", metadata={"hnsw:space": "cosine"},
        )

    def upsert_to_db(self, chunks, embeddings):

        try:
            self.collection.upsert(
                ids=[
                    f"cookbook_demo_001_chunk_{i}"
                    for i in range(len(chunks))
                ],
                documents=chunks,
                embeddings=embeddings.embeddings
            )
            return f"Total chunks {len(chunks)} are stored to vector db"
        except Exception as e:
            raise Exception(f"Failed while adding the chunks to the vector DB")

    @staticmethod
    def search_cookbook(embeddings, top_k: int = 3):
        db = ChromaDB()

        # 2. Retrieve the most similar chunks from Chroma
        results = db.collection.query(
            query_embeddings=embeddings,
            n_results=top_k,
            include=["documents", "distances"],
        )

        # 3. Display the retrieved results
        documents = results["documents"][0]
        distances = results["distances"][0]

        for index, (document, distance) in enumerate(
                zip(documents, distances),
                start=1,
        ):
            logger.info(f"\n--- Result {index} ---")
            logger.info("Distance:", distance)
            logger.info("Retrieved text:\n", document)

        return documents
