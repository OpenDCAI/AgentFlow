# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Ask exclusively for one sharply defined fact slot. Generate queries that surgically request one explicit identifier such as a specific date, categorical label, or uncorrupted metric value to ensure automated evaluation remains rigidly crisp. Phrase the query in accessible language, strictly avoiding convoluted subtasks that blend multiple disparate capability targets.
  - Inject related but factually impotent passages into the context bundle. Methodically design synthetic distractors to be topically cohesive, lexically repetitive, factually true in an absolute sense, but wholly non-decisive for the precise slot requested. Leverage temporally adjacent years, highly similar sister-companies, or intimately shared award categories to produce realistic enterprise-level retrieval noise.
  - Force the final answer outcome to depend entirely on respecting the discarded contrast. The target question must be formulated such that if the agent mistakenly trusts the strongest distractor, the final output dramatically and visibly flips to an incorrect state. During generation, logically confirm that swapping the decisive passage with the closest distractor absolutely inverses the generated answer.
  - Implement active character-level substitutions within target support spans. When synthesizing the final JSON evidence blocks, deliberately apply common optical artifacts by replacing '0' with 'O', '1' with 'l', or 'B' with '8' inside critical high-signal tokens. For instance, obscure a vital financial milestone by transforming the target string 'August 2025' into 'Augu5t 2O25' inside the context.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
