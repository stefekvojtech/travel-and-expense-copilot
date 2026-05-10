"""Rebuild stage 02 normalized block artifacts and previews."""

from app.core.config import get_settings
from app.ingest.pipeline_report import write_pipeline_report
from app.ingest.step02_normalize_blocks import normalize_all_blocks


def main() -> None:
    settings = get_settings()
    result = normalize_all_blocks(settings)
    write_pipeline_report(settings, runtime_warnings=result.warnings)
    print(
        f"Normalized {result.block_count} blocks "
        f"from {len(result.documents)} source files."
    )
    if result.warnings:
        print(f"Warnings: {len(result.warnings)}. See {settings.processed_data_dir / 'report.md'}.")


if __name__ == "__main__":
    main()
