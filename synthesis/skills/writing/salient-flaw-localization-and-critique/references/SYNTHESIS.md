# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Synthesize feedback comments using a 'Metalinguistic-Split Structure': provide the 'Explanation' first (identifying what is wrong and why), followed by the 'Edit Suggestion' (Action). This forces a clear distinction between the 'Teacher's insight' and the 'User's action.' For example, 'Explanation: You used a singular verb with a plural subject. Suggestion: Change "is" to "are" to agree with the subject "clothes".'
  - Implement 'Hierarchical Synthesis' by front-loading the SLOWPR dimension scores and rationales before the final holistic summary. You must generate 1-2 sentences of 'Criterion-Aligned Justification' for each of the six dimensions to ensure the user perceives the assessment as multi-granular. A concrete application is using headers like 'Logic: 8.5/10. Justification: ...' followed by 'Holistic Score: 8.2/10. Summary: ...' to enforce the hierarchical structure of the MUTA framework.
  - Deploy 'Symmetry-Aware Feedback' that balances 'Correctness' (what the student got right) with 'Constructive Critique' (what needs help) as per Vygotsky's scaffolding. You must explicitly identify 'Solid technical foundations' (Proficiency) before pointing out 'developed design motivations' needed for a higher score. Use linguistic markers like 'While you demonstrated [X], you could improve [Y]' to maintain a supportive pedagogical tone.
  - Apply 'Directness Scaling' to the Edit Suggestion based on the Exploration phase's treatability result. For SLOWPR-level 'Logic' or 'Structure' hints, use suggestive markers like 'Consider bridging chapter 2 and 3 through...' to invite self-correction. For 'Writing' or 'Rigor' corrections, use imperative markers like 'Formatting citations as per APA style...' to ensure adherence to hard academic conventions.
  - Execute a 'Factual Anchor Audit' on the final response to ensure no 'Hallucinated Improvements' occurred. Check that every suggested fix is supported by the document's internal logic or provided sources. If you suggest a user add a 'Starvation' definition, ensure you define it correctly based on OS principles in the context. This prevents the agent from providing 'smooth' but technically incorrect academic or technical advice.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
