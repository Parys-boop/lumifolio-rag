import re

from .embeddings import Embedder
from .models import Hit
from .vector_store import VectorStore

FOLLOW_UP = re.compile(
    r"^(e\b|como assim\b|explique melhor\b|pode explicar\b)"
    r"|\b(isso|esse|essa|nesse|nessa|ele|ela)\b"
    r"|^por qu[eê]\s*[?!]*$",
    re.IGNORECASE,
)


def retrieve(
    store: VectorStore, embedder: Embedder, question: str, history: list[str], limit: int
) -> list[Hit]:
    if not store.count():
        return []
    query = question
    if history and len(question.split()) <= 12 and FOLLOW_UP.search(question):
        # Acrescenta a pergunta anterior para recuperar o assunto de uma referência curta.
        query = f"{history[-1]} {question}"
    vector, = embedder.encode([query], query=True)
    return store.search(vector, limit)
