const form = document.querySelector("#chatForm");
const shell = document.querySelector(".shell");
const chatPane = document.querySelector(".chat-pane");
const questionInput = document.querySelector("#questionInput");
const questionEcho = document.querySelector("#questionEcho");
const answerText = document.querySelector("#answerText");
const answerStream = document.querySelector(".answer-stream");
const runtimeStatus = document.querySelector("#runtimeStatus");
const answerTrace = document.querySelector("#answerTrace");
const answerTraceToggle = document.querySelector("#answerTraceToggle");
const answerTraceLabel = document.querySelector("#answerTraceLabel");
const answerTraceDetails = document.querySelector("#answerTraceDetails");
const sendButton = document.querySelector("#sendButton");
const confidenceBadge = document.querySelector("#confidenceBadge");
const citationCount = document.querySelector("#citationCount");
const evidenceList = document.querySelector("#evidenceList");
const evidenceSection = document.querySelector(".evidence-section");
const debugPane = document.querySelector(".debug-pane");
const debugHeader = document.querySelector(".debug-header");
const contextSection = document.querySelector("#contextSection");
const renderMarkdownToggle = document.querySelector("#renderMarkdownToggle");
const contextText = document.querySelector("#contextText");
const copyContextButton = document.querySelector("#copyContextButton");
const exampleRibbon = document.querySelector(".example-ribbon");
const exampleViewport = document.querySelector("#exampleViewport");
const exampleTrack = document.querySelector("#exampleTrack");
const examplesBack = document.querySelector("#examplesBack");
const examplesForward = document.querySelector("#examplesForward");
const mainSplitter = document.querySelector("#mainSplitter");
const debugSplitter = document.querySelector("#debugSplitter");
const authorFooter = document.querySelector("#authorFooter");
const authorName = document.querySelector("#authorName");
const authorLinkedin = document.querySelector("#authorLinkedin");
const authorGithub = document.querySelector("#authorGithub");

const EMPTY_CONTEXT_TEXT = "No context assembled yet.";
const TRACE_DEFAULT_LABEL = "Processed";
const EXAMPLE_AUTO_SCROLL_PIXELS_PER_MS = 0.018;
const EXAMPLE_ARROW_NUDGE_PIXELS = 96;
const EXAMPLE_ARROW_NUDGE_MS = 280;
const EXAMPLE_WHEEL_PIXELS_PER_LINE = 18;
const PLACEHOLDER_ROTATION_MS = 5000;
const PLACEHOLDER_FADE_MS = 180;
const PANEL_SIZE_STORAGE_KEY = "travelExpenseCopilotPanelSizes";
const PANEL_RESIZE_KEY_STEP = 24;
const STACKED_LAYOUT_MAX_WIDTH = 700;

let activeController = null;
let streamedAnswer = "";
let currentEvidenceBlocks = [];
let shouldRenderEvidenceMarkdown = false;
let exampleQuestions = [];
let exampleAutoScrollPaused = false;
let exampleDragStartX = 0;
let exampleDragStartScrollLeft = 0;
let exampleDragging = false;
let exampleDidDrag = false;
let examplePointerStartButton = null;
let exampleLastFrameTime = 0;
let exampleScrollPosition = 0;
let exampleNudgeAnimation = null;
let exampleLoopWidth = 0;
let placeholderQuestion = "";
let placeholderTimerId = 0;
let activePanelResize = null;
let traceState = createEmptyTraceState();

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) {
    return;
  }
  questionInput.value = "";
  resizeQuestionInput();
  revealConversationUi();
  void streamQuestion(question);
});

questionInput.addEventListener("input", resizeQuestionInput);
renderMarkdownToggle?.addEventListener("click", toggleEvidenceMarkdownRendering);
copyContextButton?.addEventListener("click", copyAssembledContext);
answerTraceToggle?.addEventListener("click", toggleAnswerTrace);
window.addEventListener("resize", () => {
  clampPanelSizes();
  measureExampleLoopWidth();
  rotateExampleScroll();
  requestAnimationFrame(syncEvidenceExpandLinks);
});

questionInput.addEventListener("keydown", (event) => {
  if (event.key !== "Enter" || event.shiftKey) {
    return;
  }
  event.preventDefault();
  form.requestSubmit();
});

setupExampleRibbon();
setupRotatingPlaceholder();
setupPanelResizers();
void loadUiConfig();
resizeQuestionInput();
syncCopyContextButton();

function insertQuestion(question) {
  const currentValue = questionInput.value;
  const selectionStart = questionInput.selectionStart ?? currentValue.length;
  const selectionEnd = questionInput.selectionEnd ?? selectionStart;
  const prefix = currentValue.slice(0, selectionStart);
  const suffix = currentValue.slice(selectionEnd);
  const insertion = `${prefix && !prefix.endsWith("\n") ? "\n" : ""}${question}${
    suffix && !suffix.startsWith("\n") ? "\n" : ""
  }`;

  questionInput.value = `${prefix}${insertion}${suffix}`;
  const cursorPosition = prefix.length + insertion.length;
  questionInput.selectionStart = cursorPosition;
  questionInput.selectionEnd = cursorPosition;
  resizeQuestionInput();
}

function resizeQuestionInput() {
  questionInput.style.height = "auto";
  const computedStyle = window.getComputedStyle(questionInput);
  const lineHeight = parseFloat(computedStyle.lineHeight);
  const paddingTop = parseFloat(computedStyle.paddingTop);
  const paddingBottom = parseFloat(computedStyle.paddingBottom);
  const maxHeight = lineHeight * 12 + paddingTop + paddingBottom;
  const nextHeight = Math.min(questionInput.scrollHeight, maxHeight);

  questionInput.style.height = `${nextHeight}px`;
  questionInput.style.overflowY = questionInput.scrollHeight > maxHeight ? "auto" : "hidden";
}

function revealConversationUi() {
  chatPane?.classList.remove("is-intro");
  answerStream?.removeAttribute("aria-hidden");
}

