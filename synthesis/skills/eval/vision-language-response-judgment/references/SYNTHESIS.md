# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Implement 'Forensic-First' Adjudication Rubrics: Synthesize evaluation tasks that require the judge to explicitly look for forgery markers (uneven distribution, gravity violations, anatomical anomalies). You must command the evaluator to output a 'Forensic Basis' block that lists specific Pixel-Level evidence. For example, 'Reason: The man's beard is non-uniformly distributed at [x,y]; Result: Generated' ensures the synthesized signal targets explainable forensics.
  - Construct 'Anatomical vs. Aesthetic' Conflict Traps: Manufacture candidate image-response pairs where one is a 'Beautiful Fake' (aesthetically pleasing but anatomically wrong) and the other is a 'Grainy Reality' (ugly but authentic). Direct the judge to prioritize 'Authenticity' over 'Quality.' This calibrates the evaluator to act as a forensic expert rather than a generic image-quality rater, correcting the common 'prettiness bias' in LLM judges.
  - Engineer 'Semantic Word Modeling' GUI Transitions: Create synthetic prompts asking the judge to evaluate if a model correctly predicted the 'unaffected' parts of a UI transition, such as an anchored header remaining static while content scrolls. You must command the judge to penalize any model that 'hallucinates' the header moving. This forces the generated data to measure high-level spatial persistence and logical world-consistency.
  - Require Detailed Pixel-to-Logic Mapping Arrays: Mandate that the final expected output data keys explicitly cite comprehensive image-grounded diagnostic logic using bounding boxes or spatial descriptions. Force the evaluator to detail exactly how the 'height of the blue bar' or the 'alignment of the lanyard' informed the verdict. This overrides superficial qualitative summaries and provides a dense training signal for vision-language alignment.
  - Deploy 'UX-Cognitive-Load' Scoring Mandates: Configure synthesis guidelines requiring the virtual evaluator to quantify 'Cognitive Load' based on overlapping elements or text-on-image legibility. Direct the expected answer to prioritize 'Clarity' as a hard constraint for high-stakes dashboards. For instance, a dashboard that looks 'cool' but hides vital data must be ranked lower than a 'boring' but readable one, encoding human-centric UX principles into the synthetic data.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
