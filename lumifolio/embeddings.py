from threading import Lock

from .errors import StudyError

EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
EMBEDDING_REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"


class Embedder:
    def __init__(self):
        self.model = None
        self.lock = Lock()

    def encode(self, texts: list[str], *, query: bool = False) -> list[list[float]]:
        prefix = "query: " if query else "passage: "
        with self.lock:
            try:
                if self.model is None:
                    import torch
                    from sentence_transformers import SentenceTransformer

                    torch.set_num_threads(4)
                    self.model = SentenceTransformer(
                        EMBEDDING_MODEL,
                        revision=EMBEDDING_REVISION,
                        device="cpu",
                        trust_remote_code=False,
                        model_kwargs={"use_safetensors": True},
                    )
                # O E5 usa prefixos assimétricos e vetores normalizados para recuperação.
                return self.model.encode(
                    [prefix + text for text in texts],
                    batch_size=24,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                ).tolist()
            except (ImportError, OSError, RuntimeError, ValueError) as exc:
                raise StudyError(
                    "O modelo de embeddings não iniciou. Confira a instalação e o download inicial.",
                    503,
                ) from exc


if __name__ == "__main__":
    vector, = Embedder().encode(["verificação dos embeddings"], query=True)
    print(f"Modelo pronto com {len(vector)} dimensões.")
