from app.core.config import get_settings
from app.ingest.pipeline import ingest_sources


def main() -> None:
    settings = get_settings()
    documents = ingest_sources(settings)
    print(f"Ingested {len(documents)} documents.")

