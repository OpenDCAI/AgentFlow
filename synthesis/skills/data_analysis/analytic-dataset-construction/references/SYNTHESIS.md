# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write questions that sound like ordinary analytical requests but secretly require non-trivial tabular setup. The agent should need to decide which rows, time blocks, consecutive sequences, and units belong in the analysis frame before calling a final basic math function.
  - Make population, denominator, or time-window decisions highly consequential. Good prompts are ones where using the wrong unit of analysis (e.g. daily average vs 24h rolling average constraint) leads to a plausible but structurally incorrect result.
  - Prefer tasks where the final statistic is mechanically simple once the analysis-ready table is built. Medians, sequence flags, or direct totals work well because they let the supervision strictly focus on the agent's preparation quality.
  - Show the construction step explicitly in the trajectory. The JSON should reveal how the agent selected variables, filtered boundaries, declared any sequence counters, and formally readied the dataframe prior to the final calculation payload.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
