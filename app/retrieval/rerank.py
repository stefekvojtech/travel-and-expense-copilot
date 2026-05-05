from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable

from app.retrieval.vector_store import RetrievedChunk


@dataclass(frozen=True)
class RerankedChunk:
    retrieved_chunk: RetrievedChunk
    rerank_score: float

    @property
    def text(self) -> str:
        return self.retrieved_chunk.text

    @property
    def metadata(self) -> dict:
        return self.retrieved_chunk.metadata

    @property
    def cosine_distance(self) -> float:
        return self.retrieved_chunk.cosine_distance

    @property
    def approximate_cosine_similarity(self) -> float:
        return self.retrieved_chunk.approximate_cosine_similarity

    @property
    def chunk_id(self) -> str | None:
        return self.retrieved_chunk.chunk_id

    @property
    def source_path(self) -> str | None:
        return self.retrieved_chunk.source_path

    @property
    def section_path(self) -> str | None:
        return self.retrieved_chunk.section_path


def rerank_chunks(
    query: str,
    retrieved_chunks: Iterable[RetrievedChunk],
    *,
    model_name: str,
    top_k: int,
) -> list[RerankedChunk]:
    """Rerank vector-search candidates with a local FlashRank cross-encoder."""
    chunks = list(retrieved_chunks)
    if not chunks:
        return []

    try:
        from flashrank import RerankRequest
    except ImportError as exc:
        raise RuntimeError(
            "Reranking requires flashrank. Run `python -m pip install -e .` "
            "from the project root after adding the dependency."
        ) from exc

    passages = [
        {
            "id": str(index),
            "text": chunk.text,
            "meta": {"chunk": chunk},
        }
        for index, chunk in enumerate(chunks)
    ]
    ranker = _get_ranker(model_name)
    request = RerankRequest(query=query, passages=passages)
    ranked_passages = ranker.rerank(request)

    reranked: list[RerankedChunk] = []
    for passage in ranked_passages[:top_k]:
        index = int(passage["id"])
        reranked.append(
            RerankedChunk(
                retrieved_chunk=chunks[index],
                rerank_score=float(passage["score"]),
            )
        )
    return reranked


@lru_cache(maxsize=2)
def _get_ranker(model_name: str):
    from flashrank import Ranker

    return Ranker(model_name=model_name)
