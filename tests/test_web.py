import pytest
from fastapi.testclient import TestClient

from lumifolio import web
from lumifolio.config import Settings
from lumifolio.service import StudyService


class FakeEmbedder:
    def encode(self, texts, *, query=False):
        return [[1.0, 0.0] for _ in texts]


@pytest.fixture
def client(monkeypatch, tmp_path):
    service = StudyService(Settings(data_dir=tmp_path / "index", ollama_url="http://127.0.0.1:1"))
    service.embedder = FakeEmbedder()
    monkeypatch.setattr(web, "service", lambda: service)
    with TestClient(web.app, base_url="http://127.0.0.1") as test_client:
        yield test_client


def test_main_routes_and_content_types(client):
    response = client.get("/")
    assert response.status_code == 200 and "Lumifólio" in response.text
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert client.get("/api/documents").json() == []
    assert client.get("/api/status").json()["ready"] is False
    response = client.post("/api/ask", json={"question": "Pergunta?"})
    assert response.json()["status"] == "empty"
    assert client.post("/api/ask", json={"question": "   "}).status_code == 422


def test_import_validate_delete_and_unavailable_model(client):
    assert client.post("/api/documents", files={"file": ("ruim.pdf", b"corrompido")}).status_code == 400
    response = client.post("/api/documents", files={"file": ("vetor.txt", b"O vetor representa texto.")})
    assert response.status_code == 201
    doc = response.json()
    assert client.get("/api/documents").json() == [doc]
    assert client.post("/api/ask", json={"question": "O que e vetor?"}).status_code == 503
    assert client.delete("/api/documents/" + doc["id"]).status_code == 204
    assert client.delete("/api/documents/" + doc["id"]).status_code == 404


def test_browser_requests_cannot_mutate_across_origins(client):
    assert client.post("/api/examples", headers={"Origin": "https://example.test"}).status_code == 403
    assert client.post("/api/examples", headers={"Sec-Fetch-Site": "cross-site"}).status_code == 403
    assert client.get("/api/documents", headers={"Host": "other.example"}).status_code == 400
    assert client.get("/api/documents").json() == []
