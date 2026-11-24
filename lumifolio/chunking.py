from dataclasses import dataclass

from .documents import Page

CHUNK_WORDS = 100
OVERLAP_WORDS = 20


@dataclass(frozen=True)
class Chunk:
    page: int | None
    position: int
    text: str


def make_chunks(
    pages: list[Page], size: int = CHUNK_WORDS, overlap: int = OVERLAP_WORDS
) -> list[Chunk]:
    if not 0 <= overlap < size:
        raise ValueError("O overlap deve ser menor que a janela e não negativo.")

    chunks = []
    # Uma janela nunca cruza a página de origem. O overlap conserva frases de fronteira.
    for page in pages:
        words = page.text.split()
        for start in range(0, len(words), size - overlap):
            end = start + size
            chunks.append(Chunk(page.number, len(chunks) + 1, " ".join(words[start:end])))
            if end >= len(words):
                break
    return chunks
