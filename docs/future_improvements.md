# Future Improvements

This file collects planned and speculative improvements that are useful to keep
visible, but are not implemented yet. The goal is to preserve design thinking
without mixing future behavior into the current pipeline documentation.

## Retrieval

### Query Planning for Long Prompts

Current behavior is intentionally simple: the retrieval script sends the full
incoming query string to vector search, embeds that query, retrieves nearby
chunks from Chroma, reranks the candidates locally with FlashRank, and assembles
citation-ready evidence context.

That works well for focused questions such as:

```text
Can I take a taxi from Prague airport after 21:00?
```

It is less reliable for long prompts that contain instructions, background
story, multiple expense categories, pasted itinerary details, or several
questions in one message. In those cases, embedding the entire user message as
one query can dilute the vector representation. The retrieval embedding has to
represent too many details at once, and semantically important details can
compete with unrelated text.

The planned improvement is to add a query-planning layer before vector search:

```text
incoming user prompt
  -> query planner / router
  -> one or more focused retrieval intents
  -> one or more vector searches
  -> merged and deduplicated candidates
  -> reranking
  -> context assembly
```

The query planner should inspect the incoming prompt itself. It should not first
search the vector database to decide whether the prompt has multiple semantic
units. Search should happen only after the system has created focused retrieval
queries.

#### Semantic Units

A semantic unit is an independently answerable information need. It is not the
same as a text chunk. Prompt chunking should not be a blind sliding-window split
over the user's message.

Examples:

```text
Can I take a taxi from Prague airport after 21:00?
```

This is one semantic unit:

- taxi eligibility from Prague airport after 21:00

```text
Can I take a taxi from Prague airport after 21:00, and do I need a receipt?
```

This likely contains two semantic units:

- taxi eligibility from Prague airport after 21:00
- receipt requirement for taxi reimbursement

```text
I traveled to Vienna and had hotel, dinner, taxi, and laundry expenses. What is
reimbursable?
```

This likely contains several semantic units:

- hotel reimbursement policy
- meal or dinner cap policy
- taxi reimbursement policy
- laundry reimbursement policy

The planner should split only when the prompt contains separate policy questions
or separate expense categories that may need different evidence.

#### Initial Detection Heuristics

The first implementation can be deterministic and local. It does not need an LLM.

Useful signals:

- Multiple question marks, bullet points, numbered lists, or line-separated
  expense rows.
- Conjunctions such as `and`, `also`, `plus`, or `as well as` when they connect
  separate policy topics.
- Multiple domain terms in one prompt, such as `taxi`, `flight`, `hotel`,
  `meal`, `breakfast`, `dinner`, `receipt`, `invoice`, `per diem`, `mileage`,
  `laundry`, `currency`, or `reimbursement cap`.
- Structured pasted inputs such as itinerary lines, receipt lines, or expense
  report rows.
- Mixed task types, such as asking both whether something is allowed and asking
  the system to calculate a reimbursable amount.

The planner should avoid oversplitting. A long but single-purpose question should
usually be condensed into one focused retrieval query rather than split into many
searches.

#### Retrieval Intent Shape

A future retrieval planner could return structured intents instead of raw query
strings. For example:

```python
@dataclass(frozen=True)
class RetrievalIntent:
    query: str
    expense_type: str | None = None
    location: str | None = None
    needs_calculation: bool = False
```

Examples:

```text
Original prompt:
Can I take a taxi from Prague airport after 21:00, and do I need a receipt?

Planned retrieval intents:
1. query="taxi reimbursement Prague airport after 21:00"
   expense_type="taxi"
   location="Prague"
   needs_calculation=False

2. query="receipt requirement taxi reimbursement"
   expense_type="taxi"
   location=None
   needs_calculation=False
```

The final answer generator can still see the original user prompt. The retrieval
queries are only search tools, not replacements for the user's message.

#### Search Strategy

For one focused intent, use the current retrieval flow:

```text
intent query
  -> query embedding
  -> Chroma similarity search
  -> FlashRank reranking
  -> context assembly
```

For multiple intents, run a separate vector search for each focused query. Then
merge and deduplicate the retrieved chunks before reranking. Deduplication should
prefer stable metadata such as `chunk_id`, `source_path`, and `section_path`.

