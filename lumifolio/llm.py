import httpx
from pydantic import ValidationError

from .config import Settings
from .errors import StudyError
from .prompts import ModelAnswer


class Ollama:
    def __init__(self, settings: Settings):
        self.settings = settings

    def ready(self) -> bool:
        try:
            response = httpx.get(f"{self.settings.ollama_url}/api/tags", timeout=2, trust_env=False)
            response.raise_for_status()
            return any(
                item["name"] == self.settings.model_name and not item.get("remote_model")
                for item in response.json()["models"]
            )
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            return False

    def generate(self, messages: list[dict[str, str]], structured: bool = True) -> str:
        if self.settings.model_name.endswith((":cloud", "-cloud")):
            raise StudyError("Selecione um modelo Ollama baixado para execução local.", 503)
        body = {
            "model": self.settings.model_name,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0, "seed": 42, "num_ctx": 4096, "num_predict": 512},
            "keep_alive": "10m",
        }
        if structured:
            body["format"] = ModelAnswer.model_json_schema()
        try:
            response = httpx.post(
                f"{self.settings.ollama_url}/api/chat",
                json=body,
                timeout=httpx.Timeout(self.settings.llm_timeout, connect=3),
                trust_env=False,
            )
        except httpx.TimeoutException as exc:
            raise StudyError("O modelo excedeu o tempo limite. Aguarde alguns segundos e tente novamente.", 504) from exc
        except httpx.RequestError as exc:
            raise StudyError("O Ollama está inacessível. Inicie o serviço local e tente novamente.", 503) from exc

        if response.status_code == 404:
            raise StudyError(f"Modelo indisponível. Execute ollama pull {self.settings.model_name}.", 503)
        if response.is_error:
            raise StudyError("O Ollama não conseguiu gerar a resposta. Confira o serviço e o modelo.", 502)
        try:
            payload = response.json()
            if payload.get("done_reason") == "length":
                raise ValueError("Incomplete model output")
            text = payload["message"]["content"]
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Empty model output")
            return text
        except (KeyError, ValueError, TypeError, AttributeError) as exc:
            raise StudyError("O Ollama retornou uma resposta incompleta ou inválida.", 502) from exc

    def structured(self, messages: list[dict[str, str]]) -> ModelAnswer:
        try:
            return ModelAnswer.model_validate_json(self.generate(messages))
        except ValidationError as exc:
            raise StudyError("O modelo retornou um formato inválido. Tente reformular a pergunta.", 502) from exc
