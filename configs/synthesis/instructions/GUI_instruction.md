description:
  Starting entity and its description

sampling_tips:
  - Use VM tools to explore the UI and gather concrete evidence
  - Record precise UI states, labels, and values
  - Prefer actionable steps that lead to verifiable facts

selecting_tips:
  - Prefer trajectories with stronger evidence quality and less redundancy.

synthesis_tips:
  - Create questions requiring multi-step UI interactions
  - Keep questions concise (<=3 sentences)
  - Answers should be specific and verifiable from the UI state
  - Provide clear reasoning steps based on observed UI evidence

qa_examples:
  - question: "What is the displayed version number in the settings window?"
    answer: "1.2.3"
