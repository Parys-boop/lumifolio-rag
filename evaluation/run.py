"""Avaliação do Lumifólio com corpus de demonstração e perguntas anotadas."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import platform
import re
from statistics import mean, median
from tempfile import TemporaryDirectory
from time import perf_counter
import unicodedata

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "examples"
CASES = Path(__file__).with_name("cases.json")
KS = (1, 2, 4)
MODE = "few-shot"


def normalize(value):
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    unaccented = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(unaccented.split())


def source_key(source):
    return source["filename"], source["page"]


def matches(hit, evidence):
    return (
        source_key(hit) == source_key(evidence)
        and normalize(evidence["anchor"]) in normalize(hit["text"])
    )


def retrieval_metrics(hits, gold):
    gold_files = {item["filename"] for item in gold}
    gold_sources = {source_key(item) for item in gold}
    values = {}
    for k in KS:
        first_k = hits[:k]
        relevance = [any(matches(hit, item) for item in gold) for hit in first_k]
        covered = [any(matches(hit, item) for hit in first_k) for item in gold]
        retrieved_files = {hit["filename"] for hit in first_k}
        retrieved_sources = {source_key(hit) for hit in first_k}
        values[f"precision_at_{k}"] = sum(relevance) / k
        values[f"evidence_recall_at_{k}"] = sum(covered) / len(gold)
        values[f"document_hit_at_{k}"] = bool(gold_files & retrieved_files)
        values[f"source_recall_at_{k}"] = len(gold_sources & retrieved_sources) / len(gold_sources)
    return values


def mention(text, option):
    term = normalize(option)
    if term.isdecimal():
        return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text) is not None
    return term in text


def grade_text(answer, concepts):
    normalized = normalize(answer)
    checks = {
        concept["label"]: any(mention(normalized, option) for option in concept["any_of"])
        for concept in concepts
    }
    return {"concepts": checks, "all_concepts_matched": all(checks.values())}


def grade_citations(answer, gold):
    sources = {source_key(item) for item in gold}
    citations = answer["citations"]
    return {
        "has_expected_source": any(source_key(item) in sources for item in citations),
        "all_citations_expected": bool(citations)
        and all(source_key(item) in sources for item in citations),
        "quotes_covering_gold_anchor": sum(
            any(matches({**citation, "text": citation["quote"]}, item) for item in gold)
            for citation in citations
        ),
    }


def elapsed_ms(start):
    return round((perf_counter() - start) * 1000, 2)


def generate(call):
    start = perf_counter()
    try:
        answer = call()
    except Exception as error:
        # Preserva as demais medições e publica apenas o tipo da falha, sem detalhes locais.
        return {"elapsed_ms": elapsed_ms(start), "error": type(error).__name__}
    return {"elapsed_ms": elapsed_ms(start), "output": answer}


def evaluate_case(service, case, retrieval_only, rag_first):
    question = case["question"]
    gold = case["gold_evidence"]
    start = perf_counter()
    hits = service.search(question, limit=max(KS))
    search_ms = elapsed_ms(start)
    retrieval = [hit.model_dump(mode="json") for hit in hits]
    result = {
        **case,
        "search_ms": search_ms,
        "best_candidate_similarity": hits[0].score if hits else None,
        "retrieved": retrieval,
    }
    if gold:
        result["retrieval_metrics"] = retrieval_metrics(retrieval, gold)
    if retrieval_only:
        return result

    calls = {
        "rag": lambda: service.ask(question, history=[], mode=MODE).model_dump(mode="json"),
        "baseline": lambda: service.baseline(question),
    }
    order = ["rag", "baseline"] if rag_first else ["baseline", "rag"]
    result["generation_order"] = order
    for method in order:
        run = generate(calls[method])
        result[method] = run
        if "output" not in run:
            continue
        output = run["output"]
        if gold:
            answer = output["answer"] if method == "rag" else output
            run["quality"] = grade_text(answer, case["required_concepts"])
            if method == "rag":
                run["quality"].update(grade_citations(output, gold))
        elif method == "rag":
            run["refused_without_citations"] = output["status"] == "insufficient" and not output["citations"]
    return result


def summarize(rows, retrieval_only):
    answerable = [row for row in rows if row["category"] == "answerable"]
    unanswerable = [row for row in rows if row["category"] != "answerable"]
    keys = answerable[0]["retrieval_metrics"] if answerable else []
    summary = {
        "cases": len(rows),
        "answerable": len(answerable),
        "unanswerable": len(unanswerable),
        "retrieval_mean": {
            key: round(mean(row["retrieval_metrics"][key] for row in answerable), 6)
            for key in keys
        },
        "retrieval_latency_ms": {
            "mean": round(mean(row["search_ms"] for row in rows), 2),
            "median": round(median(row["search_ms"] for row in rows), 2),
        },
    }
    if retrieval_only:
        return summary

    for method in ("rag", "baseline"):
        succeeded = [row[method] for row in rows if "output" in row[method]]
        quality = [run["quality"] for run in succeeded if "quality" in run]
        ms = [run["elapsed_ms"] for run in succeeded]
        summary[method] = {
            "successful_calls": len(succeeded),
            "failed_calls": len(rows) - len(succeeded),
            "qualified_answerable_cases": len(quality),
            "matches_all_concepts": sum(item["all_concepts_matched"] for item in quality),
            "latency_ms": {"mean": round(mean(ms), 2), "median": round(median(ms), 2)} if ms else None,
        }
    summary["rag"].update({
        "cited_expected_source": sum(
            row["rag"].get("quality", {}).get("has_expected_source", False) for row in answerable
        ),
        "answered_with_all_concepts_and_expected_source": sum(
            row["rag"].get("output", {}).get("status") == "answered"
            and row["rag"]["quality"]["all_concepts_matched"]
            and row["rag"]["quality"]["has_expected_source"]
            for row in answerable
        ),
        "correct_refusals": sum(row["rag"].get("refused_without_citations", False) for row in unanswerable),
        "correct_refusals_by_category": {
            category: {
                "correct": sum(
                    row["rag"].get("refused_without_citations", False)
                    for row in unanswerable if row["category"] == category
                ),
                "total": sum(row["category"] == category for row in unanswerable),
            }
            for category in ("near_unanswerable", "far_unanswerable")
        },
    })
    return summary


def verify_annotations(cases, corpus):
    """Confirma que cada âncora anotada existe na página e no documento declarados."""
    import pymupdf

    pages = {}
    for path in corpus:
        if path.suffix == ".txt":
            pages[(path.name, None)] = path.read_text(encoding="utf-8-sig")
        else:
            with pymupdf.open(path) as pdf:
                for number, page in enumerate(pdf, start=1):
                    pages[(path.name, number)] = page.get_text(sort=True)
    for case in cases:
        for item in case["gold_evidence"]:
            if normalize(item["anchor"]) not in normalize(pages.get(source_key(item), "")):
                raise ValueError(f"Âncora ausente no corpus: {case['id']} {item['filename']}")


def model_release(settings):
    """Registra o digest do modelo local, que pode mudar mesmo com uma tag igual."""
    import httpx

    try:
        response = httpx.get(f"{settings.ollama_url}/api/tags", timeout=2, trust_env=False)
        response.raise_for_status()
        for item in response.json().get("models", []):
            if item.get("name") == settings.model_name:
                return item.get("digest")
    except (httpx.HTTPError, AttributeError, TypeError, ValueError):
        return None
    return None


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--output", type=Path, required=True, help="Destino do resultado em JSON")
    cli.add_argument("--retrieval-only", action="store_true", help="Mede a recuperação sem consultar o LLM")
    cli.add_argument("--case", help="Executa um caso específico para diagnóstico, por exemplo Q02")
    args = cli.parse_args()

    from lumifolio.chunking import CHUNK_WORDS, OVERLAP_WORDS
    from lumifolio.config import TOP_K, Settings
    from lumifolio.embeddings import EMBEDDING_MODEL, EMBEDDING_REVISION
    from lumifolio.service import StudyService

    cases = json.loads(CASES.read_text(encoding="utf-8-sig"))
    corpus = sorted(path for path in CORPUS.iterdir() if path.suffix in {".pdf", ".txt"})
    verify_annotations(cases, corpus)
    selected = [case for case in cases if case["id"] == args.case] if args.case else cases
    if not selected:
        cli.error(f"Caso desconhecido: {args.case}")

    stamp = datetime.now(timezone.utc).isoformat()
    rows = []
    runtime = ROOT / ".runtime"
    runtime.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="eval-", dir=runtime, ignore_cleanup_errors=True) as temporary:
        settings = Settings(data_dir=Path(temporary))
        start = perf_counter()
        service = StudyService(settings)
        documents = [service.add_document(path.name, path.read_bytes()) for path in corpus]
        setup_ms = elapsed_ms(start)
        digest = None if args.retrieval_only else model_release(settings)
        for index, case in enumerate(selected):
            print(f"{case['id']} ({index + 1}/{len(selected)})", flush=True)
            rows.append(evaluate_case(service, case, args.retrieval_only, rag_first=index % 2 == 0))

    summary = summarize(rows, args.retrieval_only)
    result = {
        "started_at_utc": stamp,
        "config": {
            "python": platform.python_version(),
            "platform": platform.system(),
            "packages": {
                name: version(name) for name in ("sentence-transformers", "chromadb", "PyMuPDF", "torch")
            },
            "embedding_model": EMBEDDING_MODEL,
            "embedding_revision": EMBEDDING_REVISION,
            "ollama_model": None if args.retrieval_only else settings.model_name,
            "ollama_model_digest": digest,
            "rag_top_k": TOP_K,
            "rag_min_score": settings.min_score,
            "chunk_words": CHUNK_WORDS,
            "overlap_words": OVERLAP_WORDS,
            "index_documents": [document.model_dump(mode="json") for document in documents],
            "rag_prompt_mode": None if args.retrieval_only else MODE,
            "retrieval_only": args.retrieval_only,
            "retrieval_k": KS,
            "index_setup_ms": setup_ms,
            "cases_sha256": sha256(CASES.read_bytes()).hexdigest(),
            "corpus_sha256": {path.name: sha256(path.read_bytes()).hexdigest() for path in corpus},
        },
        "summary": summary,
        "cases": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    failed = not args.retrieval_only and (summary["rag"]["failed_calls"] or summary["baseline"]["failed_calls"])
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
