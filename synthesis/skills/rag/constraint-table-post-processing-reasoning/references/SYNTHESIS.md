# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Phrase the query strictly around concrete multi-faceted logic or Numeric Budget Entanglement. Elicit specific operational constraints by naturally requesting the optimal balance of variables, filtering logic combined with 'NOT' statements, or reading table cells based on row-column combinations. Use layman wording to initially conceal the complexity, such as 'Find the best middle ground for my budget' or 'List everyone except those matching this profile'. This tests the model's ability to trigger dense operational processing from basic input.
  - Infuse prompts with Conflicting Familiarity and Role-Reversal Traps. Explicitly design questions that highlight a highly popular domain but explicitly forbid retrieving the famous entities using restrictive negative constraints, or ask for an action performed by an obscure actor role while the context highlights the protagonist. This effectively tests if the operational mapping safely overrides the generative engine's innate autocomplete biases. If the model is lazy, it relies on its bias and instantly fails the constraint.
  - Formulate 'Layman-to-Official' lexical constraints and mask operations until retrieval completion. Construct scenarios where the conversational query deliberately avoids the official terms explicitly used throughout the text and tables, providing instead a localized glossary constraint. Concurrently, distribute the mathematical operands or filtering targets across multiple corpus chunks. This forces the agent to gather the parameters blindly before meticulously initiating the translation and post-processing steps.
  - Vary the operation and filtering families heavily across the synthetic set. Actively balance combinations of multi-objective threshold optimization sweeps, deep negative-constraint entity intersection lists, formal terminology substitution, and numerical representation transformations. Creating this diverse algorithmic exposure ensures the underlying downstream LLM does not overfit onto one single mathematical operation sequence. The capability effectively simulates complex data-analytics workflows running on top of localized text repositories.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
