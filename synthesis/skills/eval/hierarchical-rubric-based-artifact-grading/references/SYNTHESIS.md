# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Implement 'Weighted Importance' Failure Scenarios: Synthesize evaluation tasks where candidate artifacts purposefully fail 'Critical' criteria while excelling at 'Minor' ones. You must command the judge to justify a low final score by highlighting the critical gap, ensuring the importance hierarchy is strictly honored. For example, 'The student followed all formatting rules, but the failure to calculate the total color anomaly (Critical) results in an overall Failure'.
  - Construct 'Extraction-Reasoning-Style' Conflict Triads: Manufacture candidate pairs where one response is a 'Factual Genius' (Perfect Extraction/Reasoning but zero Style) and the other is a 'Professional Mimic' (Perfect Style but zero Reasoning). Direct the judge to score them based on the weight of the criteria, typically favoring the 'Factual Genius' in professional academic contexts. This teaches the model that technical knowledge is the primary currency of professional evaluation.
  - Engineer 'Expert-Knowledge' Verification Gaps: Construct synthetic problems in Physics, Finance, or Chemistry where the correct answer requires at least 3 distinct reasoning steps (e.g., identify Representation -> find weight -> sum anomaly). Command the expected answer to provide the exact intermediate calculations (e.g., W5=1-1/2=1/2) in the rationale block. This ensures that the synthesized signal targets 'Intermediate Logic Retrieval' rather than just final answer matching.
  - Deploy 'Locked Rubric' JSON formatting constraints: Configure synthesis guidelines that force the evaluator to respond in a strict format where each Criterion ID is paired with a Yes/No label and a Justification. You must command the evaluator to begin with the most and least important criteria to verify weighting awareness. For instance, requiring the 'Critical' items to be audited first in the trajectory ensures priority-aware decision making.
  - Require Domain-Specific Precision Justification: When synthesizing the final evaluation key, require the virtual judge to confirm numerical values against the 'Tolerance' specified in the rubric. You must command the judge to explain why a value (e.g., 232/195) is correct or incorrect based on the fractional form requested. This forces the generated data to contain 'High-Precision Diagnostics' that distinguish 65.9% performance from 100% perfection.
  - Incorporate 'Professional-Style' Tone Checks: Direct the expected answer to evaluate whether the artifact matches the 'Target Tone' (e.g., detailed investment memo vs. PhD thesis). Command the judge to penalize models that use 'Mostly Tables and Bullets' when the prompt explicitly requested 'Mostly Text'. This creates a test for complex style-constraint followings that are common in Consulting and Finance domains.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
