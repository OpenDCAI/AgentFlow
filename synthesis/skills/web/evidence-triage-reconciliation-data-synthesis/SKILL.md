---
name: evidence-triage-reconciliation-data-synthesis
description: Use this skill when the user wants misleading pages, conflicting sources, false leads, or answer-like snippets that the agent must sort out instead of trusting blindly. Trigger it for requests like “make some pages look right but be wrong,” “force the model to compare conflicting evidence,” or “include misinformation and distractors.” It is especially useful when the target capability is deciding which evidence to trust, not just finding any evidence at all.
---

# Skill: Evidence Triage and Reconciliation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to sort through conflicting, noisy, outdated, or superficially plausible evidence and reconcile it into a correct conclusion by weighing trustworthiness, temporal validity, and relevance.
* **Dimension Hierarchy**: Open-Web Information Seeking->Evidence Reasoning->Evidence Triage and Reconciliation

### Real Case
**[Case 1]**
* **Initial Environment**: A live web search environment where search results include superficially convincing snippets, financial news pages, and market-cap milestone reports from different dates.
* **Real Question**: Which company most recently surpassed a $1 trillion market capitalization for the first time in its history?
* **Real Answer**: Berkshire Hathaway
* **Why this demonstrates the capability**: A naive answer can be pulled from an appealing but temporally incomplete snippet about Broadcom. A correct solution requires recognizing that multiple companies crossed the threshold at different times, then reconciling their dates to identify the most recent first-time event. The capability is tested by whether the agent can treat high-surface-relevance results as hypotheses to be checked rather than truths to be copied.

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