The merged candidate pool can be ranked with a simple first version:

- keep the best retrieval score seen for each chunk
- keep the list of retrieval intents that matched each chunk
- cap the number of candidates per intent so one subquery does not dominate
- pass the pooled candidates through the existing reranker

A later version can use Reciprocal Rank Fusion-style rank merging. This is useful
when combining several ranked result lists because it rewards chunks that rank
well across multiple searches without depending on raw score comparability.

#### Hybrid Retrieval Considerations

Hybrid retrieval is a strong future fit for this project, but it is not
implemented yet. The current retrieval path is vector-only candidate generation
followed by local reranking:

```text
query
  -> OpenAI query embedding
  -> Chroma vector search
  -> FlashRank reranking
  -> context assembly
```

FlashRank can improve the order of the chunks returned by Chroma, but it cannot
recover a chunk that vector search never put into the candidate set. That matters
for this domain because travel and expense questions often combine semantic
policy wording with exact lookup terms that embeddings may blur:

- city names
- countries
- times
- dates
- currencies
- amounts
- expense categories
- receipt or invoice terminology
- policy section names

Examples from the golden eval set include questions about `Vienna`, `Prague`,
`Berlin`, `Zurich`, `Munich`, `22:00`, `0.42`, `35 EUR`, hotel caps, taxi
thresholds, receipt evidence, and alcohol exclusions. These are not only
semantic concepts. They are also exact tokens or structured values that should be
easy to match directly.

The existing ingestion pipeline already prepares useful structure for this. XLSX
rows are chunked as row-level chunks, with worksheet location in `section_path`
and row location in `row_number`. A future hybrid implementation can derive
additional structured values from row text or a purpose-built index instead of
treating every query as plain unstructured text.

This suggests a future hybrid retrieval design:

```text
focused semantic query
  -> vector search

extracted keywords/entities
  -> keyword or metadata search

combined candidates
  -> merge / dedupe / rank fusion
  -> reranking
  -> context assembly
```

The current project uses local Chroma vector search only. Hybrid keyword search,
expanded metadata filtering, candidate fusion, and hybrid retrieval evaluation
are not implemented yet.

##### Recommended Hybrid Architecture

The first hybrid implementation should stay local-first and dependency-light:

1. Keep Chroma as the semantic vector retriever.
2. Add a local keyword index over `data/processed/03_chunks/*.jsonl`.
3. Prefer SQLite FTS5 for the first keyword index because it is local, widely
   available with Python, supports BM25-style scoring, and avoids adding a
   search server.
4. Store one keyword-search row per chunk, including `chunk_id`, `doc_id`,
   `source_path`, `doc_type`, `section_path`, `title`, chunk text, and useful
   scalar metadata.
5. Rebuild the keyword index from chunk artifacts as part of a future retrieval
   indexing step, not from the Chroma database. The chunk JSONL files should
   remain the shared source of truth for both vector and keyword indexes.

The planned retrieval flow should look like this:

```text
incoming prompt
  -> optional query planner / entity extractor
  -> focused retrieval intent
  -> Chroma vector search
  -> SQLite FTS keyword search
  -> optional metadata-filtered exact lookup
  -> merge and deduplicate candidates by chunk_id
  -> rank fusion
  -> FlashRank reranking
  -> context assembly
```

Hybrid retrieval should be treated as candidate generation. The existing
FlashRank reranker should remain the final relevance sorter before context
assembly, at least for the first implementation.

##### Metadata Filters Before Heavy Search Logic

Before adding complex keyword behavior, consider adding a purpose-built metadata
or keyword index for structured values the project can derive:

- `city`
- `country`
- `country_code`
- `expense_category`
- `currency`

For table-driven questions such as hotel caps, meal caps, mileage rates, and taxi
thresholds, metadata filters may produce a smaller and better candidate set than
either plain vector search or plain keyword search.

Filter extraction can start deterministic and conservative. For example:

- detect known cities/countries from indexed or derived values
- detect expense-category terms such as `hotel`, `meal`, `taxi`, `flight`,
  `receipt`, `mileage`, `entertainment`, and `alcohol`
- preserve exact numeric/time/currency tokens such as `22:00`, `35 EUR`, or
  `0.42`

This does not require an LLM. A later router can make this more flexible, but the
first version should be transparent and easy to evaluate.

