# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Dynamic Observable Flaws: Generate dynamic issue prompts articulating explicit externally observable behavioral flaws (e.g., timezone bugs, logic duplicates, crashes, NaN generation) while rigorously withholding direct mentions of edit target locations, requiring deep architectural navigation.
  - Diverse Framework Pool: Sample from a 'Diverse Repository Pool' across vastly varying frameworks (Web Django, C++ Systems, PostgreSQL engines, ML PyTorch) when synthesizing instances to ensure the synthetic environment demands zero-shot infrastructure adaptability.
  - Long-Context Dependency Traps: Inject traps where the origin of the bug or a configuration constant is located far away (e.g., in a separate directory or 32k tokens out) from the immediate execution stack, forcing rigorous semantic tracing and environment exploration.
  - Plausible Misdirection: Embed highly plausible misdirection targets harboring identical technical jargon strictly excluded from the genuine failing path, compelling agents to base verification entirely upon execution data rather than semantic pattern matching.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
