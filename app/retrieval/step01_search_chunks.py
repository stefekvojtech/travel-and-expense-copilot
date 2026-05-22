"""Open the local Chroma vector store and search embedded policy chunks.

Vector search embeds the incoming query through the configured embedding model,
applies optional exact metadata filters, and returns chunks with their stored
lineage metadata and cosine distance scores.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.config import Settings
from app.core.openai_clients import build_openai_http_client
from app.retrieval.chroma_config import CHROMA_COLLECTION_METADATA

_DEFAULT_EMBEDDING_FUNCTION = object()


@dataclass(frozen=True)
class RetrievalFilters:
    """Exact-match metadata filters supported by the first retrieval pass."""

    doc_type: str | None = None
    source_path: str | None = None
    section_path: str | None = None


@dataclass(frozen=True)
class RetrievedChunk:
    """A chunk returned by vector search, including lineage metadata."""

    text: str
    metadata: dict[str, Any]
    cosine_distance: float

    @property
    def chunk_id(self) -> str | None:
        return _optional_str(self.metadata.get("chunk_id"))

    @property
    def source_path(self) -> str | None:
        return _optional_str(self.metadata.get("source_path"))

    @property
    def section_path(self) -> str | None:
        return _optional_str(self.metadata.get("section_path"))

    @property
    def approximate_cosine_similarity(self) -> float:
        return 1 - self.cosine_distance


def search_chunks(
    settings: Settings,
    query: str,
    *,
    k: int | None = None,
    filters: RetrievalFilters | None = None,
) -> list[RetrievedChunk]:
    """Search embedded chunks in Chroma.

    This function embeds the query, so calling it uses the configured embedding
    provider. The stored chunk text and metadata come from the Chroma collection.
    """
    query_embedding = embed_query(settings, query)
    return search_chunks_by_query_embedding(
        settings,
        query_embedding,
        k=k,
        filters=filters,
    )


def embed_query(settings: Settings, query: str) -> list[float]:
    """Embed a user query with the configured embedding provider."""
    return list(_build_embeddings(settings).embed_query(query))


def search_chunks_by_query_embedding(
    settings: Settings,
    query_embedding: list[float],
    *,
    k: int | None = None,
    filters: RetrievalFilters | None = None,
) -> list[RetrievedChunk]:
    """Search Chroma with an already embedded query vector."""
    vector_store = _open_chroma_vector_store(settings, embedding_function=None)
    where_filter = _build_chroma_filter(filters)
    search_k = k if k is not None else settings.retrieval_top_k

    results = vector_store.similarity_search_by_vector_with_relevance_scores(
        query_embedding,
        k=search_k,
        filter=where_filter,
    )
    return [
        RetrievedChunk(
            text=document.page_content,
            metadata=dict(document.metadata),
            cosine_distance=float(score),
        )
        for document, score in results
    ]


def _build_embeddings(settings: Settings):
    try:
        from langchain_openai import OpenAIEmbeddings
    except ImportError as exc:
        raise RuntimeError(
            "Retrieval requires langchain-openai. Run "
            "`python -m pip install -e .` from the project root."
        ) from exc

    return OpenAIEmbeddings(
        model=settings.embedding_model,
        http_client=build_openai_http_client(),
    )


def _open_chroma_vector_store(
    settings: Settings,
    *,
    embedding_function: Any = _DEFAULT_EMBEDDING_FUNCTION,
):
    try:
        from langchain_chroma import Chroma
    except ImportError as exc:
        raise RuntimeError(
            "Retrieval requires langchain-chroma. "
            "Run `python -m pip install -e .` from the project root."
        ) from exc

    if embedding_function is _DEFAULT_EMBEDDING_FUNCTION:
        embedding_function = _build_embeddings(settings)

    return Chroma(
        collection_name=settings.vector_collection_name,
        embedding_function=embedding_function,
        persist_directory=settings.vector_store_dir.as_posix(),
        collection_metadata=CHROMA_COLLECTION_METADATA,
    )


def _build_chroma_filter(filters: RetrievalFilters | None) -> dict[str, Any] | None:
    if filters is None:
        return None

    conditions: list[dict[str, Any]] = []
    if filters.doc_type:
        conditions.append({"doc_type": {"$eq": filters.doc_type}})
    if filters.source_path:
        # Stored paths are project-relative POSIX-style paths.
        conditions.append({"source_path": {"$eq": filters.source_path.replace("\\", "/")}})
    if filters.section_path:
        conditions.append({"section_path": {"$eq": filters.section_path}})

    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def _optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None
