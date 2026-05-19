const form = document.querySelector("#chatForm");
const questionInput = document.querySelector("#questionInput");
const questionEcho = document.querySelector("#questionEcho");
const answerText = document.querySelector("#answerText");
const runtimeStatus = document.querySelector("#runtimeStatus");
const sendButton = document.querySelector("#sendButton");
const confidenceBadge = document.querySelector("#confidenceBadge");
const citationCount = document.querySelector("#citationCount");
const evidenceList = document.querySelector("#evidenceList");
const evidenceSection = document.querySelector(".evidence-section");
const renderMarkdownToggle = document.querySelector("#renderMarkdownToggle");
const warningList = document.querySelector("#warningList");
const contextText = document.querySelector("#contextText");
const exampleRibbon = document.querySelector(".example-ribbon");
const exampleViewport = document.querySelector("#exampleViewport");
const exampleTrack = document.querySelector("#exampleTrack");
const examplesBack = document.querySelector("#examplesBack");
const examplesForward = document.querySelector("#examplesForward");
const authorFooter = document.querySelector("#authorFooter");
const authorName = document.querySelector("#authorName");
const authorLinkedin = document.querySelector("#authorLinkedin");
const authorGithub = document.querySelector("#authorGithub");

const EXAMPLE_AUTO_SCROLL_PIXELS_PER_MS = 0.018;
const EXAMPLE_ARROW_NUDGE_PIXELS = 96;
const PLACEHOLDER_ROTATION_MS = 5000;
const PLACEHOLDER_FADE_MS = 180;

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
let exampleLoopWidth = 0;
let placeholderQuestion = "";
let placeholderTimerId = 0;

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) {
    return;
  }
  void streamQuestion(question);
});

questionInput.addEventListener("input", resizeQuestionInput);
renderMarkdownToggle?.addEventListener("click", toggleEvidenceMarkdownRendering);
window.addEventListener("resize", () => {
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
void loadUiConfig();
resizeQuestionInput();

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
      setStatus("Retrieving...", false);
      break;
    case "retrieval_complete":
      setStatus("Answering...", false);
      renderEvidence(data.evidence_blocks || []);
      contextText.textContent = data.context_text || "No context assembled.";
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
      showError(data.message || "The backend returned an error.");
      break;
    default:
      break;
  }
}

function renderFinalAnswer(data) {
  streamedAnswer = data.answer || streamedAnswer;

  const citations = data.citations || [];
  renderAnswerWithCitations(streamedAnswer || "No answer returned.", citations);

  const confidence = data.confidence || "unknown";
  confidenceBadge.textContent = `Confidence ${confidence}`;
  confidenceBadge.className = `badge ${confidence}`;
  citationCount.textContent = citations.length === 1 ? "1 citation" : `${citations.length} citations`;

  renderEvidence(data.evidence_blocks || []);
  renderWarnings(data.debug?.validation_warnings || []);
  contextText.textContent = data.debug?.context_text || contextText.textContent;
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
  if (!evidenceSection) {
    item.scrollIntoView({ block: "start", behavior: "smooth" });
    return;
  }

  const scrollPadding = getEvidenceScrollPadding();
  evidenceSection.scrollTo({
    top:
      item.getBoundingClientRect().top -
      evidenceSection.getBoundingClientRect().top +
      evidenceSection.scrollTop -
      scrollPadding,
    behavior: "smooth",
  });
}

function getEvidenceScrollPadding() {
  const header = evidenceSection?.querySelector(".debug-section-header");
  const sectionStyle = evidenceSection ? window.getComputedStyle(evidenceSection) : null;
  const sidePadding = sectionStyle ? parseFloat(sectionStyle.paddingLeft) : 0;
  const headerStyle = header ? window.getComputedStyle(header) : null;
  const headerBottomPadding = headerStyle ? parseFloat(headerStyle.paddingBottom) : 0;
  return (
    (header ? header.getBoundingClientRect().height : 0)
    + Math.max(
      0,
      (Number.isFinite(sidePadding) ? sidePadding : 0)
        - (Number.isFinite(headerBottomPadding) ? headerBottomPadding : 0),
    )
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

function resetUi() {
  streamedAnswer = "";
  questionEcho.textContent = "No question yet.";
  questionEcho.classList.add("is-empty");
  answerText.textContent = "No answer yet.";
  confidenceBadge.textContent = "Confidence pending";
  confidenceBadge.className = "badge muted";
  citationCount.textContent = "No citations yet";
  currentEvidenceBlocks = [];
  syncRenderMarkdownToggle();
  evidenceList.innerHTML = '<p class="empty-state">No evidence yet.</p>';
  renderWarnings([]);
  contextText.textContent = "No context assembled yet.";
  setStatus("Idle", false);
}

function setBusy(isBusy) {
  sendButton.disabled = isBusy;
  questionInput.disabled = isBusy;
}

function setStatus(text, isError) {
  runtimeStatus.textContent = text;
  runtimeStatus.classList.toggle("is-error", isError);
}

function showError(message) {
  setStatus("Error", true);
  answerText.textContent = `The request failed before a final answer was returned.\n\n${message}`;
  renderWarnings([message]);
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
  setExampleScrollPosition(exampleScrollPosition + distance);
}

function autoScrollExamples(timestamp) {
  if (!exampleLastFrameTime) {
    exampleLastFrameTime = timestamp;
  }
  const elapsed = timestamp - exampleLastFrameTime;
  exampleLastFrameTime = timestamp;

  if (!exampleAutoScrollPaused && !exampleDragging) {
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
  } catch {
    authorFooter.hidden = true;
  }
}
