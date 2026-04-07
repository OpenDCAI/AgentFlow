---
name: scientific-threshold-and-context-inference-data-synthesis
description: Use this skill when the user wants SQL data where the agent must infer hidden expert rules rather than just read column names. Trigger it for requests like “make the model use an unstated threshold”, “the question should rely on domain conventions”, “approved should not just mean a boolean flag”, or “it should need scientific background to write the SQL correctly.” Example trigger: “The hard part should be an implied threshold.” Example trigger: “I want expert-rule SQL, not literal schema matching.” Example trigger: “The model should have to infer what counts as significant or approved.”
---

# Skill: Scientific Threshold and Context Inference

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to operationalize implicit domain conventions that are not explicitly encoded in the schema, such as significance thresholds, effect directionality, trial-phase interpretation, or approval logic that depends on external scientific context.
* **Dimension Hierarchy**: Query Reasoning->Domain-Constrained Semantics->Scientific Threshold and Context Inference

### Real Case
**[Case 1]**
* **Initial Environment**: A biomedical BigQuery database stores GWAS summary statistics including p-values, beta coefficients, gene mappings, and disease labels. The schema does not itself encode the phrase “increase the risk” as a ready-made field.
* **Real Question**: Are there any C9orf72 gene mutations that increase the risk of Parkinson’s disease?
* **Real Trajectory**: Filter the Parkinson’s GWAS table to the target gene, apply the genome-wide significance threshold, constrain the beta direction to positive effect, and then inspect the remaining variants.
* **Real Answer**: A correct SQL answer requires applying both p-value and directionality conventions rather than merely filtering on the gene name.
* **Why this demonstrates the capability**: Nothing in the natural-language question explicitly says “p < 5e-08” or “beta > 0”. The agent must know that “increase the risk” implies positive effect direction and that significant association implies a strict threshold. This is therefore a canonical threshold-and-context inference task.

---
**[Case 2]**
* **Initial Environment**: The same biomedical environment links genes, diseases, drugs, and trial or approval metadata. The user asks about intervention relevance rather than a raw join result.
* **Real Question**: What drugs target genes up-regulated in Parkinson’s disease?
* **Real Answer**: The correct answer requires identifying the relevant genes first, then using contextual drug-target and status information to decide which candidates qualify.
* **Why this demonstrates the capability**: The challenge is not just joining drug and gene tables. The phrase “target genes up-regulated in Parkinson’s disease” presupposes a domain-aware interpretation of what biological evidence and status filters are relevant. The agent must therefore inject context that is partly outside bare schema matching.

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
