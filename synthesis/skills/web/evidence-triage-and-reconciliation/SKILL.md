---
name: evidence triage and reconciliation
description: Use this skill to verify the truthfulness of web-based claims, handle conflicting reports, and self-correct agent failures by decomposing complex answers into verifiable sub-questions. Trigger it for requests like “is this statement true?”, “fact-check this,” “verify the findings,” or “verify if the previous answer makes sense.” It is essential for avoiding 'premature conclusions' and 'hallucinated claims' by leveraging verification asymmetry—breaking a major claim into atomic 'Yes/No' sub-tasks that are easier to ground in primary documentation than the initial open-ended query.
---

# Skill: evidence triage and reconciliation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform high-stakes veracity verification and iterative self-evolution by decomposing complex, unverified claims into 'Atomic Rubric Seeds' and simpler sub-questions. This method exploits the asymmetry of verification—where checking a specific fact is computationally and logically easier than generating a holistic research answer—to identify known agent failure modes such as consulting wrong evidence, misinterpreting instructions, or making inferential leaps, ultimately reconciling these signals into a structured, corrective verdict.
* **Dimension Hierarchy**: Open-Web Information Seeking->Evidence Reasoning->evidence triage and reconciliation

### Real Case
**[Case 1]**
* **Initial Environment**: A web browser with access to global academic profiles, publication repositories (Google Scholar, DBLP), and university directory pages.
* **Real Question**: Identify the earliest peer-reviewed publication of researcher X and provide the exact title and year.
* **Real Trajectory**: 1. Search for 'researcher X publications' and land on a secondary summary blog. 2. Extract a title from 2012 cited in the blog. 3. Decompose verification: 'Does Researcher X have any papers before 2012 listed on their official university faculty page?' 4. Search 'Researcher X faculty profile'. 5. Retrieve an earlier technical report from 2008 on the CV. 6. Reconcile: The blog was an incomplete secondary source; the faculty page provides the primary ground truth.
* **Real Answer**: Initial answer: [2012 Paper]; Corrected answer: [2008 Paper Title]
* **Why this demonstrates the capability**: This case demonstrates the 'Finding Sources' failure mode from the baseline taxonomy, where agents often rely on generic searches or secondary sources. By applying 'Decomposition-Based Verification,' the agent identifies the risk of starting from a secondary source and issues a targeted sub-query to find the primary CV, preventing a premature and incorrect conclusion.
---
**[Case 2]**
* **Initial Environment**: A web browser viewing technical documentation portals and hardware specification matrices for semiconductor components.
* **Real Question**: What is the recorded Curie temperature for the 3:1 superlattice of LaNiO3/LaFeO3 mentioned in CAS research papers?
* **Real Trajectory**: 1. Identify common papers on CAS ferromagnetism. 2. Locate a potential candidate: 'Ferromagnetism in LaFeO3/LaNiO3 Superlattices'. 3. Break into verification sub-questions: 'Does this specific paper contain a segment on 3:1 superlattices?' and 'What is the numerical value associated with Tc in the results table for this config?' 4. Execute high-precision extraction on the HTML table. 5. Confirm through logic that the extracted 589K value specifically matches the 3:1 ratio described.
* **Real Answer**: 589K
* **Why this demonstrates the capability**: This demonstrates 'Recall Accuracy' and 'Decomposed Fact-Checking' in complex technical environments. It avoids 'Hallucinated or Overconfident Claims' by forcing the agent to verify atomic parameters (Tc, ratio, paper title) as independent logical predicates before formulating the final terminal answer.

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