async function streamQuestion(question) {
  if (activeController) {
    activeController.abort();
  }

  activeController = new AbortController();
  streamedAnswer = "";
  resetUi();
  setBusy(true);
  setStatus("Retrieving...", false);
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
      finalizeTraceAfterError();
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
    case "status_changed":
      handleStatusChanged(data);
      break;
    case "retrieval_started":
      setStatus("Retrieving...", false);
      break;
    case "retrieval_complete":
      setStatus("Answering...", false);
      renderEvidence(data.evidence_blocks || []);
      contextText.textContent = data.context_text || EMPTY_CONTEXT_TEXT;
      syncCopyContextButton();
      break;
    case "trace_started":
      startAnswerTrace(data);
      break;
    case "trace_step_started":
      startAnswerTraceStep(data);
      break;
    case "trace_step_completed":
      completeAnswerTraceStep(data);
      break;
    case "trace_complete":
      completeAnswerTrace(data);
      break;
    case "answer_started":
      setStatus("Answering...", false);
      break;
    case "answer_delta":
      streamedAnswer += data.delta || "";
      answerText.textContent = streamedAnswer;
      break;
    case "answer_replaced":
      streamedAnswer = data.answer || "";
      answerText.textContent = streamedAnswer;
      break;
    case "answer_complete":
      renderFinalAnswer(data);
      setStatus("Complete", false);
      break;
    case "error":
      finalizeTraceAfterError();
      showError(data.message || "The backend returned an error.");
      break;
    default:
      break;
  }
}

function handleStatusChanged(data = {}) {
  const status = data.status || "";
  if (status === "retrieving") {
    setStatus("Retrieving...", false);
    return;
  }
  if (status === "answering") {
    setStatus("Answering...", false);
    return;
  }
  if (status === "complete") {
    if (!traceState.complete && (traceState.hasTrace || traceState.steps.length > 0)) {
      completeAnswerTrace({ elapsed_ms: data.elapsed_ms });
    }
    setStatus("Complete", false);
    return;
  }
  if (status === "error") {
    finalizeTraceAfterError();
    setStatus("Error", true);
  }
}

function createEmptyTraceState() {
  return {
    label: TRACE_DEFAULT_LABEL,
    startedAt: 0,
    elapsedMs: 0,
    steps: [],
    expanded: false,
    complete: false,
    hasTrace: false,
  };
}

function startAnswerTrace(data = {}) {
  traceState = createEmptyTraceState();
  traceState.label = data.label || TRACE_DEFAULT_LABEL;
  traceState.startedAt = performance.now();
  traceState.elapsedMs = data.elapsed_ms || 0;
  traceState.hasTrace = true;
  renderAnswerTrace();
}

function startAnswerTraceStep(data = {}) {
  ensureTraceStarted();
  const sequence = Number(data.sequence);
  const existingStep = traceState.steps.find((step) => step.sequence === sequence);
  const step = existingStep || {
    sequence,
    label: data.label || "Processing...",
    status: "running",
    durationMs: null,
  };

  step.label = data.label || step.label;
  step.status = "running";
  step.durationMs = null;

  if (!existingStep) {
    traceState.steps.push(step);
  }
  renderAnswerTrace();
}

function completeAnswerTraceStep(data = {}) {
  ensureTraceStarted();
  const sequence = Number(data.sequence);
  let step = traceState.steps.find((item) => item.sequence === sequence);
  if (!step) {
    step = {
      sequence,
      label: data.label || "Processing...",
      status: "completed",
      durationMs: null,
    };
    traceState.steps.push(step);
  }

  step.label = data.label || step.label;
  step.status = "completed";
  step.durationMs = typeof data.duration_ms === "number" ? data.duration_ms : null;
  traceState.elapsedMs = typeof data.elapsed_ms === "number" ? data.elapsed_ms : traceState.elapsedMs;
  renderAnswerTrace();
}

function completeAnswerTrace(data = {}) {
  if (!traceState.hasTrace && traceState.steps.length === 0) {
    return;
  }
  traceState.label = data.label || traceState.label || TRACE_DEFAULT_LABEL;
  traceState.elapsedMs = typeof data.elapsed_ms === "number"
    ? data.elapsed_ms
    : elapsedTraceMs();
  traceState.complete = true;
  renderAnswerTrace();
}

function finalizeTraceAfterError() {
  if (!traceState.hasTrace && traceState.steps.length === 0) {
    return;
  }
  traceState.steps.forEach((step) => {
    if (step.status === "running") {
      step.status = "completed";
    }
  });
  traceState.elapsedMs = traceState.elapsedMs || elapsedTraceMs();
  traceState.complete = true;
  renderAnswerTrace();
}

function ensureTraceStarted() {
  if (traceState.hasTrace) {
    return;
  }
  traceState.hasTrace = true;
  traceState.startedAt = performance.now();
}

function toggleAnswerTrace() {
  if (!traceState.complete || traceState.steps.length === 0) {
    return;
  }
  traceState.expanded = !traceState.expanded;
  renderAnswerTrace();
}

function renderAnswerTrace() {
  if (!answerTrace || !answerTraceToggle || !answerTraceLabel || !answerTraceDetails) {
    return;
  }

  const hasExpandableHistory = traceState.complete && traceState.steps.length > 0;
  const runningStep = [...traceState.steps].reverse().find((step) => step.status === "running");

  if (!traceState.hasTrace && !hasExpandableHistory) {
    answerTrace.hidden = true;
    answerTraceDetails.hidden = true;
    return;
  }

  answerTrace.hidden = false;
  answerTrace.classList.toggle("is-running", !traceState.complete);
  answerTrace.classList.toggle("is-complete", traceState.complete);
  answerTrace.classList.toggle("is-expanded", traceState.expanded && hasExpandableHistory);
  answerTraceToggle.setAttribute("aria-expanded", String(traceState.expanded && hasExpandableHistory));
  answerTraceToggle.setAttribute("aria-disabled", String(!hasExpandableHistory));
  answerTraceToggle.tabIndex = hasExpandableHistory ? 0 : -1;

  answerTraceLabel.textContent = traceState.complete
    ? `${traceState.label || TRACE_DEFAULT_LABEL} for ${formatTraceSeconds(traceState.elapsedMs)}`
    : runningStep?.label || "Processing...";

  answerTraceDetails.hidden = !(traceState.expanded && hasExpandableHistory);
  answerTraceDetails.replaceChildren(...traceState.steps.map(renderTraceStepRow));
}

