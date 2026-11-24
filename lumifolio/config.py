from pathlib import Path
from typing import Annotated
from urllib.parse import urlsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent
MAX_FILE_BYTES = 12 * 1024 * 1024
MAX_DOCUMENTS = 50
TOP_K = 4
QUESTION_LIMIT = 600
HISTORY_LIMIT = 3


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LUMIFOLIO_", env_file=ROOT / ".env", extra="ignore"
    )

    data_dir: Path = ROOT / ".runtime" / "chroma"
    ollama_url: str = "http://127.0.0.1:11434"
    model_name: Annotated[str, Field(min_length=1, max_length=150)] = "qwen2.5:3b"
    llm_timeout: Annotated[float, Field(gt=0, le=600)] = 120
    min_score: Annotated[float, Field(ge=-1, le=1)] = 0.75

    @field_validator("ollama_url")
    @classmethod
    def require_loopback(cls, value: str) -> str:
        parsed = urlsplit(value)
        if (
            parsed.scheme != "http"
            or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
            or parsed.path not in {"", "/"}
            or parsed.port is None
        ):
            raise ValueError("Use um endereço HTTP local do Ollama com porta explícita.")
        return value.rstrip("/")
