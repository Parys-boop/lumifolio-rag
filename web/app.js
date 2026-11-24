
"use strict";

const ui = {
  library: document.querySelector("#library"),
  libraryToggle: document.querySelector("#library-toggle"),
  libraryLink: document.querySelector("#library-link"),
  count: document.querySelector("#document-count"),
  list: document.querySelector("#document-list"),
  files: document.querySelector("#files"),
  choose: document.querySelector("#choose-files"),
  examples: document.querySelector("#load-examples"),
  status: document.querySelector("#model-status"),
  model: document.querySelector("#model-label"),
  mode: document.querySelector("#prompt-mode"),
  clear: document.querySelector("#clear-chat"),
  notice: document.querySelector("#notice"),
  welcome: document.querySelector("#welcome"),
  chat: document.querySelector("#chat"),
  processing: document.querySelector("#processing"),
  form: document.querySelector("#ask-form"),
  question: document.querySelector("#question"),
  send: document.querySelector("#send-question"),
  note: document.querySelector("#composer-note"),
};
const historyKey = "lumifolio:chat:v1";
const suggestions = [...document.querySelectorAll(".suggestion")];
let documents = [];
let turns = readChat();
let busy = false;

function node(tag, className, text) {
  const item = document.createElement(tag);
  if (className) item.className = className;
  if (text !== undefined) item.textContent = text;
  return item;
}

function readChat() {
  try {
    const saved = JSON.parse(sessionStorage.getItem(historyKey));
    return Array.isArray(saved) ? saved : [];
  } catch {
    return [];
  }
}

function saveChat() {
  try {
    sessionStorage.setItem(historyKey, JSON.stringify(turns));
  } catch {
    // Se o navegador bloquear o armazenamento, a conversa fica na página aberta.
  }
}

async function api(path, init) {
  let response;
  try {
    response = await fetch(path, init);
  } catch {
    throw new Error("A aplicação local não respondeu. Confira se o Lumifólio continua aberto.");
  }
  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);
  if (!response.ok || data === null) throw new Error(data?.detail || "Não foi possível concluir a operação.");
  return data;
}

function notice(message = "", tone = "info") {
  ui.notice.textContent = message;
  ui.notice.dataset.tone = tone;
  ui.notice.hidden = !message;
}

async function updateModel() {
  try {
    const {ready, model} = await api("/api/status");
    ui.status.dataset.ready = ready;
    ui.status.title = ready ? model : "Inicie o Ollama e verifique se o modelo local foi baixado";
    ui.model.textContent = ready ? "Modelo local pronto" : "Modelo indisponível";
  } catch {
    ui.status.dataset.ready = false;
    ui.model.textContent = "Modelo indisponível";
  }
}

function updateControls() {
  for (const element of [ui.choose, ui.examples, ui.mode, ...ui.list.querySelectorAll("button")]) {
    element.disabled = busy;
  }
  for (const element of [ui.question, ui.send]) element.disabled = busy || !documents.length;
  ui.clear.disabled = busy || !turns.length;
  ui.note.textContent = documents.length
    ? "Confira os trechos citados antes de usar uma resposta."
    : "Adicione materiais à biblioteca para começar.";
}

function renderDocuments() {
  ui.count.textContent = documents.length;
  ui.list.replaceChildren();
  if (!documents.length) {
    ui.list.append(node("p", "empty-library", "Sua biblioteca está vazia."));
  }
  for (const item of documents) {
    const row = node("div", "document");
    const info = node("div");
    const pages = item.pages === null ? "" : ` · ${item.pages} pág. com texto`;
    const meta = `${item.chunks} ${item.chunks === 1 ? "trecho" : "trechos"}${pages}`;
    info.append(node("p", "document-name", item.filename), node("p", "document-meta", meta));
    const remove = node("button", "remove", "×");
    remove.type = "button";
    remove.title = `Remover ${item.filename}`;
    remove.setAttribute("aria-label", remove.title);
    remove.addEventListener("click", () => removeDocument(item));
    row.append(node("span", "file-type", item.filename.split(".").pop().toUpperCase()), info, remove);
    ui.list.append(row);
  }
  updateControls();
}

function setLibrary(open) {
  ui.library.classList.toggle("open", open);
  ui.libraryToggle.setAttribute("aria-expanded", String(open));
}

async function updateDocuments() {
  documents = await api("/api/documents");
  // Uma exclusão torna obsoletos os turnos que ainda exibiriam trechos do arquivo removido.
  const current = new Set(documents.map(item => item.id));
  const kept = turns.filter(turn => turn.result.hits.every(hit => current.has(hit.id.split(":")[0])));
  if (kept.length !== turns.length) {
    turns = kept;
    saveChat();
    renderChat();
  }
  renderDocuments();
}

async function perform(task) {
  if (busy) return;
  busy = true;
  updateControls();
  try {
    await task();
  } catch (error) {
    notice(error.message, "error");
  } finally {
    busy = false;
    updateControls();
  }
}