function renderTraceStepRow(step) {
  const row = document.createElement("div");
  row.className = `answer-trace-step is-${step.status || "completed"}`;

  const status = document.createElement("span");
  status.className = "answer-trace-step-status";
  status.setAttribute("aria-hidden", "true");

  const label = document.createElement("span");
  label.className = "answer-trace-step-label";
  label.textContent = step.label;

  row.append(status, label);
  return row;
}

function resetAnswerTrace() {
  traceState = createEmptyTraceState();
  renderAnswerTrace();
}

function elapsedTraceMs() {
  if (!traceState.startedAt) {
    return 0;
  }
  return Math.max(Math.round(performance.now() - traceState.startedAt), 0);
}

function formatTraceSeconds(elapsedMs) {
  const seconds = Math.max(Math.round((elapsedMs || 0) / 1000), 0);
  return seconds === 1 ? "1s" : `${seconds}s`;
}

function renderFinalAnswer(data) {
  if (!traceState.complete && (traceState.hasTrace || traceState.steps.length > 0)) {
    completeAnswerTrace({ elapsed_ms: data.processing_ms });
  }

  streamedAnswer = data.answer || streamedAnswer;

  const citations = data.citations || [];
  renderAnswerWithCitations(streamedAnswer || "No answer returned.", citations);

  const confidence = data.confidence || "unknown";
  confidenceBadge.textContent = `Confidence ${confidence}`;
  confidenceBadge.className = `badge ${confidence}`;
  citationCount.textContent = citations.length === 1 ? "1 citation" : `${citations.length} citations`;
  answerText.classList.toggle(
    "is-problem-answer",
    Boolean(data.abstained || data.debug?.validation_warnings?.length),
  );

  renderEvidence(data.evidence_blocks || []);
  contextText.textContent = data.debug?.context_text || contextText.textContent;
  syncCopyContextButton();
}

function renderEvidence(blocks) {
  currentEvidenceBlocks = blocks;
  syncRenderMarkdownToggle();

  if (blocks.length === 0) {
    evidenceList.innerHTML = '<p class="empty-state">No evidence blocks returned.</p>';
    return;
  }

  evidenceList.replaceChildren(
    ...blocks.map((block) => {
      const item = document.createElement("article");
      item.className = "evidence-item";
      if (block.citation_id) {
        item.dataset.citationKey = normalizeCitationKey(block.citation_id);
      }

      const title = document.createElement("div");
      title.className = "evidence-title";
      title.append(
        textElement("span", block.citation_id || "Evidence"),
        textElement("span", formatScore(block.rerank_score)),
      );

      const meta = document.createElement("div");
      meta.className = "evidence-meta";
      meta.append(
        textElement("span", formatSourceName(block.source_path)),
        textElement("span", formatLocation(block)),
        textElement("span", `Similarity ${formatNumber(block.approximate_cosine_similarity)}`),
      );

      const snippet = shouldRenderEvidenceMarkdown
        ? renderEvidenceMarkdown(block.text || "")
        : textElement("p", block.text || "");
      snippet.className = "evidence-text";

      const snippetWrapper = document.createElement("div");
      snippetWrapper.className = "evidence-text-wrap";

      const expandLink = document.createElement("a");
      expandLink.className = "evidence-expand";
      expandLink.href = "#";
      expandLink.textContent = "more";
      expandLink.setAttribute("aria-expanded", "false");
      expandLink.addEventListener("click", (event) => {
        event.preventDefault();
        const isExpanded = item.classList.toggle("is-expanded");
        expandLink.textContent = isExpanded ? "less" : "more";
        expandLink.setAttribute("aria-expanded", String(isExpanded));
        requestAnimationFrame(() => syncEvidenceExpandLink(item));
      });

      snippetWrapper.append(snippet, expandLink);
      item.append(title, meta, snippetWrapper);
      return item;
    }),
  );
  requestAnimationFrame(syncEvidenceExpandLinks);
}

function toggleEvidenceMarkdownRendering() {
  shouldRenderEvidenceMarkdown = !shouldRenderEvidenceMarkdown;
  syncRenderMarkdownToggle();
  renderEvidence(currentEvidenceBlocks);
}

function syncRenderMarkdownToggle() {
  if (!renderMarkdownToggle) {
    return;
  }
  const hasEvidence = currentEvidenceBlocks.length > 0;
  renderMarkdownToggle.hidden = !hasEvidence;
  renderMarkdownToggle.disabled = !hasEvidence;
  renderMarkdownToggle.tabIndex = hasEvidence ? 0 : -1;
  renderMarkdownToggle.setAttribute("aria-hidden", String(!hasEvidence));
  renderMarkdownToggle.setAttribute("aria-pressed", String(shouldRenderEvidenceMarkdown));
  renderMarkdownToggle.classList.toggle("is-active", shouldRenderEvidenceMarkdown);
}

