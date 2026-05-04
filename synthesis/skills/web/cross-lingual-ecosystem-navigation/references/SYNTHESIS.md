# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Construct 'Attribute-Constrained Interactive Tasks' where the user wants a very specific variation of a product (e.g., 'a medium-sized purple silk shirt') from a local-language site. This forces the agent to not just find the product but navigate the non-English dropdown menus and dynamic attribute filters correctly. The synthesis should focus on languages where naming conventions for sizes or colors differ slightly from English (e.g., Asian sizing vs Western sizing).
  - Design 'Cross-Lingual Search-to-Buy Sequences' where the agent is given an initial instruction in one language (e.g., English) but must execute the final transaction on a site in another language (e.g., Japanese or Thai). The task should require at least 3 distinct UI interaction types: Search, Item-Focus, and Attribute-Selection/Checkout. This tests the agent's ability to maintain goal persistence across a language switch.
  - Embed 'Low-Resource Navigation Traps' by choosing target languages where LLMs typically show 'over-action' behavior (e.g., Hindi, Turkish, or Vietnamese). The question should be phrased simply but requires the agent to navigate a complex local UI (like a government registry or a regional shopping mall) that lacks standard English UX patterns. This evaluates if the agent can remain efficient despite tokenization noise or script complexity.
  - Create 'Ambiguous Label Disambiguation' tasks where two buttons in the foreign UI have similar sounding labels but different functions (e.g., 'Return to Shop' vs 'Return Item' in simplified/traditional characters). The prompt should require the agent to choose correctly between them to complete the task. This ensures the agent is performing high-precision UI grounding rather than guessing based on word proximity.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