function shortName(item) {
  return item.page === null ? item.filename : `${item.filename} · p. ${item.page}`;
}

function showAnswer(result) {
  const card = node("div", result.status === "answered" ? "assistant" : "assistant answer-limited");
  const heading = node("div", "assistant-head");
  const mark = node("span", "mark");
  mark.setAttribute("aria-hidden", "true");
  heading.append(mark, node("span", null, "Lumifólio"));
  card.append(heading, node("p", "answer-text", result.answer));
  if (result.citations.length) {
    const citations = node("section", "citations");
    const sources = node("div", "source-list");
    for (const citation of result.citations) {
      const source = node("div", "source");
      source.append(node("strong", null, shortName(citation)), node("blockquote", null, citation.quote));
      sources.append(source);
    }
    citations.append(node("h3", null, "Fontes citadas"), sources);
    card.append(citations);
  }
  if (result.hits.length) {
    const details = node("details", "retrieval");
    details.append(
      node("summary", null, `Ver trechos da busca (${result.hits.length})`),
      node("p", null, "Resultados ordenados por similaridade de cosseno."),
    );
    const submitted = new Set(result.submitted_ids);
    for (const hit of result.hits) {
      const excerpt = node("div", "excerpt");
      const score = hit.score.toFixed(3).replace(".", ",");
      const used = submitted.has(hit.id) ? "Enviado ao modelo" : "Abaixo do limiar";
      excerpt.append(
        node("strong", null, `${shortName(hit)} · trecho ${hit.position}`),
        node("small", null, `${used} · cosseno ${score}`),
        node("p", null, hit.text),
      );
      details.append(excerpt);
    }
    card.append(details);
  }
  return card;
}

function renderChat() {
  ui.welcome.hidden = turns.length > 0;
  ui.chat.hidden = turns.length === 0;
  ui.chat.replaceChildren();
  for (const turn of turns) {
    const item = node("article", "turn");
    const user = node("p", "user-message", turn.question);
    user.setAttribute("aria-label", "Sua pergunta");
    item.append(user, showAnswer(turn.result));
    ui.chat.append(item);
  }
  updateControls();
}

async function removeDocument(item) {
  await perform(async () => {
    await api(`/api/documents/${item.id}`, {method: "DELETE"});
    await updateDocuments();
    notice(`Material removido: ${item.filename}.`);
  });
}

ui.files.addEventListener("change", () => {
  const files = Array.from(ui.files.files);
  ui.files.value = "";
  if (!files.length) return;
  void perform(async () => {
    notice("Lendo e indexando os arquivos…");
    const failures = [];
    let accepted = 0;
    for (const file of files) {
      const form = new FormData();
      form.append("file", file);
      try {
        await api("/api/documents", {method: "POST", body: form});
        accepted++;
      } catch (error) {
        failures.push(`${file.name}: ${error.message}`);
      }
    }
    await updateDocuments();
    const count = accepted ? `${accepted} ${accepted === 1 ? "arquivo processado" : "arquivos processados"}.` : "";
    notice([count, ...failures].filter(Boolean).join("\n"), failures.length ? "error" : "info");
  });
});

ui.examples.addEventListener("click", () => {
  void perform(async () => {
    notice("Preparando os materiais de exemplo…");
    try {
      await api("/api/examples", {method: "POST"});
    } finally {
      await updateDocuments();
    }
    notice("Materiais de exemplo disponíveis na biblioteca.");
  });
});

ui.form.addEventListener("submit", event => {
  event.preventDefault();
  const question = ui.question.value.trim();
  if (!question || !documents.length) return;
  void perform(async () => {
    notice();
    ui.processing.hidden = false;
    ui.processing.scrollIntoView({block: "nearest"});
    try {
      const result = await api("/api/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          question,
          history: turns.slice(-3).map(turn => turn.question),
          mode: ui.mode.value,
        }),
      });
      turns = [...turns.slice(-11), {question, result}];
      saveChat();
      ui.question.value = "";
      renderChat();
      ui.chat.lastElementChild?.scrollIntoView({block: "start"});
    } finally {
      ui.processing.hidden = true;
      void updateModel();
    }
  });
});

ui.clear.addEventListener("click", () => {
  turns = [];
  saveChat();
  notice();
  renderChat();
  window.scrollTo({top: 0});
});

ui.choose.addEventListener("click", () => ui.files.click());
ui.libraryToggle.addEventListener("click", () => setLibrary(!ui.library.classList.contains("open")));
ui.libraryLink.addEventListener("click", event => {
  event.preventDefault();
  setLibrary(true);
  ui.choose.focus();
});
for (const suggestion of suggestions) {
  suggestion.addEventListener("click", () => {
    if (busy) return;
    if (!documents.length) {
      setLibrary(true);
      ui.examples.focus();
      notice("Carregue os exemplos para usar esta pergunta sugerida.");
      return;
    }
    ui.question.value = suggestion.dataset.question;
    ui.question.focus();
  });
}

renderChat();
void updateModel();
updateDocuments().catch(error => notice(error.message, "error"));