function renderAnswerWithCitations(answer, citations) {
  const citationMarkers = buildCitationMarkers(citations);
  if (citationMarkers.length === 0) {
    answerText.textContent = answer;
    return;
  }

  const citationKeys = new Map(
    citationMarkers.map((marker) => [marker, normalizeCitationKey(marker)]),
  );
  const citationPattern = new RegExp(
    `(${citationMarkers.map(escapeRegex).join("|")})`,
    "g",
  );
  const nodes = [];
  let lastIndex = 0;
  let match;

  while ((match = citationPattern.exec(answer)) !== null) {
    if (match.index > lastIndex) {
      nodes.push(document.createTextNode(answer.slice(lastIndex, match.index)));
    }
    nodes.push(createCitationButton(match[1], citationKeys.get(match[1]) || match[1]));
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < answer.length) {
    nodes.push(document.createTextNode(answer.slice(lastIndex)));
  }

  answerText.replaceChildren(...nodes);
}

function renderEvidenceMarkdown(markdown) {
  const container = document.createElement("div");
  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];
    const trimmedLine = line.trim();

    if (!trimmedLine) {
      index += 1;
      continue;
    }

    if (isMarkdownTableStart(lines, index)) {
      const { table, nextIndex } = renderMarkdownTable(lines, index);
      container.append(table);
      index = nextIndex;
      continue;
    }

    const headingMatch = /^(#{1,4})\s+(.+)$/.exec(trimmedLine);
    if (headingMatch) {
      const heading = document.createElement(`h${Math.min(headingMatch[1].length + 3, 6)}`);
      appendInlineMarkdown(heading, headingMatch[2]);
      container.append(heading);
      index += 1;
      continue;
    }

    if (/^[-*]\s+/.test(trimmedLine)) {
      const list = document.createElement("ul");
      while (index < lines.length && /^[-*]\s+/.test(lines[index].trim())) {
        const item = document.createElement("li");
        appendInlineMarkdown(item, lines[index].trim().replace(/^[-*]\s+/, ""));
        list.append(item);
        index += 1;
      }
      container.append(list);
      continue;
    }

    const paragraphLines = [trimmedLine];
    index += 1;
    while (
      index < lines.length
      && lines[index].trim()
      && !isMarkdownTableStart(lines, index)
      && !/^(#{1,4})\s+/.test(lines[index].trim())
      && !/^[-*]\s+/.test(lines[index].trim())
    ) {
      paragraphLines.push(lines[index].trim());
      index += 1;
    }

    const paragraph = document.createElement("p");
    appendInlineMarkdown(paragraph, paragraphLines.join(" "));
    container.append(paragraph);
  }

  return container;
}

function isMarkdownTableStart(lines, index) {
  return Boolean(
    lines[index]?.includes("|")
      && /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(lines[index + 1] || ""),
  );
}

function renderMarkdownTable(lines, startIndex) {
  const table = document.createElement("table");
  const headerCells = splitMarkdownTableRow(lines[startIndex]);
  const thead = document.createElement("thead");
  const headerRow = document.createElement("tr");
  for (const cell of headerCells) {
    const th = document.createElement("th");
    appendInlineMarkdown(th, cell);
    headerRow.append(th);
  }
  thead.append(headerRow);
  table.append(thead);

  const tbody = document.createElement("tbody");
  let index = startIndex + 2;
  while (index < lines.length && lines[index].includes("|") && lines[index].trim()) {
    const row = document.createElement("tr");
    for (const cell of splitMarkdownTableRow(lines[index])) {
      const td = document.createElement("td");
      appendInlineMarkdown(td, cell);
      row.append(td);
    }
    tbody.append(row);
    index += 1;
  }
  table.append(tbody);
  return { table, nextIndex: index };
}

function splitMarkdownTableRow(row) {
  return row
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((cell) => cell.trim());
}

function appendInlineMarkdown(parent, text) {
  const pattern = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let lastIndex = 0;
  let match;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parent.append(document.createTextNode(text.slice(lastIndex, match.index)));
    }

    const token = match[0];
    if (token.startsWith("**")) {
      const strong = document.createElement("strong");
      strong.textContent = token.slice(2, -2);
      parent.append(strong);
    } else {
      const code = document.createElement("code");
      code.textContent = token.slice(1, -1);
      parent.append(code);
    }
    lastIndex = match.index + token.length;
  }

  if (lastIndex < text.length) {
    parent.append(document.createTextNode(text.slice(lastIndex)));
  }
}

function buildCitationMarkers(citations) {
  return [...new Set(citations.filter(Boolean).map((citation) => String(citation).trim()))]
    .filter(Boolean)
    .sort((left, right) => right.length - left.length);
}

function createCitationButton(citationMarker, citationKey) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "citation-link";
  button.textContent = citationMarker;
  button.dataset.citationKey = citationKey;
  button.setAttribute("aria-label", `Highlight retrieved chunk ${citationMarker}`);
  button.addEventListener("mouseenter", () => highlightEvidence(citationKey, true));
  button.addEventListener("mouseleave", () => highlightEvidence(citationKey, false));
  button.addEventListener("focus", () => highlightEvidence(citationKey, true));
  button.addEventListener("blur", () => highlightEvidence(citationKey, false));
  return button;
}

function highlightEvidence(citationKey, shouldHighlight) {
  const item = findEvidenceItem(citationKey);
  if (!item) {
    return;
  }

  item.classList.toggle("is-citation-highlighted", shouldHighlight);
  if (shouldHighlight) {
    scrollEvidenceToTop(item);
  }
}

function findEvidenceItem(citationKey) {
  return [...evidenceList.querySelectorAll(".evidence-item")].find(
    (item) => item.dataset.citationKey === citationKey,
  );
}

function scrollEvidenceToTop(item) {
  if (!evidenceList) {
    item.scrollIntoView({ block: "start", behavior: "smooth" });
    return;
  }

  const scrollPadding = getEvidenceScrollPadding();
  evidenceList.scrollTo({
    top:
      item.getBoundingClientRect().top -
      evidenceList.getBoundingClientRect().top +
      evidenceList.scrollTop -
      scrollPadding,
    behavior: "smooth",
  });
}

function getEvidenceScrollPadding() {
  const listStyle = evidenceList ? window.getComputedStyle(evidenceList) : null;
  const listPaddingTop = listStyle ? parseFloat(listStyle.paddingTop) : 0;
  return Number.isFinite(listPaddingTop) ? listPaddingTop : 0;
}

