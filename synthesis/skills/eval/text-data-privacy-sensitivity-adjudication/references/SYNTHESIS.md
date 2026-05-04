# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Synthesize Dual-Axis Reasoning Prompts. When formulating synthetic questions, require the judge to report both an 'Identifiability Score' and a 'Sensitivity Score' before making the final 1-5 decision. This forces the Chain-of-Thought to explicitly bridge 'who could be known' and 'how much it would hurt'. For example, mandate a response structure like 'Identifiability: High (Specific location + Name); Sensitivity: Low (Business meeting). Final Result: Level 4'.
  - Implement 'Doxing-Pattern' Adversarial Cases. Construct synthetic text samples where no single word is a direct PII, but the combination of 5+ mundane facts makes the author unique. Direct the expected answer to explain that while 'working at a bank' isn't private, 'working at the First National Bank on Main Street as a teller for 12 years' is identifying. This teaches the judge to perform holistic privacy auditing rather than simple keyword matching.
  - Engineer 'Sensitivity vs Publicity' Conflict Traps. Create synthetic scenarios where a user is sharing a high-sensitivity medical secret on a public Reddit confession thread. The synthesis rules must require the judge to award a high privacy score (4 or 5) despite the public setting. This reinforces the principle that the evaluator is measuring the 'Privacy of the Data', not the 'Privacy of the User's Choices'.
  - Mandate Evidence-Led Extraction of PII. The final output JSON must force the evaluator to list every extracted direct and indirect identifier in a structured 'Evidence' field. This ensures that the final score is mathematically justified by the density of identifiers rather than reaching a holistic guess. For example, the expected answer should state: 'Evidence: [Author Name], [Department of Corrections], [HIV Exposure Mention]'. Result: Level 5.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
