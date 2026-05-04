---
name: evidence-synthesis-and-insight-derivation
description: Use this skill when the writing task requires moving beyond a simple list of facts to produce reasoned insights, justify a verdict, or synthesize massive amounts of fragmented evidence. Trigger it for requests like 'write an investigative report,' 'analyze the trends,' 'give me a 360-degree view of these 100 documents,' 'explain why this claim is false based on the evidence,' or 'draft a legal reasoning section.' It perfectly resolves tasks where raw data must be explicitly mapped to overarching conclusions, truths, or rules.
---

# Skill: evidence-synthesis-and-insight-derivation

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to evaluate, synthesize, and logically map massive or heterogeneous external evidence—ranging from raw data to judicial facts or cross-domain research papers—into a structured analytical argument. This requires 'Inferential Synthesis,' where the model bridges the gap between raw unstructured information and higher-level conclusions, policy verdicts, or veracity assessments by making explicitly articulated causal or deductive connections without dropping critical factual pillars.
* **Dimension Hierarchy**: Grounded Expository Writing->Analytical and Logical Synthesis->evidence-synthesis-and-insight-derivation

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is provided with established facts regarding a lease dispute where a factory lacks a property ownership certificate. The rules provide that contracts for unapproved buildings are fundamentally void.
* **Real Question**: Compose the legal reasoning section explaining the court's analysis of the disputed lease contract.
* **Real Trajectory**: The agent extracts the established factual anchor (lack of construction approval) and explicitly maps it to the condition stated in the relevant legal provision. It constructs a deductive argument seamlessly bridging the physical fact to the resulting void contract.
* **Real Answer**: This Court finds that the factory leased by the defendant lacks a property ownership certificate. Consequently, according to current regulations, a lease contract involving an unapproved building is void; therefore, the Factory Lease Contract signed on July 11, 2010, is declared invalid.
* **Why this demonstrates the capability**: This illustrates 'Fact-to-Rule Mapping.' The model integrates physical evidence with governing principles to create an unavoidable logical deduction, proving its capacity for rigorous legal and policy-based synthesis.
---
**[Case 2]**
* **Initial Environment**: The agent receives a viral claim that CO2 rise is purely natural, alongside scientific records detailing atmospheric isotopic signatures and fossil fuel emission volumes.
* **Real Question**: Generate an article justifying the verdict that the claim 'Rising CO2 levels are entirely natural and not caused by human activity' is False.
* **Real Trajectory**: The agent calculates that fossil fuel production directly correlates with the specific anthropogenic isotopic signatures found in the atmosphere. It addresses the likely interpretation that 'natural cycles exist' but synthesizes the data to refute the viral claim decisively.
* **Real Answer**: While natural processes release CO2, scientific analysis of carbon isotopes confirms the current atmospheric addition bears the signature of fossil fuels, not volcanic sources. This data synthesizes to prove the claim False; understanding this distinction is vital because natural cycles cannot account for the rapid rate of contemporary warming.
* **Why this demonstrates the capability**: This highlights 'Veracity Justification.' A summary would merely list statistics, but this output actively synthesizes the statistics into a causal, argumentative proof that directly resolves the veracity of a specific human claim.
---
**[Case 3]**
* **Initial Environment**: The agent is provided with an Oracle Context containing the summarized full text of 120 reference papers concerning Large Language Model capabilities, accompanied by a mandate to categorize these into specific methodology approaches.
* **Real Question**: Based on the provided reference papers, give me a comprehensive survey on the topic of reasoning models. Classify them structurally into: 1. Shorten CoT, 2. Develop SLMs, 3. Enhance Decoding.
* **Real Trajectory**: The agent constructs an 'Intellectual Skeleton' mapping the massive bibliography to the three categories. It executes a saturation-scan, aggregating at least 8 distinct method names per cluster instead of providing a sparse list, ensuring sweeping high-volume factual consolidation.
* **Real Answer**: Reasoning Models: A Survey. ...A key trend involves developing SLMs via distillation. For example, CoT-KD (Magister et al., 2022) pioneered reasoning capability distillation. Furthermore, Open-RS employs reinforcement learning to build reasoning traces. To enhance decoding, Tree-of-Thought extends linear chains...
* **Why this demonstrates the capability**: This illustrates 'Comprehensive Factual Consolidation.' The agent successfully manages extreme input volume, avoiding 'Synthesis Effort Collapse' by ensuring a high density of specific atomic facts and entity names persist into the final deduced categories.

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