function syncEvidenceExpandLinks() {
  for (const item of evidenceList.querySelectorAll(".evidence-item")) {
    syncEvidenceExpandLink(item);
  }
}

function syncEvidenceExpandLink(item) {
  const text = item.querySelector(".evidence-text");
  const expandLink = item.querySelector(".evidence-expand");
  if (!text || !expandLink) {
    return;
  }

  const isExpanded = item.classList.contains("is-expanded");
  const isOverflowing = text.scrollHeight > text.clientHeight + 1;
  const shouldShowLink = isExpanded || isOverflowing;

  item.classList.toggle("has-overflowing-evidence", shouldShowLink);
  expandLink.hidden = !shouldShowLink;
}

async function copyAssembledContext() {
  if (!contextText || !copyContextButton) {
    return;
  }

  const text = contextText.textContent || "";
  if (!hasAssembledContext(text)) {
    return;
  }

  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      copyTextWithFallback(text);
    }
    showCopyContextResult(true);
  } catch {
    try {
      copyTextWithFallback(text);
      showCopyContextResult(true);
    } catch {
      showCopyContextResult(false);
    }
  }
}

function copyTextWithFallback(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.className = "clipboard-fallback";
  document.body.append(textarea);
  textarea.select();
  document.execCommand("copy");
  textarea.remove();
}

function syncCopyContextButton() {
  if (!copyContextButton || !contextText) {
    return;
  }
  const canCopy = hasAssembledContext(contextText.textContent || "");
  copyContextButton.hidden = !canCopy;
  copyContextButton.disabled = !canCopy;
}

function hasAssembledContext(text) {
  const normalizedText = text.trim();
  return Boolean(normalizedText && normalizedText !== EMPTY_CONTEXT_TEXT);
}

function showCopyContextResult(wasCopied) {
  copyContextButton.dataset.copyState = wasCopied ? "copied" : "failed";
  copyContextButton.setAttribute(
    "aria-label",
    wasCopied ? "Copied assembled context" : "Copy failed",
  );
  window.setTimeout(() => {
    delete copyContextButton.dataset.copyState;
    copyContextButton.setAttribute("aria-label", "Copy assembled context");
  }, 1400);
}

function setupPanelResizers() {
  if (!shell || !debugPane || !mainSplitter || !debugSplitter) {
    return;
  }

  restorePanelSizes();

  mainSplitter.addEventListener("pointerdown", startMainPanelResize);
  mainSplitter.addEventListener("pointermove", dragMainPanelResize);
  mainSplitter.addEventListener("pointerup", stopPanelResize);
  mainSplitter.addEventListener("pointercancel", stopPanelResize);
  mainSplitter.addEventListener("lostpointercapture", stopPanelResize);
  mainSplitter.addEventListener("dblclick", resetMainPanelSize);
  mainSplitter.addEventListener("keydown", handleMainSplitterKeydown);

  debugSplitter.addEventListener("pointerdown", startDebugPanelResize);
  debugSplitter.addEventListener("pointermove", dragDebugPanelResize);
  debugSplitter.addEventListener("pointerup", stopPanelResize);
  debugSplitter.addEventListener("pointercancel", stopPanelResize);
  debugSplitter.addEventListener("lostpointercapture", stopPanelResize);
  debugSplitter.addEventListener("dblclick", resetDebugPanelSize);
  debugSplitter.addEventListener("keydown", handleDebugSplitterKeydown);

  requestAnimationFrame(clampPanelSizes);
}

function startMainPanelResize(event) {
  if (isStackedLayout()) {
    return;
  }
  event.preventDefault();
  activePanelResize = "main";
  mainSplitter.classList.add("is-active");
  document.body.classList.add("is-resizing", "is-resizing-main");
  mainSplitter.setPointerCapture(event.pointerId);
}

function dragMainPanelResize(event) {
  if (activePanelResize !== "main") {
    return;
  }
  setDebugPanelWidth(widthFromMainSplitterPointer(event.clientX));
}

function startDebugPanelResize(event) {
  if (isStackedLayout()) {
    return;
  }
  event.preventDefault();
  activePanelResize = "debug";
  debugSplitter.classList.add("is-active");
  document.body.classList.add("is-resizing", "is-resizing-debug");
  debugSplitter.setPointerCapture(event.pointerId);
}

function dragDebugPanelResize(event) {
  if (activePanelResize !== "debug") {
    return;
  }
  setContextPanelHeight(heightFromDebugSplitterPointer(event.clientY));
}

function stopPanelResize(event) {
  if (!activePanelResize) {
    return;
  }
  if (event?.pointerId !== undefined) {
    for (const splitter of [mainSplitter, debugSplitter]) {
      if (splitter?.hasPointerCapture(event.pointerId)) {
        splitter.releasePointerCapture(event.pointerId);
      }
    }
  }
  activePanelResize = null;
  mainSplitter?.classList.remove("is-active");
  debugSplitter?.classList.remove("is-active");
  document.body.classList.remove("is-resizing", "is-resizing-main", "is-resizing-debug");
  savePanelSizes();
}

function handleMainSplitterKeydown(event) {
  if (isStackedLayout() || !["ArrowLeft", "ArrowRight", "Home"].includes(event.key)) {
    return;
  }
  event.preventDefault();
  if (event.key === "Home") {
    resetMainPanelSize();
    return;
  }
  const direction = event.key === "ArrowLeft" ? 1 : -1;
  setDebugPanelWidth(currentDebugPanelWidth() + direction * PANEL_RESIZE_KEY_STEP);
  savePanelSizes();
}

