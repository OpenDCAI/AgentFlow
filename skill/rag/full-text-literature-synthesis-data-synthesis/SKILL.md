---
name: full-text-literature-synthesis-data-synthesis
description: Use this skill when the user wants questions that feel like paper-reading, literature review, recent findings, or 'you have to open the paper, not just the abstract'. Trigger it for requests like 'make it retrieve scientific papers', 'ask about a new result from the literature', 'force source-backed answering', or 'reward saying unsure when the paper isn't enough'. This skill is for bounded scientific corpora and full-text evidence use.
---

# Skill: Full-Text Literature Synthesis

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to answer scientific questions by retrieving full-text papers, extracting evidence from relevant sections beyond superficial summaries, and synthesizing a cited answer with calibrated uncertainty when the evidence remains insufficient. The capability combines literature retrieval, section-level evidence gathering, and answer calibration.
* **Dimension Hierarchy**: Specialized Knowledge Navigation->Corpus-Specific Retrieval & Reasoning->Full-Text Literature Synthesis

### Real Case
**[Case 1]**
* **Initial Environment**: A bounded corpus of recent biomedical full-text papers published after common model cutoff dates. The decisive evidence is inside a paper’s body rather than safely recoverable from an abstract-only summary.
* **Real Question**: Has anyone performed a base editing screen against splice sites in CD33 before?
* **Real Answer**: Yes
* **Why this demonstrates the capability**: The question targets a recent scientific finding and is intentionally difficult to answer from latent memory alone. The agent must retrieve the right paper, inspect relevant full-text sections, and synthesize a bounded answer. This is the core retrieval-and-synthesis pattern for literature RAG.
---
**[Case 2]**
* **Initial Environment**: A bounded recent-paper corpus in neuroscience. The relevant evidence compares laminar patterns between two neuron groups and must be extracted from the paper content.
* **Real Question**: How diffuse are the laminar patterns of the axonal terminations of lower Layer 5/Layer 6 intratelencephalic neurons compared to Layer 2-4 intratelencephalic neurons in mouse cortex?
* **Real Answer**: More diffuse
* **Why this demonstrates the capability**: This case tests whether the agent can retrieve specialized literature and read enough of the paper to answer a fine-grained comparative question. The answer is compact, but the supporting evidence is not a generic factoid. The capability is therefore full-text scientific synthesis rather than keyword lookup.
---
**[Case 3]**
* **Initial Environment**: A bounded recent-paper corpus in immunology or molecular biology. The question asks which listed glycoRNA does not display a specified increase under stimulation conditions.
* **Real Question**: Which of these glycoRNAs does NOT show an increase in M0 macrophages upon stimulation with LPS: U1, U35a, Y5 or U8?
* **Real Answer**: U8
* **Why this demonstrates the capability**: The agent must retrieve the correct paper, inspect the relevant result, and resist plausible distractor options. The question is closed-form, but the underlying skill is still full-text evidence discovery and careful answer selection. This makes it a strong calibration case for literature-grounded RAG.

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
