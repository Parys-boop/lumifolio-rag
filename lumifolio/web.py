from functools import lru_cache
from threading import Lock

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .config import MAX_FILE_BYTES, ROOT, Settings
from .errors import StudyError
from .models import Answer, AskRequest, Document
from .service import StudyService

app = FastAPI(title="Lumifólio", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
app.mount("/static", StaticFiles(directory=ROOT / "web"), name="static")

EXAMPLE_FILES = (
    "pln-e-embeddings.pdf", "pratica-de-rag.pdf",
    "guia-do-laboratorio.txt", "cuidados-com-fontes.txt",
)


service_lock = Lock()


@lru_cache
def build_service() -> StudyService:
    return StudyService(Settings())


def service() -> StudyService:
    with service_lock:
        return build_service()


@app.middleware("http")
async def local_requests(request: Request, call_next):
    if request.method not in {"GET", "HEAD"}:
        origin = request.headers.get("origin")
        if request.headers.get("sec-fetch-site") == "cross-site" or (
            origin and origin != f"{request.url.scheme}://{request.headers.get('host')}"
        ):
            return JSONResponse({"detail": "Operação disponível na origem local do aplicativo."}, 403)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    )
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(StudyError)
async def expected_error(request: Request, error: StudyError):
    return JSONResponse({"detail": str(error)}, error.status_code)


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, error: RequestValidationError):
    return JSONResponse({"detail": "Envie uma pergunta entre 1 e 600 caracteres ou um arquivo válido."}, 422)


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(ROOT / "web" / "index.html")


@app.get("/api/status")
def status():
    engine = service()
    return {"ready": engine.llm.ready(), "model": engine.settings.model_name}


@app.get("/api/documents")
def documents() -> list[Document]:
    return service().documents()


@app.post("/api/documents", status_code=201)
def upload(file: UploadFile = File(...)) -> Document:
    try:
        content = file.file.read(MAX_FILE_BYTES + 1)
        return service().add_document(file.filename or "", content)
    finally:
        file.file.close()


@app.post("/api/examples", status_code=201)
def examples() -> list[Document]:
    return [
        service().add_document(name, (ROOT / "examples" / name).read_bytes())
        for name in EXAMPLE_FILES
    ]


@app.delete("/api/documents/{document_id}", status_code=204)
def delete_document(document_id: str):
    service().remove_document(document_id)
    return Response(status_code=204)


@app.post("/api/ask")
def ask(question: AskRequest) -> Answer:
    return service().ask(question.question, question.history, question.mode)
