from dataclasses import dataclass
from pathlib import PurePosixPath
import re
import unicodedata

import pymupdf

from .config import MAX_FILE_BYTES
from .errors import StudyError

MAX_PAGES = 300
MAX_TEXT = 500_000


@dataclass(frozen=True)
class Page:
    number: int | None
    text: str


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text).replace("\u00ad", "")
    return " ".join(text.split())


def document_name(filename: str) -> str:
    name = PurePosixPath(filename.replace("\\", "/")).name
    return "".join(char for char in name if not unicodedata.category(char).startswith("C")).strip()


def read_document(filename: str, content: bytes) -> list[Page]:
    suffix = PurePosixPath(filename).suffix.lower()
    if suffix not in {".pdf", ".txt"}:
        raise StudyError("Use um arquivo PDF ou TXT.")
    if not content:
        raise StudyError("O arquivo está vazio.")
    if len(content) > MAX_FILE_BYTES:
        raise StudyError("O arquivo excede 12 MB.", 413)

    if suffix == ".txt":
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise StudyError("Salve o TXT com codificação UTF-8 e importe novamente.") from exc
        if re.search(r"[\x00-\x08\x0e-\x1f]", text) or text.startswith("%PDF-"):
            raise StudyError("O arquivo não contém texto simples válido.")
        pages = [Page(None, clean_text(text))]
    else:
        pages = []
        size = 0
        try:
            if not content.startswith(b"%PDF-"):
                raise StudyError("O arquivo não tem um cabeçalho PDF válido.")
            with pymupdf.open(stream=content, filetype="pdf") as pdf:
                if pdf.needs_pass:
                    raise StudyError("Remova a proteção por senha antes de importar o PDF.")
                if len(pdf) > MAX_PAGES:
                    raise StudyError("Importe PDFs de até 300 páginas.", 413)
                for page in pdf:
                    text = clean_text(page.get_text(sort=True))
                    size += len(text)
                    if size > MAX_TEXT:
                        raise StudyError("O texto excede o limite de 500 mil caracteres.", 413)
                    if text:
                        pages.append(Page(page.number + 1, text))
        except (RuntimeError, ValueError) as exc:
            raise StudyError("Não foi possível ler o PDF. Verifique se o arquivo está íntegro.") from exc

    if not any(page.text for page in pages):
        raise StudyError("Nenhum texto selecionável foi encontrado. PDFs digitalizados precisam de OCR.")
    if sum(len(page.text) for page in pages) > MAX_TEXT:
        raise StudyError("O texto excede o limite de 500 mil caracteres.", 413)
    return pages