##### Candidate Fusion

Do not compare raw Chroma cosine distances and SQLite BM25 scores directly. They
are not on the same scale. The first implementation should merge ranked result
lists with a rank-based method such as Reciprocal Rank Fusion.

The fused candidate record should preserve debug information:

- chunk ID
- source path
- vector rank and score when present
- keyword rank and score when present
- metadata filters that matched
- retrieval intent that produced the candidate
- fused rank or fused score

This debug data will matter later for evaluation, UI inspection, and confidence
scoring.

##### What Not To Do First

Avoid these in the first hybrid version:

- Do not add Elasticsearch, OpenSearch, or a managed search service.
- Do not replace Chroma with a different vector database just to get hybrid
  search.
- Do not make an LLM choose final evidence before deterministic retrieval and
  reranking.
- Do not hardcode lookup behavior for the current demo spreadsheet rows.
- Do not rely on raw score thresholds until retrieval evaluation shows stable
  score behavior.

The goal is better recall for grounded answers, not a large search platform.

##### Evaluation Before And After Hybrid Search

Hybrid retrieval should be implemented only with retrieval evaluation around it.
The golden eval set already contains many cases where exact matching should help:

- city caps: Vienna, Berlin, Zurich, Munich
- taxi thresholds and times
- private car mileage rate
- receipt and evidence rules
- alcohol and non-reimbursable exclusions
- unsupported items that should lead to abstention

The eval runner should compare vector-only retrieval against hybrid retrieval
using at least:

- required-source hit@k before reranking
- required-source hit@k after reranking
- required-source presence in assembled context
- citation-source correctness
- abstention behavior for unsupported items
- whether metadata filters helped or incorrectly excluded relevant evidence

Hybrid should be considered successful only if it improves exact lookup recall
without noticeably reducing precision for semantic policy questions.

#### Prompt Length Handling

There are two separate issues:

1. The prompt may exceed the embedding model's input limit.
2. The prompt may be below the limit but still be a poor retrieval query because
   it contains too many unrelated details.

The planner should handle both. If a prompt is too long, the system should not
blindly truncate from the end. It should extract or summarize the parts relevant
to retrieval, then search with concise focused queries.

Even when the prompt fits within the embedding model's token limit, query
planning can still improve retrieval quality by removing conversational filler,
formatting instructions, examples, and unrelated background.

#### Practical First Version

A conservative first implementation could use this decision flow:

```text
analyze incoming prompt
  -> if short and single-intent:
       use current search flow
  -> if long but single-intent:
       condense to one focused query
  -> if multiple policy intents:
       create one query per intent
  -> if many expense lines:
       group by expense category before searching
  -> if too broad or ambiguous:
       ask a clarification question or retrieve broad policy overview evidence
```

Suggested guardrails:

- Do not create many searches for tiny wording differences.
- Limit the number of retrieval intents in one turn, for example to 3-5.
- Group repeated expense categories before searching.
- Preserve the original prompt for final answer generation.
- Record which generated retrieval query produced each selected evidence block.
- Include query-planning behavior in retrieval evaluation once an eval runner
  exists.

#### Future LLM-Based Router

The first version can be rule-based. Later, when answer-generation prompts are
added, this logic can move into a small LLM router or planner prompt under
`app/prompts/router_fewshot.md`.

That router should return structured output, not free-form prose. It should
separate:

- user intent
- retrieval queries
- extracted filters/entities
- whether deterministic tools are needed
- whether clarification is needed before retrieval

The router should remain cheap and bounded. It should not answer the policy
question directly. For policy questions, retrieval must still happen before final
answer generation.

## Answer Generation

Future answer generation should use the assembled evidence context rather than
answering directly from the user's question. Final answers should include
citations, confidence, and abstention behavior when evidence is weak.

### Chat History and Sessions

Chat history is planned future work, not implemented behavior.

The current copilot flow treats each user prompt as a standalone question. A
future version should support chat sessions where the user can ask follow-up
questions, refine details, and refer back to earlier turns in the same
conversation.

The session layer should preserve prior user messages, assistant answers,
retrieved evidence, citations, and any deterministic tool results needed to
interpret later turns. Follow-up questions such as "what about dinner?" should
be resolved against the active session context before retrieval and answer
generation.