function handleDebugSplitterKeydown(event) {
  if (isStackedLayout() || !["ArrowUp", "ArrowDown", "Home"].includes(event.key)) {
    return;
  }
  event.preventDefault();
  if (event.key === "Home") {
    resetDebugPanelSize();
    return;
  }
  const direction = event.key === "ArrowUp" ? 1 : -1;
  setContextPanelHeight(currentContextPanelHeight() + direction * PANEL_RESIZE_KEY_STEP);
  savePanelSizes();
}

function resetMainPanelSize() {
  shell?.style.removeProperty("--debug-panel-width");
  savePanelSizes();
}

function resetDebugPanelSize() {
  debugPane?.style.removeProperty("--context-panel-height");
  savePanelSizes();
}

function widthFromMainSplitterPointer(clientX) {
  const shellRect = shell.getBoundingClientRect();
  const splitterSize = mainSplitter.getBoundingClientRect().width || 8;
  return shellRect.right - clientX - (splitterSize / 2);
}

function heightFromDebugSplitterPointer(clientY) {
  const debugRect = debugPane.getBoundingClientRect();
  const footerHeight = authorFooter && !authorFooter.hidden
    ? authorFooter.getBoundingClientRect().height
    : 0;
  const splitterSize = debugSplitter.getBoundingClientRect().height || 8;
  return debugRect.bottom - footerHeight - clientY - (splitterSize / 2);
}

function setDebugPanelWidth(width) {
  if (!shell || isStackedLayout()) {
    return;
  }
  shell.style.setProperty("--debug-panel-width", `${clampDebugPanelWidth(width)}px`);
}

function setContextPanelHeight(height) {
  if (!debugPane || isStackedLayout()) {
    return;
  }
  debugPane.style.setProperty("--context-panel-height", `${clampContextPanelHeight(height)}px`);
}

function clampPanelSizes() {
  if (isStackedLayout()) {
    return;
  }
  syncAuthorFooterHeight();
  if (shell?.style.getPropertyValue("--debug-panel-width")) {
    setDebugPanelWidth(currentDebugPanelWidth());
  }
  if (debugPane?.style.getPropertyValue("--context-panel-height")) {
    setContextPanelHeight(currentContextPanelHeight());
  }
}

function clampDebugPanelWidth(width) {
  const shellRect = shell.getBoundingClientRect();
  const splitterSize = mainSplitter.getBoundingClientRect().width || 8;
  const availableWidth = Math.max(0, shellRect.width - splitterSize);
  const minChatWidth = window.innerWidth <= 1100 ? 340 : 420;
  const minDebugWidth = window.innerWidth <= 1100 ? 300 : 360;
  const maxDebugWidth = Math.max(minDebugWidth, availableWidth - minChatWidth);
  return clamp(width, minDebugWidth, maxDebugWidth);
}

function clampContextPanelHeight(height) {
  syncAuthorFooterHeight();
  const debugRect = debugPane.getBoundingClientRect();
  const headerHeight = debugHeader ? debugHeader.getBoundingClientRect().height : 0;
  const footerHeight = authorFooter && !authorFooter.hidden
    ? authorFooter.getBoundingClientRect().height
    : 0;
  const splitterSize = debugSplitter.getBoundingClientRect().height || 8;
  const availableHeight = Math.max(0, debugRect.height - headerHeight - footerHeight - splitterSize);
  const minEvidenceHeight = minimumEvidencePanelHeight();
  const minContextHeight = window.innerHeight <= 760 ? 110 : 130;
  const maxContextHeight = Math.max(minContextHeight, availableHeight - minEvidenceHeight);
  return clamp(height, minContextHeight, maxContextHeight);
}

function minimumEvidencePanelHeight() {
  if (window.innerHeight <= 760) {
    return Math.ceil(window.innerHeight * 0.48);
  }
  if (window.innerWidth <= 1100) {
    return Math.ceil(window.innerHeight * 0.42);
  }
  return Math.ceil(window.innerHeight * 0.4);
}

function syncAuthorFooterHeight() {
  if (!debugPane || !authorFooter || authorFooter.hidden) {
    debugPane?.style.removeProperty("--author-footer-height");
    return 0;
  }
  const footerHeight = Math.ceil(authorFooter.getBoundingClientRect().height);
  debugPane.style.setProperty("--author-footer-height", `${footerHeight}px`);
  return footerHeight;
}

function currentDebugPanelWidth() {
  return debugPane?.getBoundingClientRect().width || 0;
}

function currentContextPanelHeight() {
  return contextSection?.getBoundingClientRect().height || 0;
}

