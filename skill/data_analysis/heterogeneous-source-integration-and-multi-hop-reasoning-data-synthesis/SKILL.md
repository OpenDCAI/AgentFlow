---
name: heterogeneous-source-integration-and-multi-hop-reasoning-data-synthesis
description: Use this skill when the user wants “connect-the-dots” analytics over several files. Trigger it for requests such as “make it combine different sources,” “make the answer depend on more than one table and a document,” “make it join clues across files,” or “ask something that needs several hops before the final number appears.” Plain-language examples: “Give me a question that can’t be solved from one sheet,” “make it use multiple files plus notes,” “make it chain together several small findings.”
---

# Skill: Heterogeneous Source Integration And Multi-Hop Reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to answer an analytical question by combining evidence across multiple heterogeneous sources, such as CSV files, JSON files, notebooks, and unstructured text, where no single artifact contains the answer directly. It requires multi-hop linking, intermediate computations, and disciplined propagation of constraints across sources.
* **Dimension Hierarchy**: Data Grounding->Contextual Knowledge Grounding->heterogeneous source integration and multi-hop reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: Structured transaction data, fee data, and supporting documentation are all available. The answer requires combining multiple sources rather than reading a single file.
* **Real Question**: Which card scheme had the highest average fraud rate in 2023?
* **Real Trajectory**: Load the payments data; identify which table stores fraud events and which field encodes card scheme; filter to the 2023 slice; compute fraud rate per scheme using the documented definition of rate; compare the scheme-level results; report the top scheme.
* **Why this demonstrates the capability**: The question cannot be answered by a single lookup because the agent must align entity definitions, time filters, and fraud calculations across multiple sources. Intermediate computation is necessary before the ranking step. The case therefore captures true multi-hop data reasoning.

---
**[Case 2]**
* **Initial Environment**: An empty notebook is provided together with several biological data files and a preconfigured analysis environment. The answer depends on comparing differential-expression results across multiple strains.
* **Real Question**: How many genes are uniquely differentially expressed in strain 98 but not in either of strains 97 or 99?
* **Real Trajectory**: List the workspace; load the differential-expression outputs for all three strains; extract the gene sets that satisfy the relevant significance criteria; compute the set difference for strain 98 against strains 97 and 99; count the remaining genes; submit the final answer.
* **Why this demonstrates the capability**: No file directly stores the requested count. The agent must integrate results from several related analyses, maintain consistent selection criteria, and perform set-based reasoning. This is a classic multi-hop analytical trajectory over heterogeneous scientific outputs.

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
