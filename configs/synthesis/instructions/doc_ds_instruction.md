description:
  Document or data directory

sampling_tips:
  - For documents: use doc-search and doc-read to locate and extract evidence.
  - For data: use ds:inspect_data, ds:read_csv, and ds:run_python for analysis.
  - Chain operations appropriately based on the seed type.
  - Note: seed_path is automatically provided from seed context.

selecting_tips:
  - Prefer trajectories with stronger evidence quality and less redundancy.

synthesis_tips:
  - Create questions requiring multi-hop reasoning.
  - If using data analysis, ensure answers are grounded in computed results.
  - If using documents, ensure answers are grounded in extracted evidence.

qa_examples:
  - question: ""
    answer: ""
