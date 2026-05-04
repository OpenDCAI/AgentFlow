---
name: hierarchical-rubric-based-artifact-grading
description: Use this skill when you need to evaluate complex professional artifacts—such as physics proofs, financial investment memos, chemistry reports, or consulting strategies—against expert-level, multi-dimensional rubrics. It is triggered by requests like 'grade this professional report using expert criteria', 'apply weighted rubrics to this PhD-level paper', 'evaluate this MBA memo for reasoning and extraction quality', or 'use a locked checklist to score professional knowledge'. Ordinary users might say 'check if the physics math is right', 'see if the business plan covers all the risks', or 'score this report based on the official expert rules'.
---

# Skill: hierarchical-rubric-based-artifact-grading

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability involves the deterministic execution of analytical, multi-dimensional rubrics—often requiring PhD or MBA-level professional knowledge—through a 'Locked Rubric' and 'Evidence-Anchored' protocol. It categorizes evaluation criteria into functional domains (Extraction vs. Reasoning vs. Style), assigns importance weights (Critical, Major, Minor), and enforces verifiability through mandatory evidence anchors that link scores to specific text fragments, ensuring that evaluations of complex professional reports are grounded, objective, and resistant to stylistic biases.
* **Dimension Hierarchy**: Structured Evidence Evaluation->Evidence-and-Verifier-Grounded Evaluation->hierarchical-rubric-based-artifact-grading

### Real Case
**[Case 1]**
* **Initial Environment**: An evaluation environment for KSVZ-style Axion models containing a theoretical physics prompt regarding heavy vector-like fermions with specific Peccei-Quinn (PQ) charges and Standard Model gauge quantum numbers.
* **Real Question**: Compute the ratio E/N (electromagnetic to color anomaly coefficients) for five heavy vector-like fermions given their representations and PQ charges, provided in the lowest-term fractional form.
* **Real Trajectory**: The evaluator parses the five fermions and their indices. It calculates the individual color anomaly contributions (e.g., N1 through N5) and sums them to obtain the total color anomaly N = 65/4. It then calculates the electromagnetic anomaly to find E = 58/3. Finally, it computes the ratio E/N = (58/3)/(65/4) and simplifies it to 232/195, verifying each calculation step against a Reasoning rubric.
* **Real Answer**: E/N = 232/195
* **Why this demonstrates the capability**: This case demonstrates 'Causal/Mathematical Correctness' and 'Completeness of Reasoning' within the physics domain. The evaluator cannot just check the final answer; it must follow a multi-step mathematical hierarchy where intermediate variables (N and E) must be extracted and calculated correctly according to specific Dynkin indices and PQ weights.
---
**[Case 2]**
* **Initial Environment**: A corporate investment evaluation sandbox containing a prompt about the Global Alliance for Vaccination and Immunization (GAVI) and the International Finance Facility for Immunization (IFFIm) raising money on capital markets.
* **Real Question**: How did IFFIm apply securitization, what factors made it possible to raise money on capital markets, and should IFFIm be viewed as a blueprint for other social/environmental challenges?
* **Real Trajectory**: The evaluator analyzes an investment memo response. It checks the Extraction rubric to verify if the model stated that a breach of IFFIm's liquidity policy negatively impacts its rating. It moves to the Reasoning rubric to confirm the model argued that vaccines are cost-effective health investments. Finally, it assesses the Style rubric to ensure the memo is presented in a structured consulting framework without using excessive bullet points.
* **Real Answer**: PASS (Logical Validity: High; Formatting: High; Extraction: Correct)
* **Why this demonstrates the capability**: This illustrates 'Multi-Dimensional Domain Adjudication.' The capability is exercised by simultaneously checking information extraction (liquidity policy), logical reasoning (cost-effectiveness justification), and stylistic adherence (investment memo format) across a complex business context.
---
**[Case 3]**
* **Initial Environment**: A chemistry PhD-level sandbox focusing on acid-base reactions in commercial electroplating applications. The environment includes a mixture of 100 mL acetic acid (0.5 M) and formic acid (0.1 M).
* **Real Question**: Calculate the volume of 0.5 M NaOH required to reach the point where the two conjugate bases have equal concentrations, and calculate the pH at the point where both acids are neutralized.
* **Real Trajectory**: The evaluator identifies the multi-step titration logic. For the neutralization point, it calculates the salt concentrations (acetate and formate) and applies the hydrolysis equilibrium. It checks the Reasoning rubric which dictates the pH should be 9.05 +/- 0.05. It then checks the Style rubric to ensure the molecular weights used in any documentation are rounded to exactly 1 decimal place as requested.
* **Real Answer**: Neutralization pH: 9.05; Style check: SUCCESS (1 decimal place used).
* **Why this demonstrates the capability**: This demonstrates 'Hierarchical Factual Verification' in an expert scientific setting. It combines 'Extraction' of concentration values with 'Reasoning' based on complex coupled equilibria and 'Style' constraints regarding numerical precision.

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
