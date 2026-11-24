"""Fluxo real no Microsoft Edge. Use --evidence para registrar o plano B."""

import argparse
from contextlib import contextmanager
import os
from pathlib import Path
import socket
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic, sleep

import httpx
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parent.parent
CODE = "Qual código identifica a entrega do laboratório fictício?"
OVERLAP = "Por que o exercício mantém palavras em comum entre trechos consecutivos?"
MISSING = "Qual é o prazo de entrega do laboratório fictício?"


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextmanager
def app_server(index: Path, *, unavailable=False):
    port = free_port()
    env = os.environ.copy()
    env.update(LUMIFOLIO_DATA_DIR=str(index), HF_HUB_OFFLINE="1", PYTHONUTF8="1")
    if unavailable:
        env["LUMIFOLIO_OLLAMA_URL"] = "http://127.0.0.1:1"
    with index.with_suffix(".log").open("wb") as log_file:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "lumifolio.web:app", "--host", "127.0.0.1",
             "--port", str(port)],
            cwd=ROOT, env=env, stdout=log_file, stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        url = f"http://127.0.0.1:{port}"
        try:
            deadline = monotonic() + 25
            while monotonic() < deadline and process.poll() is None:
                try:
                    if httpx.get(url, timeout=1, trust_env=False).is_success:
                        break
                except httpx.RequestError:
                    pass
                sleep(.25)
            else:
                raise RuntimeError(index.with_suffix(".log").read_text(encoding="utf-8"))
            yield url
        finally:
            process.terminate()
            process.wait(timeout=10)


def capture(page, directory, name):
    if directory:
        page.screenshot(path=directory / name, full_page=True, animations="disabled")


def submit(page, question):
    page.get_by_role("textbox", name="Sua pergunta", exact=True).fill(question)
    page.get_by_role("button", name="Enviar").click()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    directory = args.evidence.resolve() if args.evidence else None
    if directory:
        directory.mkdir(parents=True, exist_ok=True)
    runtime = ROOT / ".runtime"
    runtime.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=runtime, prefix="browser-", ignore_cleanup_errors=True) as temp, sync_playwright() as playwright:
        scratch = Path(temp)
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        viewport = {"width": 1440, "height": 900}
        with app_server(scratch / "index") as url:
            options = {"viewport": viewport, "locale": "pt-BR"}
            if directory:
                options.update(record_video_dir=scratch / "recording", record_video_size=viewport)
            context = browser.new_context(**options)
            page = context.new_page()
            web_errors = []
            external_requests = []
            page.on("request", lambda request: external_requests.append(request.url)
                    if not request.url.startswith(url + "/") else None)
            page.on("pageerror", lambda error: web_errors.append(str(error)))
            page.goto(url, wait_until="networkidle")
            expect(page.get_by_text("Modelo local pronto")).to_be_visible()
            expect(page.get_by_text("Sua biblioteca está vazia.")).to_be_visible()
            expect(page.get_by_role("button", name="Enviar")).to_be_disabled()
            capture(page, directory, "01-biblioteca-vazia.png")

            page.locator("#files").set_input_files({
                "name": "arquivo-invalido.pdf", "mimeType": "application/pdf",
                "buffer": b"%PDF-1.7 broken example",
            })
            expect(page.locator("#notice")).to_contain_text("Não foi possível ler o PDF")
            capture(page, directory, "02-arquivo-invalido.png")

            page.locator("#files").set_input_files([
                ROOT / "examples" / "pratica-de-rag.pdf",
                ROOT / "examples" / "guia-do-laboratorio.txt",
            ])
            expect(page.locator("#document-count")).to_have_text("2", timeout=90_000)
            page.get_by_role("button", name="Carregar materiais de exemplo").click()
            expect(page.locator("#document-count")).to_have_text("4", timeout=90_000)
            expect(page.locator("#notice")).to_have_text("Materiais de exemplo disponíveis na biblioteca.")
            capture(page, directory, "03-biblioteca-indexada.png")

            page.get_by_role("button", name=f"Identificar uma informação {CODE}").click()
            expect(page.get_by_role("textbox", name="Sua pergunta", exact=True)).to_have_value(CODE)
            page.get_by_role("button", name="Enviar").click()
            expect(page.locator("#processing")).to_be_visible()
            expect(page.locator(".answer-text").last).to_contain_text("VETOR-17", timeout=130_000)
            expect(page.locator(".source").last).to_contain_text("guia-do-laboratorio.txt")
            capture(page, directory, "04-resposta-fundamentada.png")

            submit(page, OVERLAP)
            expect(page.locator(".turn")).to_have_count(2, timeout=130_000)
            pdf_turn = page.locator(".turn").last
            expect(pdf_turn.locator(".source").first).to_contain_text("pratica-de-rag.pdf · p. 1")
            details = pdf_turn.get_by_text("Ver trechos da busca", exact=False)
            details.click()
            expect(pdf_turn.get_by_text("Enviado ao modelo", exact=False).first).to_be_visible()
            if directory:
                pdf_turn.screenshot(path=directory / "05-trechos-e-pagina.png", animations="disabled")
                page.wait_for_timeout(2200)
            details.click()

            submit(page, MISSING)
            expect(page.locator(".turn")).to_have_count(3, timeout=130_000)
            refusal = page.locator(".turn").last
            expect(refusal.locator(".answer-text")).to_have_text(
                "Não encontrei nos documentos evidências suficientes para responder a essa pergunta."
            )
            expect(refusal.locator(".source")).to_have_count(0)
            if directory:
                refusal.screenshot(path=directory / "06-pergunta-sem-evidencia.png", animations="disabled")
                page.wait_for_timeout(2200)
            page.reload(wait_until="networkidle")
            expect(page.locator(".turn")).to_have_count(3)
            assert not web_errors, web_errors
            assert not external_requests, external_requests
            video = page.video
            if video:
                page.wait_for_timeout(1600)
            context.close()
            if video:
                video.save_as(directory / "demonstracao-real.webm")

            mobile = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
            mobile.goto(url, wait_until="networkidle")
            expect(mobile.get_by_role("button", name="Documentos", exact=True)).to_be_visible()
            assert mobile.evaluate("document.documentElement.scrollWidth === window.innerWidth")
            capture(mobile, directory, "07-interface-movel.png")
            mobile.get_by_role("button", name="Documentos", exact=True).click()
            expect(mobile.get_by_role("heading", name="Biblioteca")).to_be_visible()
            mobile.get_by_role("button", name="Remover cuidados-com-fontes.txt").click()
            expect(mobile.locator("#document-count")).to_have_text("3")
            mobile.close()
            print("Edge: fluxo completo, histórico, fontes, recusa, remoção e layout móvel.")

        with app_server(scratch / "index", unavailable=True) as url:
            page = browser.new_page(viewport=viewport)
            page.goto(url, wait_until="networkidle")
            expect(page.get_by_text("Modelo indisponível")).to_be_visible()
            submit(page, CODE)
            expect(page.locator("#notice")).to_contain_text("Ollama está inacessível", timeout=90_000)
            expect(page.get_by_role("textbox", name="Sua pergunta", exact=True)).to_have_value(CODE)
            capture(page, directory, "08-modelo-indisponivel.png")
            browser.close()
            print("Edge: falha de conexão exibida e pergunta preservada.")


if __name__ == "__main__":
    main()
