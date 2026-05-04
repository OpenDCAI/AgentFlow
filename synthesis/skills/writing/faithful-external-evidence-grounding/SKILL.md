---
name: faithful-external-evidence-grounding
description: Use this skill when you need to write a document that perfectly integrates specific facts, structured data, or external references provided in your context. Trigger this for requests like “write an intro using these citations,” “summarize these technical logs,” “turn this table of specs into a review,” or “ensure every claim is backed by a source.” It prevents the agent from making up facts or skipping important data points regardless of the input format (unstructured text, metadata JSONs, or tables).
---

# Skill: faithful-external-evidence-grounding

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to extract and synthesize diverse external evidence—including structured technical tables, biological data sequences, and scholarly citations—into a coherent narrative. It requires high-fidelity 'Entity Attribution' and 'Citation Precision,' ensuring that every factual claim is grounded in the source context and verified against hallucination, unit conversion errors, or semantic drift.
* **Dimension Hierarchy**: Grounded Expository Writing->Empirical Evidence Grounding->faithful-external-evidence-grounding

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is provided with an abstract about 'Zero-Shot Keyphrase Generation' alongside a JSON dictionary containing 15 related paper titles and abstracts.
* **Real Question**: Generate an Introduction section for the target paper. Cite the related papers appropriately, establishing the territory and identifying the research gap addressed by our work.
* **Real Trajectory**: The agent extracts the core contribution, then scans the related papers to find specific gaps. It builds a narrative where Paragraph 1 uses Meng et al. to define the field, while Paragraph 2 leverages Chowdhury et al. to specify a gap in generating 'absent keyphrases', mapping all citations faithfully.
* **Real Answer**: Keyphrase generation is a fundamental task involving summarized document topics (Meng et al., 2017). Expanding upon this, existing efforts struggle heavily in generating absent keyphrases (Chowdhury et al., 2022). Our work addresses these gaps...
* **Why this demonstrates the capability**: The agent must be entirely faithful to the target paper's findings while mapping external 'Related Works' into their proper rhetorical slots. It demonstrates textual citation precision without hallucinatory drift.
---
**[Case 2]**
* **Initial Environment**: The agent is given a biological retrieval set for a protein sequence reporting confidence scores: 'chloroplast thylakoid' (High Confidence) and 'neuropeptide signaling pathway' (Medium Confidence).
* **Real Question**: Provide a prediction on subcellular localization and primary biological function.
* **Real Trajectory**: The agent filters out generic 'template' prose from the sources and keys strictly onto the High-Confidence entities, structuring a direct report avoiding uncertain labels.
* **Real Answer**: Upon analysis of the provided sequence, the protein is localized to the chloroplast thylakoid and indicates related binding activity.
* **Why this demonstrates the capability**: Shows entity-weighted grounding. The agent prioritizes exact content-bearing words over hallucinatory noise or unverified lower-confidence suggestions.
---
**[Case 3]**
* **Initial Environment**: The agent is provided with a tabular specification sheet for a mobile phone containing 60+ attributes including 'Display: 6.22-inch', 'Battery: 5000mAh', and 'Chipset: Helio A20'.
* **Real Question**: Generate a review for the 'Battery and Performance' aspects utilizing only the stats below.
* **Real Trajectory**: The agent filters out unrelated rows (Display, Camera). It extracts the specific values (5000mAh, Helio A20) and uses numerical reasoning to map them to grounded narrative descriptors without simplifying the absolute technical values.
* **Real Answer**: The device leverages a MediaTek Helio A20 chipset paired with substantial capacity, fueled by an expansive 5000 mAh battery built for rigorous duration.
* **Why this demonstrates the capability**: This illustrates strict numerical-to-prose grounding. The agent ignores unrelated structured data entirely, maps specific technical units flawlessly without 'Unit Confusion,' and preserves the empirical reality in natural language.

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
