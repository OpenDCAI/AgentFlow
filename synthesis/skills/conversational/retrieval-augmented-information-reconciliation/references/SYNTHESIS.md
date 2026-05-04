# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate 'Synthesis-Mandatory Prompts' by providing the user with a task that requires extracting a specific procedure from a very long, technical document. For example, 'I have this 10-page guide on routers, can you just tell me how to change the WiFi name for the 2.4GHz band specifically?'. The synthesized gold response must show the agent extracting and *simplifying* only that part, proving it can synthesize rather than copy.
  - Incorporate 'Behavioral Trap Nudges' where the user asks a question that tempts the agent into excessive tool use. For example, have the user say 'Tell me everything you know about [Product]'. The synthesized 'Expert Response' should NOT dump the whole database. Instead, it should use a 'Request' act: 'I have a lot of info on [Product], are you looking for troubleshooting, specs, or pricing?'. This mimics the human 'Funnel' behavior from the research.
  - Design 'Numeric Reconciliation Challenges' where the search results are contradictory or messy (e.g., one document says 'Out of Stock' but the list shows 1 item left). The synthesized response must acknowledge the conflict or perform a 'Clarifying Search' to resolve it. The gold trace must include a 'Thought' explaining: 'Found conflicting data on stock levels; will prioritize the latest inventory list over the static FAQ.'
  - Construct 'Context-Sensitive Compression' requirements. Engineer a script where the first 5 turns are a friendly chat, and Turn 6 is a technical crisis. The synthesized agent must shift its 'Compression Ratio' dramatically—becoming blunt and efficient (Teacher-Forcing style) when the user expressses urgency or frustration. This tests if the agent can adapt its 'Behavioral Gap' to the emotional situation.
  - Implement 'ROUGE-Targeted Evaluation Hooks' in the JSON trajectory metadata. The synthesis should include a 'Synthesis_Metadata' field: {'rouge_1_target': < 0.6, 'compression_target': > 0.8}. This instructs the model to optimize its language for 'Insight' rather than 'Retrieval', providing the supervising signal for high-quality, non-verbatim RAG generation.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
