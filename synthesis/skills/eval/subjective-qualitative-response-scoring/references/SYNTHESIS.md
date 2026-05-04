# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate Multi-Faceted Qualitative Constraints: Design prompts that demand specific stylistic, tonal, or behavioral alignments alongside their core functional task. Construct instructions like 'Write a pediatric explanation using a pirate persona while strictly avoiding any bullet points.' Forcing the judge to assess these competing subjective variables simultaneously produces highly robust evaluator training sets.
  - Engineer 'Helpfulness vs Target Style' Conflict Traps: Synthesize candidate options where the agent must choose between being 'overly helpful/explanatory' and following a strict brevity or persona boundary. Command the judge to penalize the overly-helpful model if it breaks character or exceeds the word-limit constraints. This calibrates evaluators to respect user-defined qualitative boundaries over default AI verbosity.
  - Synthesize Cross-Lingual Pragmatic Dilemmas: Create candidate pairs in target languages where one response is a literal, grammatically perfect translation and the other uses authentic, culturally appropriate nuance. Mandate that the evaluation framework explicitly rewards the culturally resonant response over the rigid literal translation by tracking pragmatic alignment. For example, penalizing a Korean assistant for using casual grammar toward a senior figure ensures the judge learns true sociolinguistic evaluation.
  - Require Explicit Top-Down Defect Mapping: Structure the final expected JSON to mandate an itemized list of qualitative deductions before rendering the final ordinal score. Instruct the synthesis engine to generate rationales such as '-1 point for repetitiveness in paragraph 2' and '-2 points for slipping out of formal register'. This ensures the resulting data serves as transparent, fully-auditable training material for critique-generating judges.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
