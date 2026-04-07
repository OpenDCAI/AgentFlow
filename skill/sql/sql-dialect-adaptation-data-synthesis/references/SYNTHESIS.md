# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - **Make the target capability the only indispensable shortcut to the answer.** Write the question so that a shallow SQL pattern or memorized template will fail unless the agent performs sql dialect adaptation correctly. Do this by embedding one decisive ambiguity, reasoning dependency, or hidden constraint that only the approved trajectory resolves. An edge case to avoid is a question that sounds sophisticated but can still be solved by issuing a generic SELECT with obvious filters.
  - **Ground every trap in observed evidence from the approved trajectory.** Convert the actual exploration findings into natural-language pressure points, such as a colloquial entity mention, a near-miss distractor, a hidden threshold, a multilingual paraphrase, or a temporal/geospatial dependency. The wording should feel natural to a non-expert, but every hard part must remain traceable to something the agent truly encountered in Phase 1. For example, if the trajectory resolved two competing tables, the final question should preserve exactly that ambiguity rather than introducing a new, unsupported one.
  - **Balance realism with executability.** The synthesized question should sound like something a real developer, analyst, operator, or researcher would ask, yet it must remain precise enough that the approved SQL answer is uniquely recoverable. Achieve this by preserving real entity names, realistic business or scientific goals, and operational phrasing, while avoiding open-ended requests that admit multiple equally valid SQL programs. A useful edge case is to keep one informal phrase in the question, but anchor it with enough relational context that the answer remains objectively checkable.
  - **Write the trajectory as a compressed, causal reasoning chain.** Construct the trajectory field from the actual exploration sequence, but compress it into the minimum ordered steps needed to explain why the final SQL and answer are correct. Each step should pair an observation with the action it motivated, rather than listing raw tool calls without interpretation. A strong example is a trajectory where step 1 identifies the plausible evidence source, step 2 resolves the decisive ambiguity, and step 3 turns that resolved structure into the executable query.

* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
