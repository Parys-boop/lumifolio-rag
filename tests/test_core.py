from pathlib import Path
from types import SimpleNamespace

import pymupdf
import pytest

from lumifolio.chunking import make_chunks
from lumifolio.config import Settings
from lumifolio.documents import Page, document_name, read_document
from lumifolio.errors import StudyError
from lumifolio.models import Hit
from lumifolio.prompts import ModelAnswer, prompt
from lumifolio.service import StudyService
from lumifolio.vector_store import VectorStore

BASE = Path(__file__).resolve().parent.parent


class FakeEmbedder:
    def encode(self, texts, *, query=False):
        return [[1.0, 0.0] if "vetor" in text.lower() else [0.0, 1.0] for text in texts]


@pytest.fixture
def engine(tmp_path):
    instance = StudyService(Settings(data_dir=tmp_path / "index", ollama_url="http://127.0.0.1:1"))
    instance.embedder = FakeEmbedder()
    return instance


def test_txt_utf8_with_bom():
    assert read_document("texto.TXT", "\ufeffOlá\n  Ciência".encode()) == [Page(None, "Olá Ciência")]
    assert document_name("C:\\Pasta\\a.txt") == "a.txt"


def test_pdf_page_number_survives_blank_page():
    with pymupdf.open() as doc:
        doc.new_page()
        doc.new_page().insert_text((60, 60), "Texto selecionavel da segunda pagina")
        content = doc.tobytes()
    assert read_document("teste.pdf", content) == [Page(2, "Texto selecionavel da segunda pagina")]


@pytest.mark.parametrize(("name", "sample", "message"), [
    ("exemplo.docx", b"a", "PDF ou TXT"),
    ("vazio.txt", b"", "vazio"),
    ("invalido.pdf", b"%PDF-1.7\nINVALID", "ler o PDF"),
    ("binario.txt", b"\x00abc", "texto simples"),
    ("latin.txt", b"\xe9", "UTF-8"),
    ("espaco.txt", b" \r\n\t ", "Nenhum texto"),
])
def test_invalid_documents(name, sample, message):
    with pytest.raises(StudyError, match=message):
        read_document(name, sample)


def test_chunk_overlap_and_page_boundaries():
    chunks = make_chunks([Page(1, "a b c d e f g h"), Page(2, "i j")], size=4, overlap=2)
    assert [(c.page, c.position, c.text) for c in chunks] == [
        (1, 1, "a b c d"), (1, 2, "c d e f"), (1, 3, "e f g h"), (2, 4, "i j")
    ]
    with pytest.raises(ValueError):
        make_chunks([], size=4, overlap=4)


def test_documents_persist_and_removal_removes_vectors(engine):
    one = engine.add_document("vetor.txt", b"O vetor semantico representa texto.")
    two = engine.add_document("tema.txt", b"Outra materia.")
    assert engine.add_document("copia.txt", b"O vetor semantico representa texto.") == one
    reopened = VectorStore(engine.settings.data_dir)
    assert {doc.id for doc in reopened.documents()} == {one.id, two.id}
    hits = engine.search("O que o vetor representa?")
    assert [(h.filename, h.score) for h in hits] == [("vetor.txt", 1), ("tema.txt", 0)]
    engine.remove_document(one.id)
    assert reopened.count() == 1
    with pytest.raises(StudyError, match="não encontrado"):
        engine.remove_document(one.id)


def test_prompt_techniques_and_payload():
    hit = Hit(id="doc:1", filename="a.txt", page=None, position=1, text="evidência local", score=.9)
    zero, sources = prompt("Questão?", ["Assunto anterior"], [hit], "zero-shot")
    few, _ = prompt("Questão?", ["Assunto anterior"], [hit], "few-shot")
    assert [m["role"] for m in zero] == ["system", "user"]
    assert [m["role"] for m in few] == ["system", "user", "assistant", "user", "assistant", "user"]
    assert few[-1] == zero[-1]
    assert sources == {"F1": hit}
    for text in ("Questão?", "Assunto anterior", "evidência local"):
        assert text in few[-1]["content"]


def test_returns_empty_and_low_similarity_without_model(engine):
    assert engine.ask("A biblioteca está vazia?").status == "empty"
    engine.add_document("tema.txt", b"Uma materia de estudo.")
    answer = engine.ask("O que e vetor?")
    assert answer.status == "insufficient" and answer.hits and not answer.submitted_ids


@pytest.mark.parametrize(("quote", "label", "status"), [
    ("O vetor representa palavras.", "F1", "answered"),
    ("Essa citação foi inventada.", "F1", "insufficient"),
    ("O vetor representa palavras.", "F2", "insufficient"),
])
def test_citations_are_checked_against_retrieved_text(engine, quote, label, status):
    engine.add_document("vetor.txt", b"O vetor representa palavras.")
    output = ModelAnswer.model_validate({
        "status": "answered", "answer": "Palavras.", "citations": [{"source": label, "quote": quote}]
    })
    engine.llm = SimpleNamespace(structured=lambda messages: output)
    answer = engine.ask("O que o vetor representa?")
    assert answer.status == status
    if status == "answered":
        citation, = answer.citations
        assert citation.filename == "vetor.txt"
        assert citation.source_id == answer.submitted_ids[0]
    else:
        assert answer.citations == []


def test_connection_failure_has_safe_message(engine):
    engine.add_document("vetor.txt", b"O vetor representa palavras.")
    with pytest.raises(StudyError, match="Ollama está inacessível") as error:
        engine.ask("O que o vetor representa?")
    assert error.value.status_code == 503


def test_settings_prevent_remote_model_endpoint():
    with pytest.raises(ValueError, match="endereço HTTP local"):
        Settings(ollama_url="https://example.com:443")


@pytest.mark.parametrize(("answer", "expected"), [
    ("O texto descreve 2 dimensões.", "answered"),
    ("O texto descreve vinte dimensões e 15 graus.", "insufficient"),
])
def test_numeric_claim_must_be_present_in_citations(engine, answer, expected):
    quote = "O vetor possui duas dimensões."
    engine.add_document("vetor.txt", quote.encode())
    model = ModelAnswer(
        status="answered", answer=answer, citations=[{"source": "F1", "quote": quote}],
    )
    engine.llm = SimpleNamespace(structured=lambda messages: model)
    assert engine.ask("O que diz o texto sobre o vetor?").status == expected
