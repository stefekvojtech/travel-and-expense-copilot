# Markdown Previews

This folder contains human-readable Markdown previews generated during ingestion.

These files are useful for quickly checking whether extraction produced sensible content, headings, tables, and general document flow.

They are not the canonical source for RAG chunking.

The canonical normalized evidence lives in:

```text
data/processed/blocks/
```

Embedding-ready chunks are generated from those block artifacts and written to:

```text
data/processed/chunks/
```