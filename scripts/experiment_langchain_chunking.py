from experiments.langchain_chunking.pipeline import run_experiment


def main() -> None:
    result = run_experiment()
    print(
        f"Generated {result.chunk_count} LangChain experiment chunks "
        f"from {len(result.documents)} documents."
    )
    print(f"Output written to {result.output_dir}")
    if result.warnings:
        print(f"Warnings: {len(result.warnings)}. See {result.output_dir}/warnings.jsonl")


if __name__ == "__main__":
    main()
