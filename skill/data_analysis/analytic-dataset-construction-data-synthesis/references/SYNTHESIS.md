# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write questions that sound like ordinary analytical requests but secretly require non-trivial setup. The agent should need to decide which rows, variables, weights, and units belong in the analysis frame before calculating. This creates natural but powerful training examples.
  - Make population or denominator decisions consequential. Good prompts are ones where using the wrong unit of analysis or the wrong total field leads to a plausible but incorrect result. That encourages careful dataset construction instead of shortcut computation.
  - Prefer tasks where the final statistic is simple once the analysis-ready table is built. Median, percentage, total, or grouped summary outputs work well because they let the supervision focus on setup rather than advanced inference. An edge case to avoid is combining difficult setup with highly open-ended reporting.
  - Show the construction step explicitly in the trajectory. The JSON should reveal how the agent selected variables, filtered the population, applied any documented weighting or recoding, and then handed off to the final calculation. That is the behavior this skill is meant to teach.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
