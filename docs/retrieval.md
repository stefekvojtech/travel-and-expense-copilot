# Retrieval

Retrieval is implemented as vector search, local reranking, and citation-ready
context assembly.

The current user-facing entrypoint is:

```powershell
python scripts/10_retrieve_context.py "Can I take a taxi from Prague airport after 21:00?"
```

This prints assembled evidence context. Grounded answer generation is available
as a separate runtime entrypoint:

```powershell
python scripts/30_ask.py "Can I take a taxi from Prague airport after 21:00?"
```

## Search Flow

```text
question
  -> OpenAI query embedding
  -> Chroma similarity search
  -> RetrievedChunk records
  -> FlashRank reranking
  -> RerankedChunk records
  -> context assembly
  -> formatted evidence blocks with citation IDs
  -> optional answer generation and validation through app/agents/answer.py
```

Retrieval modules are documented with top-level module docstrings. These
docstrings should make it clear whether a module performs query embedding, local
reranking, or citation-ready context assembly.

## Vector Store

`app/retrieval/step01_search_chunks.py` opens the local Chroma collection configured by:

```text
PROCESSED_DATA_DIR=data/processed
VECTOR_COLLECTION_NAME=travel_expense_policy_chunks
```

The vector-store path is derived as `data/processed/04_vectorstore/`.

The collection metadata is defined in `app/retrieval/chroma_config.py`:

```python
{"hnsw:space": "cosine"}
```

`search_chunks()` embeds the query with the configured OpenAI embedding model.

## Retrieval Filters

The first retrieval pass supports exact-match metadata filters:

- `doc_type`
- `source_path`
- `section_path`

CLI examples:

```powershell
python scripts/10_retrieve_context.py "meal cap Vienna" --doc-type xlsx
python scripts/10_retrieve_context.py "flight evidence" --source-path data/raw/travel_policy.pdf
python scripts/10_retrieve_context.py "receipt required" --section-path "2. Receipt and Evidence Requirements"
```

Stored paths are project-relative POSIX-style paths, such as
`data/raw/expense_policy.html`.

Automatic filter inference from the user question is not yet developed.

## Retrieved Chunks

`RetrievedChunk` contains:

- `text`
- `metadata`
- `cosine_distance`

It exposes helper properties:

- `chunk_id`
- `source_path`
- `section_path`
- `approximate_cosine_similarity`

Approximate similarity is calculated as `1 - cosine_distance`.

## Reranking

`app/retrieval/step02_rerank_chunks.py` reranks vector candidates with FlashRank.

The configured model is:

```text
RERANK_MODEL=ms-marco-MiniLM-L-12-v2
```

Reranking is local after the initial vector search candidates are retrieved.

Current default retrieval settings:

```text
RETRIEVAL_TOP_K=12
RETRIEVAL_RERANK_K=5
RETRIEVAL_CONTEXT_K=4
```

`scripts/10_retrieve_context.py` currently passes all retrieved candidates through
reranking and then lets context assembly select evidence blocks.

## Context Assembly

`app/retrieval/step03_assemble_context.py` converts retrieved or reranked chunks
into evidence blocks.

Each evidence block includes:

- citation ID such as `[1]`
- source title
- source path
- chunk ID
- doc type
- section path
- page when available
- spreadsheet row number when available
- retrieval score
- rerank score when available
- content text

The assembler tries to select diverse evidence by limiting repeated chunks from
the same `(source_path, section_path)` pair before filling remaining slots.

The assembler also applies token budgets:

```text
RETRIEVAL_CONTEXT_MAX_TOKENS=3000
RETRIEVAL_CONTEXT_MAX_BLOCK_TOKENS=800
```

If a block is too long, its content is trimmed and marked with:

```text
[Trimmed to fit context budget.]
```

## Current Output

The search script prints:

```text
=== Assembled Context ===

[1] ...
source_path: ...
chunk_id: ...
doc_type: ...
section_path: ...
page: ...
retrieval_score: ...
rerank_score: ...
content:
...
```

This output is the evidence input to `app/agents/answer.py`.

## Not Yet Developed

The following retrieval-related features are planned but not currently developed:

- source-window expansion around selected chunks
- adjacent chunk collapsing
- inferred metadata filters from the user question
- judge step for unsupported claims
- deterministic tool use for arithmetic or policy-cap lookup

The first answer-generation path validates generated citations against assembled
evidence IDs and abstains before answer generation when all reranked evidence is
below the weak-evidence threshold. It still does not have an independent judge,
source-window expansion, or deterministic confidence explanation beyond the
model-provided confidence and weak-evidence cutoff.
