"""Rebuild stage 01 loaded-document artifacts from raw sources."""

from app.core.config import get_settings
from app.ingest.pipeline_report import write_pipeline_report
from app.ingest.step01_load_documents import load_all_documents


def main() -> None:
    settings = get_settings()
    result = load_all_documents(settings)
    write_pipeline_report(settings, runtime_warnings=result.warnings)
    print(
        f"Loaded {sum(document.loaded_document_count for document in result.documents)} "
        f"document records from {len(result.documents)} source files."
    )
    if result.warnings:
        print(f"Warnings: {len(result.warnings)}. See {settings.processed_data_dir / 'report.md'}.")


if __name__ == "__main__":
    main()
