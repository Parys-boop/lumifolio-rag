from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

from .config import HISTORY_LIMIT, QUESTION_LIMIT

Mode = Literal["few-shot", "zero-shot"]
Question = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=QUESTION_LIMIT)]


class Document(BaseModel):
    id: str
    filename: str
    chunks: int
    pages: int | None


class Hit(BaseModel):
    id: str
    filename: str
    page: int | None
    position: int
    text: str
    score: float


class Citation(BaseModel):
    source_id: str
    filename: str
    page: int | None
    position: int
    quote: str


class Answer(BaseModel):
    status: Literal["answered", "insufficient", "empty"]
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    hits: list[Hit] = Field(default_factory=list)
    submitted_ids: list[str] = Field(default_factory=list)
    model: str
    mode: Mode


class AskRequest(BaseModel):
    question: Question
    history: list[Question] = Field(default_factory=list, max_length=HISTORY_LIMIT)
    mode: Mode = "few-shot"
