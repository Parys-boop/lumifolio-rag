import math
import os
from pathlib import Path

import pytest

from lumifolio.config import Settings
from lumifolio.service import StudyService

ROOT = Path(__file__).resolve().parent.parent

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(os.getenv("LUMIFOLIO_LIVE_TEST") != "1", reason="Ative LUMIFOLIO_LIVE_TEST=1."),
]


@pytest.fixture(scope="module")
def live(tmp_path_factory):
    engine = StudyService(Settings(data_dir=tmp_path_factory.mktemp("index-real")))
    assert engine.llm.ready(), "Baixe e inicie o modelo Ollama definido na configuração."
    for path in ROOT.joinpath("examples").iterdir():
        if path.suffix in {".pdf", ".txt"}:
            engine.add_document(path.name, path.read_bytes())
    return engine


def test_embeddings_and_vector_retrieval_are_real(live):
    vector, = live.embedder.encode(["sobreposição entre janelas"], query=True)
    assert len(vector) == 384 and math.isclose(sum(x*x for x in vector), 1, abs_tol=1e-5)
    hit, *_ = live.search("Por que o exercício mantém palavras em comum entre trechos consecutivos?")
    assert hit.filename == "pratica-de-rag.pdf" and hit.page == 1


def test_real_llm_gives_grounded_answer(live):
    answer = live.ask("Qual código identifica a entrega do laboratório fictício?")
    assert answer.status == "answered" and "VETOR-17" in answer.answer.upper()
    hit_by_id = {hit.id: hit for hit in answer.hits}
    assert any(source.filename == "guia-do-laboratorio.txt" for source in answer.citations)
    assert all(source.quote in hit_by_id[source.source_id].text for source in answer.citations)


def test_real_llm_refuses_missing_detail_above_threshold(live):
    answer = live.ask("Qual é o prazo de entrega do laboratório fictício?")
    assert answer.submitted_ids, "O caso precisa alcançar o LLM para testar a recusa semântica."
    assert answer.status == "insufficient" and not answer.citations


def test_real_llm_cannot_attach_an_unsupported_quantity(live):
    answer = live.ask("Quantas dimensões têm os vetores usados pelo laboratório fictício?")
    assert answer.submitted_ids
    assert answer.status == "insufficient" and not answer.citations
