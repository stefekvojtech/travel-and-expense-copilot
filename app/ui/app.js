const form = document.querySelector("#chatForm");
const questionInput = document.querySelector("#questionInput");
const questionEcho = document.querySelector("#questionEcho");
const answerText = document.querySelector("#answerText");
const runtimeStatus = document.querySelector("#runtimeStatus");
const sendButton = document.querySelector("#sendButton");
const clearButton = document.querySelector("#clearButton");
const confidenceBadge = document.querySelector("#confidenceBadge");
const citationCount = document.querySelector("#citationCount");
const debugStage = document.querySelector("#debugStage");
const debugEvidenceCount = document.querySelector("#debugEvidenceCount");
const debugCitations = document.querySelector("#debugCitations");
const debugJudge = document.querySelector("#debugJudge");
const evidenceList = document.querySelector("#evidenceList");
const warningList = document.querySelector("#warningList");
const contextText = document.querySelector("#contextText");
const contextSection = document.querySelector("#contextSection");
const toggleContextButton = document.querySelector("#toggleContextButton");
const exampleButtons = document.querySelectorAll("[data-question]");

let activeController = null;
let streamedAnswer = "";

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) {
    return;
  }
  void streamQuestion(question);
});

clearButton.addEventListener("click", () => {
  if (activeController) {
    activeController.abort();
    activeController = null;
  }
  questionInput.value = "";
  resetUi();
  questionInput.focus();
});

toggleContextButton.addEventListener("click", () => {
  contextSection.classList.toggle("is-hidden");
});

for (const button of exampleButtons) {
  button.addEventListener("click", () => {
    const question = button.dataset.question || "";
    questionInput.value = question;
    void streamQuestion(question);
  });
}

async function streamQuestion(question) {
  if (activeController) {
    activeController.abort();
  }

  activeController = new AbortController();
  streamedAnswer = "";
  resetUi();
  setBusy(true);
  setStatus("Retrieving", false);
  questionEcho.textContent = question;
  questionEcho.classList.remove("is-empty");
  answerText.textContent = "";

  try {
    const response = await fetch("/api/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({ question }),
      signal: activeController.signal,
    });

    if (!response.ok || !response.body) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    await readSseStream(response.body, handleStreamEvent);
  } catch (error) {
    if (error.name !== "AbortError") {
      showError(error.message || "Streaming request failed.");
    }
  } finally {
    setBusy(false);
    activeController = null;
  }
}

async function readSseStream(body, onEvent) {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const messages = buffer.split("\n\n");
    buffer = messages.pop() || "";
    for (const message of messages) {
      const parsed = parseSseMessage(message);
      if (parsed) {
        onEvent(parsed.event, parsed.data);
      }
    }
  }

  buffer += decoder.decode();
  const parsed = parseSseMessage(buffer);
  if (parsed) {
    onEvent(parsed.event, parsed.data);
  }
}

function parseSseMessage(message) {
  const trimmed = message.trim();
  if (!trimmed) {
    return null;
  }

  let eventName = "message";
  const dataLines = [];

  for (const line of trimmed.split(/\r?\n/)) {
    if (line.startsWith("event:")) {
      eventName = line.slice("event:".length).trim();
    }
    if (line.startsWith("data:")) {
      dataLines.push(line.slice("data:".length).trimStart());
    }
  }

  if (dataLines.length === 0) {
    return null;
  }

  return {
    event: eventName,
    data: JSON.parse(dataLines.join("\n")),
  };
}

function handleStreamEvent(eventName, data) {
  switch (eventName) {
    case "retrieval_started":
      setStatus("Retrieving", false);
      debugStage.textContent = "Retrieval started";
      break;
    case "retrieval_complete":
      setStatus("Generating", false);
      debugStage.textContent = "Retrieval complete";
      renderEvidence(data.evidence_blocks || []);
      contextText.textContent = data.context_text || "No context assembled.";
      break;
    case "answer_started":
      setStatus(`Generating with ${data.model || "model"}`, false);
      debugStage.textContent = "Answer started";
      break;
    case "answer_delta":
      streamedAnswer += data.delta || "";
      answerText.textContent = streamedAnswer;
      break;
    case "answer_replaced":
      streamedAnswer = data.answer || "";
      answerText.textContent = streamedAnswer;
      debugStage.textContent = data.reason || "Answer replaced";
      break;
    case "answer_complete":
      renderFinalAnswer(data);
      setStatus("Complete", false);
      debugStage.textContent = data.abstained ? "Abstained" : "Complete";
      break;
    case "error":
      showError(data.message || "The backend returned an error.");
      break;
    default:
      debugStage.textContent = eventName;
  }
}

