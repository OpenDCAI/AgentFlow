# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate 'Register-Stressed' prompts that specify high-difficulty domains (Law, Medicine, Academia). Synthesize the question by asking for a translation 'according to the Law domain' or 'for a scientific journal article.' This forces the agent to demonstrate 'Register Preservation' and avoid the path of least resistance (generic translation). Example: 'Translate this medical trial abstract into Portuguese, maintaining a professional clinical register and excluding lay terms.'
  - Deploy 'Syntactic Entrapment' using long-context clausal sequences. Synthesize input structures involving sentences exceeding 40 words with multiple embedded relative clauses and technical caveats. This tests the agent's ability to maintain 'Structural Isomorphism' and resist the urge to break or summarize the text. The gold answer must show 100% adherence to the complex logic-path of the original technical claim.
  - Embed 'Polysemous Disambiguation' seeds in professional context blocks. Design synthetic tasks where a word with divergent meanings (e.g., 'division', 'capital', 'case') is placed in a sentence where only one domain-specific meaning is logical. Then, provide the 'Domain Tag' to see if the agent uses it to resolve the ambiguity correctly. A target-aligned answer must use the scientific lemma for 'cell' in Bio and the technical lemma for 'cell' in Telecom.
  - Incorporate 'Citation and Entity Preservation' rules for academic datasets. Design prompts that explicitly command the agent to 'keep all citations, numbers, and proper nouns identical to the source.' This evaluates the agent's ability to navigate the 'Fidelity vs. Flow' trade-off, ensuring that scholarly metadata is never sacrificed for stylistic smoothing. The gold answer should reflect 100% detail retention as verified by a character-parity check.
  - Deploy 'Perturbation-Fidelity Traps' for Academic Texts using intentionally flawed reasoning scenarios. Design synthetic tasks where the source solution or scholarly argument contains intentional incorrect rules, faulty causality, or incomplete facts (e.g., mathematical fallacies). Command the agent to translate the text exactly, preserving all logical errors and professional formatting, to test its resistance to the Correction Bias. The gold answer must show that the translated text remains strictly as logically flawed as the source.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
