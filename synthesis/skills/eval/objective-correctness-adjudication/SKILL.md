---
name: objective-correctness-adjudication
description: Use this skill when verifying if an answer is factually, mathematically, or logically correct against references, gold-standard contexts, verifiers, or massive source texts. Trigger it when users ask to 'check if the bot used the right formula', 'verify the math logic', 'find if the assistant hallucinated a detail', 'verify factuality in this 100-page document', or 'verify if the Telugu math solution is actually correct'.
---

# Skill: objective-correctness-adjudication

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to assess objective factual, mathematical, and logical correctness through verifiable grounding. This involves sequential multi-step deduction verification (Formula -> Variable -> Calculation), detecting factual precision failures in extreme long-context source windows (128K+ tokens), and utilizing native-script logic isolation to overcome 'intention-repetition gaps' in low-resource languages (LRL). The judge systematically prioritizes absolute truth logic while simultaneously resisting formatting artifacts, syntactic translation errors, or 'length/verbosity' biases.
* **Dimension Hierarchy**: Structured Evidence Evaluation->Evidence-and-Verifier-Grounded Evaluation->objective-correctness-adjudication

### Real Case
**[Case 1]**
* **Initial Environment**: A clinical assessment evaluation containing patient lab records and a requested mathematical equation for sodium correction. The assistant provides a final numeric answer that is incorrect.
* **Real Question**: What is the corrected sodium concentration at admission, and is the numeric calculation mathematically and scientifically correct?
* **Real Trajectory**: The evaluator executes a step-by-step verification pipeline. Step 1: Verify the formula selection. It finds the model used an incorrect standard formula. Step 2: Extract variables. Step 3: Calculation. Step 4: Numerical tolerance limit comparison based on decimal depth. It records a failure directly at Step 1.
* **Real Answer**: Result: Incorrect. Reason: Formula Hallucination. The mathematical steps executed based on the wrong formula are irrelevant since the base logic is factually incorrect.
* **Why this demonstrates the capability**: This demonstrates short-form, step-wise logical correctness adjudication. It verifies rigid mathematical truths and identifies exactly where a computational or logic sequence collapses, ensuring the judge does not just check the final number.
---
**[Case 2]**
* **Initial Environment**: A massive 40-page, 100k+ token scientific document containing buried data points regarding seismic activities, acting as the 'needle in a haystack'. A candidate response is generated that quotes the right depth but hallucinates medical terms not found in the context.
* **Real Question**: Does the candidate successfully and faithfully answer the query utilizing ONLY the provided massive text source?
* **Real Trajectory**: The evaluator scans the massive context chunk corresponding to the answer. It acknowledges that the answer is extremely long and fluent. However, it cross-references the medical claims with the 100k document and identifies a strict 'context-ignorance' hallucination. It actively penalizes the longer response for failing the grounding boundary constraint.
* **Real Answer**: Score: 2/10. The answer is lengthy but incorrect because it hallucinates proteins and details not mentioned anywhere in the referenced geology text.
* **Why this demonstrates the capability**: This covers Long-Context Consistency and mitigates 'Length-Bias' (pro-prose) phenomena where models reward long answers regardless of factual reality. It isolates critical fact retrieval execution across massive contextual windows.
---
**[Case 3]**
* **Initial Environment**: A mathematical correctness verification sandbox for grade-school level word problems written entirely in a low-resource language (Telugu). The problem involves tracking item counts with specific conditional loss parameters before a final calculation.
* **Real Question**: Verify if the provided solution (40.0) correctly solves the math problem given the exact Telugu text constraints.
* **Real Trajectory**: The evaluator executes its reasoning verification sequence directly in the Telugu script to avoid semantic loss common in machine translation. It parses the crucial native phrase indicating 5 items were lost prior to the comparison. It checks the algebraic relationship: Bobby = 3 * 15 - 5 = 40. It finds the candidate correctly deduced this hidden state.
* **Real Answer**: Result: Correct. The solution accurately reflects the step-wise deduction required by the native text logic.
* **Why this demonstrates the capability**: This illustrates 'Low-Resource/Multilingual Reasoning Grounding'. It proves the objective evaluator can maintain strict logical correctness in non-English contexts, parsing operators and algebraic constraints directly from native linguistics rather than falling back on lossy translations.

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
