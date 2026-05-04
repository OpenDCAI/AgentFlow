---
name: epistemic-vigilance-and-source-integrity
description: Use this skill when you need to write or verify a document where every claim MUST be anchored to a specific, ID-verified source and checked for boundary-condition accuracy. Trigger it for requests like “verify these technical findings,” “ensure no fake citations are included,” “check the boundary conditions of this device design,” or “map every claim to a retrieved span.” It is critical for enforcing ‘closed-world citation’ (abstaining rather than guessing) and auditing the formal alignment between retrieved evidence and final claims.
---

# Skill: epistemic-vigilance-and-source-integrity

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to perform systemic ‘epistemic vigilance’ by critical analysis of information provenance and the enforcement of a deterministic citation pipeline. This involves auditing sources across four axes: Motivational Bias, Temporal Validity, Objective Authority, and Bibliographic Integrity (verifying metadata against authoritative graphs). Furthermore, it requires ‘Closed-World Citation Alignment,’ where the agent strictly constrains generation to retrieved evidence IDs, performs boundary-condition verification (identifying where evidence fails to cover high-stakes technical specs), and emits an auditable claim-to-evidence map consisting of verified spans and offsets.
* **Dimension Hierarchy**: Grounded Expository Writing->Source Credibility and Vigilance->epistemic-vigilance-and-source-integrity

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is provided with a drafting interface and a research context containing three retrieved papers on thin-film lithium niobate (TFLN) modulators. One paper specifies a VπL product of 2.2 V·cm; a second paper discusses cladding but lacks numerical loss data for that specific configuration.
* **Real Question**: Draft a performance summary for LiNbO3 modulators including VπL and insertion loss. Ensure that if a specific metric is missing from the retrieved set, you explicitly flag it as a boundary-condition gap rather than estimating based on general knowledge.
* **Real Trajectory**: The agent canonicalizes the retrieved papers using DOIs. It extracts the 2.2 V·cm metric. When moving to insertion loss, it checks the 'Evidence Table' and finds no ID-verified span for that numerical value. Instead of quoting a 'typical' value (hallucination), it writes that while VπL is documented at 2.2 V·cm, the specific insertion loss for this cladding remains a boundary-condition gap in the current evidence.
* **Real Answer**: Recent benchmarks for TFLN modulators demonstrate a VπL product of 2.2 V·cm. However, the retrieved literature provides no specific insertion loss metrics for p-cladding configurations, representing a critical boundary-condition gap in the available technical evidence.
* **Why this demonstrates the capability**: This case demonstrates 'Closed-World Citation' and 'Boundary-Condition Awareness.' The agent resists 'Parametric Memory Hallucination' (guessing a loss value) by checking its internal evidence table. It correctly identifies a 'Knowledge Gap' and communicates it as a limitation, which is the hallmark of hallucination-resistant research writing.
---
**[Case 2]**
* **Initial Environment**: The agent is provided with an academic draft discussing LLM attention mechanisms and is tasked with verifying the references for a peer-review check.
* **Real Question**: Check the following citation for bibliographic accuracy: 'A. Vaswani et al., 2017, "How to effectively use attention", NeurIPS.'
* **Real Trajectory**: The agent extracts the citation fields (Title: How to effectively use attention; Author: Vaswani; Venue: NeurIPS; Year: 2017). It queries authoritative scholarly records and finds the canonical paper with identical Authors, Year, and Venue, but the title is actually 'Attention is all you need'. It flags a 'Title Mismatch' error.
* **Real Answer**: Error detected: [Title Mismatch]. The citation claims the title is 'How to effectively use attention', but the authoritative record for Vaswani et al. (2017) at NeurIPS is 'Attention is all you need'.
* **Why this demonstrates the capability**: This demonstrates 'Bibliographic Integrity Audit.' The agent identifies a subtle semantic drift in the title where the reference is plausible and the paper exists, but the specific title metadata is incorrect, requiring cross-referencing against a ground-truth scholarly graph.
---
**[Case 3]**
* **Initial Environment**: The agent receives a viral claim that CO2 rise is purely natural, alongside scientific records detailing atmospheric isotopic signatures and fossil fuel emission volumes.
* **Real Question**: Generate an article justifying the verdict that the claim 'Rising CO2 levels are entirely natural and not caused by human activity' is False.
* **Real Trajectory**: The agent calculates that fossil fuel production directly correlates with the specific anthropogenic isotopic signatures found in the atmosphere. It addresses the likely interpretation that 'natural cycles exist' but synthesizes the data to refute the viral claim decisively.
* **Real Answer**: While natural processes release CO2, scientific analysis of carbon isotopes confirms the current atmospheric addition bears the signature of fossil fuels, not volcanic sources. This data synthesizes to prove the claim False; understanding this distinction is vital because natural cycles cannot account for the rapid rate of contemporary warming.
* **Why this demonstrates the capability**: This highlights 'Veracity Justification.' A summary would merely list statistics, but this output actively synthesizes the statistics into a causal, argumentative proof that directly resolves the veracity of a specific human claim.

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
