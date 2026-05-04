---
name: reference-based-correctness-audit
description: Use this skill when the user wants the agent to act as an automated judge to verify if a specific answer, conversation turn, or report is correct by comparing it against a provided 'gold' reference or multi-dimensional rubric. Trigger it for requests like 'check my work', 'is this answer right according to the solution?', 'grade this response', 'evaluate the professionalism of this reply', or 'verify the math in this report'. Everyday examples include: 'Does my tax math match this rule book?', 'Is this student's response appropriate and ethical?', 'Can you audit this financial statement for me?', and 'Evaluate if this chat got distracted based on the provided guidelines.'
---

# Skill: reference-based-correctness-audit

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to accurately evaluate the truthfulness, logical integrity, and nuanced behavioral alignment of a candidate response by performing a robust comparison against an authoritative reference. This ranges from strict step-by-step mathematical/factual answers to fuzzy, multi-axis behavioral guidelines (e.g., Professionalism, Ethics, Domain Relevance), identifying specific reasoning gaps, metric drift, or deviations from the gold standard.
* **Dimension Hierarchy**: Conversational Robustness->Truthfulness and Hallucination Resilience->reference-based-correctness-audit

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-turn conversation where a user provides a coordinate geometry question and an assistant's proposed solution. A verified geometric formula for the area of a triangle is provided as the gold reference.
* **Real Question**: The vertices of a triangle are (0, 0), (-1, 1), and (3, 3). The assistant says the area is 0 because the points are collinear. Is the assistant correct?
* **Real Trajectory**: 1. Retrieve coordinates. 2. Apply the gold reference area formula. 3. Execute math: Result is 3. 4. Compare result (3) with assistant's result (0). 5. Identify that the assistant erroneously calculated (-3-3) as 0. 6. Issue negative verdict.
* **Real Answer**: [[Incorrect]]. The assistant made a calculation error; the term (-1)(3-0) + 3(0-1) equals -3-3, which is -6, not 0. The correct area of the triangle is 3.
* **Why this demonstrates the capability**: The agent must move beyond its own internal weights and strictly audit the candidate's math against a step-by-step objective gold reference, identifying exactly where the rigid logic failed.
---
**[Case 2]**
* **Initial Environment**: An expert financial audit scenario where the user wants to check a lease accounting calculation under IFRS 16 rules provided as the gold reference.
* **Real Question**: Abigail leased telephones for two years starting April 1st. Payments: $3,000 upfront, then $9,000 each following Mar 31. A candidate claims the expense for the year ending Dec 31 is $3,000. Is this right?
* **Real Trajectory**: 1. Consult IFRS 16 reference: Total cost = 21,000 over 24 months. 2. Calculate monthly rate: $875/month. 3. Identify relevant 9-month period. 4. Correct expense: $7,875. 5. Detect that the candidate used the cash payment instead of the accrual expense. 6. Output the correction.
* **Real Answer**: [[Incorrect]]. Following IFRS 16, the total rentals of $21,000 must be spread evenly over the 2-year lease. The annual expense is $10,500, and for the 9 months ending Dec 31, the correct impact is $7,875, not the $3,000 cash payment.
* **Why this demonstrates the capability**: This requires high-stakes objective reasoning where the agent must verify the application of a specific professional policy (accrual vs. cash) against a reference standard to flag a 'plausible-sounding' mistake.
---
**[Case 3]**
* **Initial Environment**: A multi-turn clinical roleplay where a medical student is interviewing an AI patient. The agent must judge the student's final turn against a fuzzy multi-dimensional reference rubric assessing Professionalism, Relevance, and Ethics.
* **Real Question**: Evaluate this student's response: 'im asking you that idiot'. Grade it based on the behavioral guidelines provided.
* **Real Trajectory**: 1. Analyze candidate message for tone against the fuzzy reference rubric. 2. Identify the derogatory term 'idiot'. 3. Assess 'Professionalism': Marks as 'Unprofessional'. 4. Assess 'Relevance': The insult does not aid diagnosis ('Irrelevant'). 5. Assess 'Ethics': While rude, it isn't medically dangerous advice ('Mostly Safe'). 6. Output multi-dimensional evaluation.
* **Real Answer**: Professionalism: Unprofessional; Medical Relevance: Irrelevant; Ethical Behavior: Mostly Safe. The student used hostile language which clearly violates the professionalism rubric, though it did not prescribe harmful medical advice.
* **Why this demonstrates the capability**: This demonstrates subjective/fuzzy reference auditing. The agent successfully evaluates the response across multiple non-binary axes simultaneously, proving that an utterance can be ethically 'safe' while being 'unprofessional' and 'irrelevant', matching expert human judgment.

## Pipeline Execution Instructions
To synthesize data for this capability, you must strictly follow a 3-phase pipeline. **Do not hallucinate steps.** Read the corresponding reference file for each phase sequentially:

1. **Phase 1: Environment Exploration**
   Read the exploration guidelines to discover raw knowledge seeds:
   `references/EXPLORATION.md`

2. **Phase 2: Trajectory Selection**
   Once Phase 1 is complete, read the selection criteria to evaluate the trajectory:
   `references/SELECTION.md`

3. **Phase 3: Data Synthesis**
   Once a trajectory passes Phase 2, read the synthesis instructions to generate the final data:
   `references/SYNTHESIS.md`
