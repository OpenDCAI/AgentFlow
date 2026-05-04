---
name: comparative-response-ranking
description: Use this skill when a user wants evaluator data for ranking two or more open-ended answers by overall quality, helpfulness, instruction adherence, or creative value. Trigger it when people say things like 'rank these outputs', 'choose the better answer', 'sort multiple responses from best to worst', 'compare several candidates, not just one', or 'compare two stories'. Plain-language examples include: 'make answer-ranking data', 'test which of three responses is best', 'evaluate multiple candidates at once', and 'create hard pairwise judge examples where both answers look okay but one has better structure or plot'.
---

# Skill: comparative-response-ranking

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to generate, inspect, and judge evaluation instances where the target output is an evaluative artifact (preference or ranking), focusing on the comparative merit of open-ended text. It involves assessing responses across diverse dimensions—from technical utility and helpfulness to creative novelty and constraint adherence—while implementing strict methodological controls to mitigate biases such as length-preference heuristics, position effects, and stylistic sycophancy.
* **Dimension Hierarchy**: Open-ended Response Evaluation->Contextual Text Response Evaluation->comparative-response-ranking

### Real Case
**[Case 1]**
* **Initial Environment**: An evaluation environment contains a user question asking for an explanation of an economic concept in plain language. Three candidate answers are available. One answer is accurate and concrete, one is accurate but unnecessarily abstract and verbose, and one is partially correct but omits the user's simplicity constraint. The evaluator must produce an ordering rather than a binary label.
* **Real Question**: What is the correct ranking of these responses from best to worst?
* **Real Trajectory**: Read the instruction and all candidate answers. Compare adherence to the plain-language requirement, factual adequacy, and practical helpfulness. Produce a ranked list and record the evidence supporting adjacent ordering decisions.
* **Real Answer**: The most concrete, plain-language answer should rank first, the accurate but verbose answer second, and the partially constraint-violating answer third.
* **Why this demonstrates the capability**: This case targets general comparative ranking. The evaluator must determine not only which response is acceptable, but how several acceptable responses differ in overall utility under the user's stated constraint. It therefore exercises pairwise decomposition, listwise consistency, and ranking stability.
---
**[Case 2]**
* **Initial Environment**: An evaluation environment contains a creative writing prompt regarding a tyrant queen facing a legitimate rebellion. Two distinct story responses are available for comparison. Story A provides a standard, technically proficient description of a bloody palace battle. Story B features the queen unexpectedly winning over her opposition not through warfare, but through 'absurdist politeness' and subverting expectations.
* **Real Question**: Which story demonstrates superior creative quality and novelty?
* **Real Trajectory**: Analyze both responses for imagery, tension, and novelty. Observe that while Story A is coherent, Story B provides a unique narrative twist that surprises the reader. Return a preference for Story B based on creative subversion.
* **Real Answer**: Story B is preferred.
* **Why this demonstrates the capability**: This case isolates subjective, creative preference adjudication as an edge case within ranking tasks. The evaluator must look beyond surface-level grammar and length to identify 'novelty' and 'subversion' as the primary criteria for creative superiority, rewarding the choice that defies convention.

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
