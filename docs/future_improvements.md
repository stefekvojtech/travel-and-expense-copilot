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

Travel and expense questions often include exact terms that vector search may not
handle perfectly on its own:

- city names
- countries
- times
- dates
- currencies
- amounts
- expense categories
- receipt or invoice terminology
- policy section names

The planner should eventually extract these as entities. Some entities can become
metadata filters when the indexed metadata supports them. Others can become
keyword constraints or separate full-text searches if a keyword search layer is
added.

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

The current project uses local Chroma vector search only. Hybrid keyword search is
not implemented yet.

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

## Evaluation

Future evaluation should measure retrieval quality before and after query
planning. Useful checks include whether each generated retrieval intent finds the
expected source, whether merged results preserve relevant evidence, and whether
oversplitting hurts precision.

## UI

The future UI can expose query-planning debug information in the debug panel:

- detected retrieval intents
- generated search queries
- inferred filters
- retrieved chunks per intent
- merged/reranked candidates
