from collections import defaultdict
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from .chunking import Chunk
from .models import Document, Hit


class VectorStore:
    def __init__(self, directory: Path):
        client = chromadb.PersistentClient(
            path=str(directory.resolve()), settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = client.get_or_create_collection(
            name="lumifolio-e5-small-v1",
            configuration={"hnsw": {"space": "cosine"}},
            embedding_function=None,
        )

    def documents(self) -> list[Document]:
        grouped = defaultdict(list)
        for metadata in self.collection.get(include=["metadatas"])["metadatas"]:
            grouped[metadata["document_id"]].append(metadata)
        documents = [
            Document(
                id=key,
                filename=rows[0]["filename"],
                chunks=len(rows),
                pages=rows[0]["pages"] or None,
            )
            for key, rows in grouped.items()
        ]
        return sorted(documents, key=lambda document: document.filename.casefold())

    def add(self, document: Document, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        # Um documento é gravado em um único lote. O hash impede duplicação no reenvio.
        self.collection.add(
            ids=[f"{document.id}:{chunk.position}" for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=vectors,
            metadatas=[
                {
                    "document_id": document.id,
                    "filename": document.filename,
                    "page": chunk.page or 0,
                    "pages": document.pages or 0,
                    "position": chunk.position,
                }
                for chunk in chunks
            ],
        )

    def remove(self, document_id: str) -> bool:
        where = {"document_id": document_id}
        if not self.collection.get(limit=1, where=where, include=[])["ids"]:
            return False
        self.collection.delete(where=where)
        return True

    def search(self, vector: list[float], limit: int) -> list[Hit]:
        limit = min(limit, self.collection.count())
        if limit <= 0:
            return []
        result = self.collection.query(
            query_embeddings=[vector],
            n_results=limit,
            include=["metadatas", "documents", "distances"],
        )
        # Para a métrica cosseno do Chroma, distância = 1 - similaridade.
        return [
            Hit(
                id=key,
                filename=metadata["filename"],
                page=metadata["page"] or None,
                position=metadata["position"],
                text=text,
                score=max(-1.0, min(1.0, 1 - distance)),
            )
            for key, metadata, text, distance in zip(
                result["ids"][0], result["metadatas"][0],
                result["documents"][0], result["distances"][0], strict=True
            )
        ]

    def count(self) -> int:
        return self.collection.count()