function renderFinalAnswer(data) {
  streamedAnswer = data.answer || streamedAnswer;
  answerText.textContent = streamedAnswer || "No answer returned.";

  const citations = data.citations || [];
  const confidence = data.confidence || "unknown";
  confidenceBadge.textContent = `Confidence ${confidence}`;
  confidenceBadge.className = `badge ${confidence}`;
  citationCount.textContent = citations.length === 1 ? "1 citation" : `${citations.length} citations`;
  debugCitations.textContent = citations.length ? citations.join(", ") : "None";
  debugJudge.textContent = data.judge_result ? "Available" : "Not implemented";

  renderEvidence(data.evidence_blocks || []);
  renderWarnings(data.debug?.validation_warnings || []);
  contextText.textContent = data.debug?.context_text || contextText.textContent;
}

function renderEvidence(blocks) {
  debugEvidenceCount.textContent = blocks.length === 1 ? "1 chunk" : `${blocks.length} chunks`;

  if (blocks.length === 0) {
    evidenceList.innerHTML = '<p class="empty-state">No evidence blocks returned.</p>';
    return;
  }

  evidenceList.replaceChildren(
    ...blocks.map((block) => {
      const item = document.createElement("article");
      item.className = "evidence-item";

      const title = document.createElement("div");
      title.className = "evidence-title";
      title.append(
        textElement("span", block.citation_id || "Evidence"),
        textElement("span", formatScore(block.rerank_score)),
      );

      const meta = document.createElement("div");
      meta.className = "evidence-meta";
      meta.append(
        textElement("span", block.source_path || "Unknown source"),
        textElement("span", formatLocation(block)),
        textElement("span", `Similarity ${formatNumber(block.approximate_cosine_similarity)}`),
      );

      const snippet = textElement("p", block.text || "");
      snippet.className = "evidence-text";

      item.append(title, meta, snippet);
      return item;
    }),
  );
}

function renderWarnings(warnings) {
  warningList.classList.toggle("has-warning", warnings.length > 0);
  warningList.replaceChildren(
    ...(warnings.length ? warnings : ["No validation warnings."]).map((warning) =>
      textElement("li", warning),
    ),
  );
}

function resetUi() {
  streamedAnswer = "";
  questionEcho.textContent = "No question yet.";
  questionEcho.classList.add("is-empty");
  answerText.textContent = "No answer yet.";
  confidenceBadge.textContent = "Confidence pending";
  confidenceBadge.className = "badge muted";
  citationCount.textContent = "No citations yet";
  debugStage.textContent = "Idle";
  debugEvidenceCount.textContent = "0 chunks";
  debugCitations.textContent = "None";
  debugJudge.textContent = "Not implemented";
  evidenceList.innerHTML = '<p class="empty-state">No evidence yet.</p>';
  renderWarnings([]);
  contextText.textContent = "No context assembled yet.";
  setStatus("Idle", false);
}

function setBusy(isBusy) {
  sendButton.disabled = isBusy;
  questionInput.disabled = isBusy;
  for (const button of exampleButtons) {
    button.disabled = isBusy;
  }
}

function setStatus(text, isError) {
  runtimeStatus.textContent = text;
  runtimeStatus.classList.toggle("is-error", isError);
}

function showError(message) {
  setStatus("Error", true);
  debugStage.textContent = "Error";
  answerText.textContent = `The request failed before a final answer was returned.\n\n${message}`;
  renderWarnings([message]);
}

function textElement(tagName, text) {
  const element = document.createElement(tagName);
  element.textContent = text;
  return element;
}

function formatScore(value) {
  if (typeof value !== "number") {
    return "No rerank score";
  }
  return `Rerank ${formatNumber(value)}`;
}

function formatNumber(value) {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "n/a";
  }
  return value.toFixed(3);
}

function formatLocation(block) {
  const parts = [];
  if (block.section_path) {
    parts.push(block.section_path);
  }
  if (block.page_label) {
    parts.push(`page ${block.page_label}`);
  }
  if (block.sheet_label) {
    parts.push(`sheet ${block.sheet_label}`);
  }
  if (block.row_number !== null && block.row_number !== undefined) {
    parts.push(`row ${block.row_number}`);
  }
  return parts.length ? parts.join(" | ") : block.doc_type || "No location metadata";
}
