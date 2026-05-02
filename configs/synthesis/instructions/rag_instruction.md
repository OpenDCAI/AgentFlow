description:
  Starting entity and its description

sampling_tips:
  - Explore deeply to build multi-hop reasoning chains
  - Focus on gathering specific facts and evidence
  - Use retrieval tools to find relevant information
  - Build dependency chains (A→B→C→D...)
  - Capture hard metadata (dates, versions, IDs, counts)

selecting_tips:
  - Prefer trajectories with stronger evidence quality and less redundancy.

synthesis_tips:
  - Create questions requiring multi-hop reasoning (>=3 hops)
  - Keep questions concise (<=2 sentences)
  - Answers should be specific facts (names, dates, locations)
  - Ensure answer is grounded in trajectory evidence
  - Provide clear reasoning steps

qa_examples:
  - question: "What year was the company founded that developed the framework used in the project?"
    answer: "2004"
