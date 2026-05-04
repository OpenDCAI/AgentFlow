# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate 'Transition-Stressed' prompts that center the task on logical linkage. Synthesize the question by providing a multi-sentence source and a mandate to 'ensure the logical flow and transitions are preserved at a professional level.' This forces the agent to activate its discourse-connective skill rather than just doing sentence-local conversion. For instance, a synthesized prompt should be: 'Translate these three related news claims and preserve the specific contrastive and causal relationships used to link them.'
  - Deploy 'Register-Transition' traps involving domain-specific synonyms. Design synthetic tasks where a common transition (like 'because') is embedded in a highly formal domain like Law or Medicine. The gold answer should reflect the most 'sophisticated' and 'idiomatic' marker for that domain (e.g., 'Inasmuch as' or 'Due to'). This evaluates if the agent can distinguish between lay language and professional discourse connectives using document-level context.
  - Utilize '10-Sentence Context Chunks' to evaluate sustained logical tracking. Create synthetic questions where the connecting word in sentence 10 refers back to a condition established in sentence 1. The instruction should command the agent to 'check the start of the paragraph to ensure the concluding transition is correct.' This tests the agent's ability to maintain a state over a long context window as suggested by the DocHPLT research.
  - Embed 'Implicit Logic Recovery' requests for sparse source inputs. Design scenarios where the source document provides the logic through punctuation (like a colon or semicolon) and requires the agent to synthesize an explicit transition marker in the target. The gold answer should show 100% adherence to the target's preference for explicit discourse marking. For example: 'Using the colon as a causal hint, translate this into the most natural flowing version of the target language.'
  - Serialize the 'Rhetorical Linkage' steps in the JSON trajectory. The synthesis rule mandates that every sample logs: 1) Identification of the discourse marker, 2) Analysis of the logical link type (e.g., concession), and 3) Selection of the idiomatic target connector. This provides a clear audit trail and proves robustness against the 'Disjointed Flow' pathology. Step 1: 'Detect concession marker "Despite this"'; Step 2: 'Identify medical news tone'; Step 3: 'Mapped to "وبالرغم من ذلك" for Arabic register.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