function isStackedLayout() {
  return window.innerWidth <= STACKED_LAYOUT_MAX_WIDTH;
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function restorePanelSizes() {
  try {
    const rawValue = window.localStorage.getItem(PANEL_SIZE_STORAGE_KEY);
    if (!rawValue) {
      return;
    }
    const sizes = JSON.parse(rawValue);
    if (typeof sizes.debugPanelWidth === "number") {
      shell.style.setProperty(
        "--debug-panel-width",
        `${clampDebugPanelWidth(sizes.debugPanelWidth)}px`,
      );
    }
    if (typeof sizes.contextPanelHeight === "number") {
      debugPane.style.setProperty(
        "--context-panel-height",
        `${clampContextPanelHeight(sizes.contextPanelHeight)}px`,
      );
    }
  } catch {
    window.localStorage.removeItem(PANEL_SIZE_STORAGE_KEY);
  }
}

function savePanelSizes() {
  if (!shell || !debugPane) {
    return;
  }
  const debugWidth = shell.style.getPropertyValue("--debug-panel-width");
  const contextHeight = debugPane.style.getPropertyValue("--context-panel-height");
  try {
    if (!debugWidth && !contextHeight) {
      window.localStorage.removeItem(PANEL_SIZE_STORAGE_KEY);
      return;
    }
    window.localStorage.setItem(
      PANEL_SIZE_STORAGE_KEY,
      JSON.stringify({
        debugPanelWidth: debugWidth ? parseFloat(debugWidth) : null,
        contextPanelHeight: contextHeight ? parseFloat(contextHeight) : null,
      }),
    );
  } catch {
    // Layout preferences are optional; ignore storage failures.
  }
}

function resetUi() {
  streamedAnswer = "";
  questionEcho.textContent = "No question yet.";
  questionEcho.classList.add("is-empty");
  answerText.textContent = "No answer yet.";
  answerText.classList.remove("is-problem-answer");
  confidenceBadge.textContent = "Confidence pending";
  confidenceBadge.className = "badge muted";
  citationCount.textContent = "No citations yet";
  resetAnswerTrace();
  currentEvidenceBlocks = [];
  syncRenderMarkdownToggle();
  evidenceList.innerHTML = '<p class="empty-state">No evidence yet.</p>';
  contextText.textContent = EMPTY_CONTEXT_TEXT;
  syncCopyContextButton();
  setStatus("Idle", false);
}

function setBusy(isBusy) {
  sendButton.disabled = isBusy;
  questionInput.disabled = isBusy;
}

function setStatus(text, isError) {
  runtimeStatus.textContent = text;
  runtimeStatus.hidden = text === "Idle";
  runtimeStatus.classList.toggle("is-error", isError);
}

function showError(message) {
  setStatus("Error", true);
  answerText.textContent = `The request failed before a final answer was returned.\n\n${message}`;
  answerText.classList.add("is-problem-answer");
}

function textElement(tagName, text) {
  const element = document.createElement(tagName);
  element.textContent = text;
  return element;
}

function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function normalizeCitationKey(value) {
  return String(value).trim().replace(/^\[/, "").replace(/\]$/, "");
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
  if (block.row_number !== null && block.row_number !== undefined) {
    parts.push(`row ${block.row_number}`);
  }
  return parts.length ? parts.join(" | ") : block.doc_type || "No location metadata";
}

function formatSourceName(sourcePath) {
  if (!sourcePath) {
    return "Unknown source";
  }
  const normalizedPath = String(sourcePath).replaceAll("\\", "/");
  return normalizedPath.split("/").filter(Boolean).pop() || normalizedPath;
}

function setupExampleRibbon() {
  if (!exampleRibbon || !exampleViewport || !exampleTrack || !examplesBack || !examplesForward) {
    return;
  }

  const originalButtons = [...exampleTrack.querySelectorAll("[data-question]")];
  exampleQuestions = originalButtons
    .map((button) => button.dataset.question || "")
    .filter(Boolean);

  duplicateExampleButtonsForLoop(originalButtons);

  exampleRibbon.addEventListener("mouseenter", () => {
    exampleAutoScrollPaused = true;
  });
  exampleRibbon.addEventListener("mouseleave", () => {
    exampleAutoScrollPaused = false;
  });
  exampleRibbon.addEventListener("focusin", () => {
    exampleAutoScrollPaused = true;
  });
  exampleRibbon.addEventListener("focusout", () => {
    exampleAutoScrollPaused = false;
  });

  exampleViewport.addEventListener("pointerdown", startExampleDrag);
  exampleViewport.addEventListener("pointermove", dragExamples);
  exampleViewport.addEventListener("pointerup", stopExampleDrag);
  exampleViewport.addEventListener("pointercancel", stopExampleDrag);
  exampleViewport.addEventListener("lostpointercapture", stopExampleDrag);
  exampleViewport.addEventListener("wheel", scrollExamplesWithWheel, { passive: false });

  examplesBack.addEventListener("click", () => scrollExamplesBy(-EXAMPLE_ARROW_NUDGE_PIXELS));
  examplesForward.addEventListener("click", () => scrollExamplesBy(EXAMPLE_ARROW_NUDGE_PIXELS));

  requestAnimationFrame(() => {
    measureExampleLoopWidth();
    setExampleScrollPosition(0);
  });
  requestAnimationFrame(autoScrollExamples);
}

function duplicateExampleButtonsForLoop(originalButtons) {
  if (originalButtons.length === 0) {
    return;
  }

  while (exampleTrack.children.length < originalButtons.length * 5) {
    for (const button of originalButtons) {
      const clone = button.cloneNode(true);
      clone.setAttribute("aria-hidden", "true");
      clone.tabIndex = -1;
      exampleTrack.append(clone);
    }
  }
}

function startExampleDrag(event) {
  const target = event.target instanceof Element ? event.target : null;
  exampleDragging = true;
  exampleDidDrag = false;
  exampleNudgeAnimation = null;
  examplePointerStartButton = target?.closest("[data-question]") || null;
  exampleAutoScrollPaused = true;
  exampleDragStartX = event.clientX;
  exampleDragStartScrollLeft = exampleScrollPosition;
  exampleViewport.classList.add("is-dragging");
  exampleViewport.setPointerCapture(event.pointerId);
}

function dragExamples(event) {
  if (!exampleDragging) {
    return;
  }
  event.preventDefault();
  const deltaX = event.clientX - exampleDragStartX;
  if (Math.abs(deltaX) > 6) {
    exampleDidDrag = true;
  }
  setExampleScrollPosition(exampleDragStartScrollLeft - deltaX);
}

function stopExampleDrag(event) {
  if (!exampleDragging) {
    return;
  }

  if (!exampleDidDrag && examplePointerStartButton) {
    insertQuestion(examplePointerStartButton.dataset.question || "");
    questionInput.focus();
  }

  if (event?.pointerId !== undefined && exampleViewport.hasPointerCapture(event.pointerId)) {
    exampleViewport.releasePointerCapture(event.pointerId);
  }

  exampleDragging = false;
  examplePointerStartButton = null;
  exampleViewport.classList.remove("is-dragging");
  exampleAutoScrollPaused = exampleRibbon.matches(":hover") || exampleRibbon.matches(":focus-within");
}

function scrollExamplesBy(distance) {
  if (exampleLoopWidth <= 0) {
    return;
  }
  exampleNudgeAnimation = {
    startPosition: exampleScrollPosition,
    distance,
    startTime: 0,
  };
}

function scrollExamplesWithWheel(event) {
  if (exampleLoopWidth <= 0) {
    return;
  }

  const distance = normalizeExampleWheelDistance(event);
  if (!distance) {
    return;
  }

  event.preventDefault();
  exampleNudgeAnimation = null;
  exampleAutoScrollPaused = true;
  setExampleScrollPosition(exampleScrollPosition + distance);
}

function normalizeExampleWheelDistance(event) {
  const dominantDelta = Math.abs(event.deltaX) > Math.abs(event.deltaY)
    ? event.deltaX
    : event.deltaY;

  if (!dominantDelta) {
    return 0;
  }

  if (event.deltaMode === WheelEvent.DOM_DELTA_LINE) {
    return dominantDelta * EXAMPLE_WHEEL_PIXELS_PER_LINE;
  }

  if (event.deltaMode === WheelEvent.DOM_DELTA_PAGE) {
    return dominantDelta * exampleViewport.clientWidth;
  }

  return dominantDelta;
}

function autoScrollExamples(timestamp) {
  if (!exampleLastFrameTime) {
    exampleLastFrameTime = timestamp;
  }
  const elapsed = timestamp - exampleLastFrameTime;
  exampleLastFrameTime = timestamp;

  if (exampleNudgeAnimation) {
    if (!exampleNudgeAnimation.startTime) {
      exampleNudgeAnimation.startTime = timestamp;
    }
    const progress = Math.min(
      (timestamp - exampleNudgeAnimation.startTime) / EXAMPLE_ARROW_NUDGE_MS,
      1,
    );
    setExampleScrollPosition(
      exampleNudgeAnimation.startPosition
        + exampleNudgeAnimation.distance * easeOutCubic(progress),
    );
    if (progress >= 1) {
      exampleNudgeAnimation = null;
    }
  } else if (!exampleAutoScrollPaused && !exampleDragging) {
    setExampleScrollPosition(exampleScrollPosition + elapsed * EXAMPLE_AUTO_SCROLL_PIXELS_PER_MS);
  }

  requestAnimationFrame(autoScrollExamples);
}

function rotateExampleScroll() {
  if (exampleLoopWidth <= 0) {
    return;
  }
  exampleScrollPosition = normalizeExampleScrollPosition(exampleScrollPosition);
  renderExampleTrackPosition();
}

function setExampleScrollPosition(nextPosition) {
  if (exampleLoopWidth <= 0) {
    return;
  }
  exampleScrollPosition = normalizeExampleScrollPosition(nextPosition);
  renderExampleTrackPosition();
}

function normalizeExampleScrollPosition(position) {
  if (exampleLoopWidth <= 0) {
    return 0;
  }
  return ((position % exampleLoopWidth) + exampleLoopWidth) % exampleLoopWidth;
}

function easeOutCubic(progress) {
  return 1 - ((1 - progress) ** 3);
}

function measureExampleLoopWidth() {
  const firstClone = exampleTrack.children[exampleQuestions.length];
  if (!(firstClone instanceof HTMLElement)) {
    return;
  }
  exampleLoopWidth = firstClone.offsetLeft;
  rotateExampleScroll();
}

function renderExampleTrackPosition() {
  exampleTrack.style.transform = `translate3d(${-exampleScrollPosition}px, 0, 0)`;
}

function setupRotatingPlaceholder() {
  if (!questionInput) {
    return;
  }
  if (exampleQuestions.length === 0) {
    exampleQuestions = [...document.querySelectorAll(".example-button[data-question]")]
      .map((button) => button.dataset.question || "")
      .filter(Boolean);
  }
  if (exampleQuestions.length === 0) {
    return;
  }

  setRandomPlaceholder({ immediate: true });
  placeholderTimerId = window.setInterval(setRandomPlaceholder, PLACEHOLDER_ROTATION_MS);
}

function setRandomPlaceholder(options = {}) {
  const nextQuestion = pickRandomPlaceholderQuestion();
  if (!nextQuestion) {
    return;
  }
  placeholderQuestion = nextQuestion;

  if (options.immediate) {
    questionInput.placeholder = nextQuestion;
    return;
  }

  questionInput.classList.add("is-placeholder-transitioning");
  window.setTimeout(() => {
    questionInput.placeholder = nextQuestion;
    questionInput.classList.remove("is-placeholder-transitioning");
  }, PLACEHOLDER_FADE_MS);
}

function pickRandomPlaceholderQuestion() {
  if (exampleQuestions.length === 0) {
    return "";
  }
  if (exampleQuestions.length === 1) {
    return exampleQuestions[0];
  }

  let nextQuestion = placeholderQuestion;
  while (nextQuestion === placeholderQuestion) {
    nextQuestion = exampleQuestions[Math.floor(Math.random() * exampleQuestions.length)];
  }
  return nextQuestion;
}

async function loadUiConfig() {
  if (!authorFooter || !authorName || !authorLinkedin || !authorGithub) {
    return;
  }

  try {
    const response = await fetch("/api/ui/config", { headers: { Accept: "application/json" } });
    if (!response.ok) {
      return;
    }

    const config = await response.json();
    const name = String(config.author_name || "").trim();
    const linkedinUrl = String(config.author_linkedin_url || "").trim();
    const githubUrl = String(config.author_github_url || "").trim();

    if (!name || !linkedinUrl || !githubUrl) {
      return;
    }

    authorName.textContent = name;
    authorLinkedin.href = linkedinUrl;
    authorLinkedin.setAttribute("aria-label", `${name} on LinkedIn`);
    authorGithub.href = githubUrl;
    authorGithub.setAttribute("aria-label", `${name} on GitHub`);
    authorFooter.hidden = false;
    requestAnimationFrame(() => {
      syncAuthorFooterHeight();
      clampPanelSizes();
    });
  } catch {
    authorFooter.hidden = true;
    syncAuthorFooterHeight();
  }
}
