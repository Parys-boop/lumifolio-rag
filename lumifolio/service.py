from hashlib import sha256
from pathlib import Path
from threading import RLock

from .chunking import make_chunks
from .config import HISTORY_LIMIT, MAX_DOCUMENTS, TOP_K, Settings
from .documents import clean_text, document_name, read_document
from .embeddings import Embedder
from .errors import StudyError
from .grounding import quantities
from .llm import Ollama
from .models import Answer, AskRequest, Citation, Document, Hit, Mode
from .prompts import baseline_prompt, prompt
from .retrieval import retrieve
from .vector_store import VectorStore

EMPTY = "Adicione um documento à base para começar a fazer perguntas."
INSUFFICIENT = "Não encontrei nos documentos evidências suficientes para responder a essa pergunta."


class StudyService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.embedder = Embedder()
        self.store = VectorStore(settings.data_dir)
        self.llm = Ollama(settings)
        self.lock = RLock()

    def documents(self) -> list[Document]:
        with self.lock:
            return self.store.documents()

    def add_document(self, filename: str, content: bytes) -> Document:
        name = document_name(filename)
        if not name or len(name) > 180:
            raise StudyError("Use um nome de arquivo com até 180 caracteres.")
        pages = read_document(name, content)
        doc_id = sha256(Path(name).suffix.lower().encode() + content).hexdigest()
        chunks = make_chunks(pages)
        with self.lock:
            current = self.store.documents()
            for document in current:
                if document.id == doc_id:
                    return document
            if len(current) >= MAX_DOCUMENTS:
                raise StudyError("A biblioteca está cheia. Remova um documento antes de continuar.", 409)
            if len(chunks) > 2500:
                raise StudyError("O documento gerou mais de 2.500 trechos. Divida o arquivo.", 413)
            document = Document(
                id=doc_id, filename=name, chunks=len(chunks),
                pages=len(pages) if pages[0].number is not None else None,
            )
            self.store.add(document, chunks, self.embedder.encode([chunk.text for chunk in chunks]))
            return document

    def remove_document(self, document_id: str) -> None:
        with self.lock:
            if not self.store.remove(document_id):
                raise StudyError("Documento não encontrado na biblioteca.", 404)

    def search(self, question: str, limit: int = TOP_K, history: list[str] | None = None) -> list[Hit]:
        with self.lock:
            return retrieve(self.store, self.embedder, question, history or [], limit)

    def ask(self, question: str, history: list[str] | None = None, mode: Mode = "few-shot") -> Answer:
        request = AskRequest(question=question, history=(history or [])[-HISTORY_LIMIT:], mode=mode)
        with self.lock:
            if not self.store.count():
                return Answer(status="empty", answer=EMPTY, model=self.settings.model_name, mode=mode)
            hits = self.search(request.question, history=request.history)
        eligible = [hit for hit in hits if hit.score >= self.settings.min_score]
        result = Answer(
            status="insufficient", answer=INSUFFICIENT, hits=hits,
            submitted_ids=[hit.id for hit in eligible], model=self.settings.model_name, mode=mode,
        )
        if not eligible:
            return result
        messages, sources = prompt(request.question, request.history, eligible, mode)
        output = self.llm.structured(messages)
        if output.status != "answered" or not output.answer.strip() or not output.citations:
            return result
        citations = []
        for citation in output.citations:
            hit = sources.get(citation.source)
            quote = clean_text(citation.quote)
            if hit is None or len(quote) < 12 or quote not in hit.text:
                # Erro de atribuição invalida a resposta inteira, mesmo se houver outra citação.
                return result
            citations.append(Citation(
                source_id=hit.id, filename=hit.filename, page=hit.page,
                position=hit.position, quote=quote,
            ))
        # Uma citação pode existir e ainda omitir o dado afirmado. Para números
        # explícitos, também exija a quantidade em pelo menos um dos excertos.
        if not quantities(output.answer) <= quantities(" ".join(item.quote for item in citations)):
            return result
        return result.model_copy(update={
            "status": "answered", "answer": output.answer.strip(), "citations": citations,
        })

    def baseline(self, question: str) -> str:
        return self.llm.generate(baseline_prompt(question), structured=False)
