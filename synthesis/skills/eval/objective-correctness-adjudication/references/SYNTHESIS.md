# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate Hard-Boundary Verifiable Tasks: Draw specific synthesis questions straight from distinct, verifiable knowledge domains such as progressive step-wise math puzzles, bounded 100k-token RAG retrieval modules, or deterministic code executions. Demand that the final generated evaluation rigorously grades exact equivalence or algorithmic fidelity alongside the baseline text.
  - Engineer 'Plausible False' Long-Context Decoys: Manufacture synthetically flawed candidate answers designed to sound expertly written while stealthily replacing specific entities or metrics with outside facts not present in the long context text. Direct the judge to ruthlessly penalize these nuanced context violations, establishing unyielding constraints on reference grounding.
  - Mandate Atomic Step-Wise Auditing Structures: Command the synthesis engine to output a JSON evaluation structure requiring discrete checking across every segment of logic. Construct explicit labels stepping sequentially (e.g., Formula=True, Variable mapping=True, Base Calculation=False) prior to outputting a final score. Forcing this breakdown minimizes skip-logic errors.
  - Deploy 'Target-Language Logic' Stress Prompts: When constructing objective challenges in low-resource or non-English configurations, strictly command the final judge output to base its proof mechanics on native structures and variables. Explicitly require that translation mapping is bypassed when checking variables (e.g. tracking native counters) guaranteeing mathematical resilience cross-linguistically.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
