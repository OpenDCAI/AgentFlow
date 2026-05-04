---
name: contextual-lexical-sophistication-alignment
description: Use this skill when the writing must scale its complexity, vocabulary, and grammatical structures to strictly match a designated audience proficiency level (e.g., CEFR A1-C2, HSK 3-6, layperson vs. expert). Trigger it for requests like 'explain this medical report in plain English,' 'ensure the grammar is HSK 4 compatible,' 'make this sound more academically sophisticated,' or 'check this essay to simulate errors a non-native might make.' It seamlessly handles both vocabulary disambiguation for upscaling and standardized language acquisition modeling for downscaling.
---

# Skill: contextual-lexical-sophistication-alignment

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to continuously scale the lexical, syntactical, and conceptual complexity of a document to strictly align with designated audience echelons (e.g., standardized CEFR/HSK learner brackets vs. specialized expert audiences). This involves precise word-sense disambiguation, 'Staged-Grammar-Item Integration' for SLA modeling, and rigorous fact-set mapping to ensure translation across proficiency strata avoids epistemological oversimplification or out-of-bounds grammatical complexity.
* **Dimension Hierarchy**: Open-ended Writing Judgment->Audience-Targeted Register Scaling->contextual-lexical-sophistication-alignment

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is provided with an essay draft: 'It was tough on the worn out employees.' The environment lists possible meanings for the word 'tough' scaling from level A2 (physical durability) up to B2 (severity of rules/conditions).
* **Real Question**: Identify the intended meaning of 'tough' in this specific sentence context and determine the current proficiency level of the phrasing to evaluate if it needs upgrading.
* **Real Trajectory**: The agent identifies the target word 'tough' and parses its part-of-speech (adjective). It analyzes the semantic environment surrounding 'employees' and 'worn out.' It deliberately rejects the physical object baseline (A2) to lock onto the 'difficult/hardship' concept (B1), successfully resolving the polysemous ambiguity before scaling.
* **Real Answer**: In this context, 'tough' means 'difficult' or 'demanding', properly corresponding to a B1 proficiency level based on the contextual reference to workplace hardship.
* **Why this demonstrates the capability**: This perfectly models 'Polysemy Disambiguation.' The agent actively distinguishes between a common literal meaning and a contextualized complex usage, guaranteeing the complexity assessment accurately matches semantic intent rather than randomly grabbing the lowest-common-denominator frequency score.
---
**[Case 2]**
* **Initial Environment**: The agent is provided with a dense clinical trial report discussing risk stratification based on age distributions during an experimental cardiovascular intervention.
* **Real Question**: Simplify this result for a general patient audience: 'The study found that aspirin notably reduced the risk of myocardial infarction in patients over 50 but registered no statistically significant effect on younger demographics.'
* **Real Trajectory**: The agent extracts vital conditional triples: {Aspirin: reduces risk, Target: older than 50}. Assessing generalization boundaries, it explicitly vetoes the simpler statement 'Aspirin reduces the risk of heart attacks' due to 'Oversimplification.' It preserves the age constraint mandatorily during the simplification rewrite to prevent medical falsehoods.
* **Real Answer**: The study showed that taking aspirin can safely help prevent heart attacks in people over 50, but it did not seem to provide the same protective benefits for younger patients.
* **Why this demonstrates the capability**: This isolates 'Epistemic Faithfulness' during complexity down-scaling. By consciously preserving the stringent age qualifier rather than sacrificing it purely in the name of simpler word counts, the agent flawlessly mitigates 'Overgeneralization' risks.
---
**[Case 3]**
* **Initial Environment**: The agent is in a basic writing exercise environment for a level 3 language learner. The specific grammar focus is strictly constrained to the modal auxiliary verb 'dare' without advanced nested relative clauses.
* **Real Question**: Please write a sentence describing your experience attempting a difficult task, ensuring the grammatical complexity simulates a Level 3 beginner using the modal 'dare'.
* **Real Trajectory**: The agent identifies the Level 3 proficiency constraint and the specific grammar item anchor. It actively avoids overly complex subordinate clauses or high-density dependent structures that would exceed the beginner threshold. It constructs a simple, direct declarative sentence using the target word realistically.
* **Real Answer**: Even though the task was hard, I dared to try finishing it.
* **Why this demonstrates the capability**: The answer achieves 'Grammar Item Mastery and Complexity Capping.' It correctly utilizes a stage-appropriate construct in a grammatically simple framework, proving the model can artificially depress its syntactic complexity (average dependency distance) to match a realistic human milestone.

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
