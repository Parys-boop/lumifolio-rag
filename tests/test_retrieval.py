from types import SimpleNamespace

from lumifolio.retrieval import retrieve


def test_history_helps_short_followups_and_preserves_explicit_questions():
    encoded = []

    def encode(texts, *, query):
        assert query
        encoded.extend(texts)
        return [[1.0]]

    store = SimpleNamespace(count=lambda: 1, search=lambda vector, limit: [])
    embedder = SimpleNamespace(encode=encode)
    history = ["O que é chunking?"]
    retrieve(store, embedder, "Por quê?", history, 4)
    retrieve(store, embedder, "Por que o céu é azul?", history, 4)
    assert encoded == ["O que é chunking? Por quê?", "Por que o céu é azul?"]
