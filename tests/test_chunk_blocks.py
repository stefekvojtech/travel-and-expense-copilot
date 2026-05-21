"""Tests for document chunking strategies."""

from app.ingest.artifacts import BlockArtifact
from app.ingest.step03_chunk_blocks import chunk_blocks


def test_image_markdown_sections_are_merged() -> None:
    chunks = chunk_blocks(
        [
            _block(
                doc_type="image",
                text="\n\n".join(
                    [
                        "# Poster",
                        "## First",
                        "Alpha policy detail.",
                        "## Second",
                        "Beta policy detail.",
                    ]
                ),
            )
        ],
        chunk_size=120,
        chunk_overlap=20,
        max_chunk_tokens=200,
    )

    assert len(chunks) == 1
    assert chunks[0].chunk_strategy == "image_markdown_header_merged"
    assert "## First" in chunks[0].text
    assert "## Second" in chunks[0].text


def test_non_image_markdown_sections_stay_separate() -> None:
    chunks = chunk_blocks(
        [
            _block(
                doc_type="html",
                text="\n\n".join(
                    [
                        "# Policy",
                        "## First",
                        "Alpha policy detail.",
                        "## Second",
                        "Beta policy detail.",
                    ]
                ),
            )
        ],
        chunk_size=120,
        chunk_overlap=20,
        max_chunk_tokens=200,
    )

    assert len(chunks) == 2
    assert all(
        chunk.chunk_strategy == "markdown_header+section_as_chunk"
        for chunk in chunks
    )


def _block(*, doc_type: str, text: str) -> BlockArtifact:
    return BlockArtifact(
        doc_id=f"{doc_type}-doc",
        block_id=f"{doc_type}-doc:00001",
        source_path=f"data/raw/{doc_type}-doc.md",
        doc_type=doc_type,
        title="Test Document",
        block_type="text",
        text=text,
        section_path="Image Extraction" if doc_type == "image" else "Policy",
        page=None,
        order=1,
        metadata={},
    )
