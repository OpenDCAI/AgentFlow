# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Execute 'Deterministic Citation Anchoring' by generating the raw answer as a JSON claim-to-evidence table before translating it into prose. Each claim must be linked to a (doc_id, span_id, offset) tuple. This forces the synthesis engine to verify existence before fluency, ensuring that the final narrative is a strict projection of the evidence table.
  - Apply 'Boundary-Condition Suffixing' to every technical metric description. If a claim is made about a performance value, immediately follow it with the specific ID-verified environment or 'cladding' condition mentioned in the source (e.g., 'achieved 2.2V-cm under p-cladding [ID#4]'). If no such spec exists, replace the metric with a 'Verified Gap' statement to preserve the document's technical integrity.
  - Implement 'Regulated Claim Density' for low-confidence answers. If the cumulative confidence score for a section is < 0.75, you must synthesize the paragraph using 'Epistemic Modality' verbs (e.g., 'appears to suggest,' 'preliminary indicators show'). A concrete rule: never use declarative 'is/are' for findings sourced from 'Tier-5' patent filings or low-confidence vector snippets.
  - Execute a 'Closed-World Reference Audit' as the final synthesis pass. Systematically verify that every bracketed citation number (e.g., [8]) corresponds to the final, de-duplicated bibliography generated from the evidence table. If an extra citation survived the drafting pass, surgically prune it. A success case is a report where a human can click any number and find a 100% DOI-matched verified paper.
  - Format the output to include a 'Technical Disclaimer' if the FSM loop terminated at the retry cap (i=5). If high confidence was not achieved across all subtopics after 5 iterations, you must prepend the answer with a statement identifying which specific sub-questions remained 'Unresolved due to Evidence Gaps.' This maintains the 'Self-Evaluation' standard found in the RA-FSM benchmark.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