Chat history should not replace retrieval. Each policy answer should still be
grounded in fresh or session-relevant evidence, with citations and confidence.
The system should avoid treating earlier generated answers as policy evidence.

## Receipt OCR and Claim Intake

Receipt image upload and OCR post-processing are planned future work. The current
image ingestion path extracts Markdown text from images for corpus indexing, but
it does not normalize uploaded bills into structured receipt data for claim
evaluation.

The current browser UI intentionally does not expose file upload. A future UI/API
workflow can add explicit upload controls once the backend has a scoped intake
route, clear cost warnings, and a defined storage policy for uploaded artifacts.

The future receipt flow should support one or more uploaded bill images:

```text
receipt image or images
  -> local upload API
  -> vision/OCR extraction
  -> receipt post-processor
  -> structured receipt records
  -> claim eligibility evaluator
  -> evidence completeness checker
```

Multiple images may represent separate receipts or multiple photos/pages of the
same receipt. The first implementation should make that distinction explicit in
the input instead of guessing silently.

The post-processor should normalize extracted bill data into a clean Python
structure with fields such as:

- vendor
- transaction date
- receipt total
- tax amount when visible
- currency
- payment method when visible
- line items with description, amount, quantity, and category guesses
- unclear fields and extraction warnings
- source image path or upload ID

This should stay separate from policy lookup. OCR extracts claim facts from the
bill. Retrieval still provides policy evidence, and deterministic tools apply
retrieved policy facts to the structured claim.

Vision extraction uses paid model calls when implemented with OpenAI vision, so
the upload/OCR path should be explicit and opt-in. A later version can consider a
local OCR fallback, but the first version can use the existing OpenAI-backed
image extraction pattern if the user approves the cost.

A future browser upload workflow should:

- accept PNG/JPG/PDF receipt files through a dedicated API route
- keep uploaded files local by default
- show that OpenAI vision/OCR is a paid call before processing
- stream extraction progress to the UI
- display extracted receipt fields for user review before claim evaluation
- link extracted fields back to source image regions or page references when
  practical
- avoid sending raw uploaded files to the answer model unless the user explicitly
  starts the OCR/extraction flow

Useful open design decisions:

- whether extracted receipt records are temporary only or written to a local
  inspection folder
- whether the first UI/API accepts images directly or starts with a structured
  JSON receipt input
- how to represent confidence for unclear OCR fields
- how to group multiple images into one claim versus multiple claims

## Evaluation

Future evaluation should measure retrieval quality before and after query
planning. Useful checks include whether each generated retrieval intent finds the
expected source, whether merged results preserve relevant evidence, and whether
oversplitting hurts precision.

### Answer-Level Regression Evaluation

The current eval runner is retrieval-focused. It checks whether the retrieval
pipeline finds, reranks, and assembles the expected evidence for each golden
question. That is useful for testing the evidence pipeline, but it is not the
same as testing the final copilot answer from `scripts/30_ask.py`.

A future answer-level eval runner should be treated as a regression test suite
for final answer behavior, not as part of the normal user flow. It would run the
full path:

```text
question
  -> retrieval
  -> reranking
  -> context assembly
  -> answer generation
  -> answer validation / judge checks
```

The likely command could live in the `20_*` evaluation band, for example:

```powershell
python scripts/21_run_answer_eval.py
```

This should be useful after changing prompts, retrieval behavior, context
assembly, abstention thresholds, deterministic tools, or judge logic. It should
help catch regressions that retrieval-only eval cannot see, such as:

- the right evidence was present, but the generated answer missed the policy
  point
- the answer cited evidence IDs that exist but do not support the specific claim
- the answer failed to abstain for a `should_abstain` case
- the answer performed arithmetic or cap logic incorrectly
- confidence was inconsistent with the available evidence

The first version does not need to be elaborate. It can start by running a small
subset of golden examples through `app/agents/answer.py` and recording structured
outputs for human inspection. Later versions can add deterministic checks for
citation presence and abstention behavior, then an independent judge step for
groundedness and claim support.

## UI

The future UI can expose query-planning debug information in the debug panel:

- detected retrieval intents
- generated search queries
- inferred filters
- retrieved chunks per intent
- merged/reranked candidates
