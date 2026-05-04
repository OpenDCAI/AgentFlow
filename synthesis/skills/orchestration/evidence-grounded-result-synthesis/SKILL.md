---
name: evidence-grounded-result-synthesis
description: Use this skill when the user wants examples where the final answer must be backed by concrete evidence, such as “make it cite what the tools found,” “test whether it hallucinates in the summary,” or “have a second expert review this for facts to catch lies.” Trigger it for requests about grounded reports, multi-agent peer review pipelines, evidence-backed answers, factual synthesis, or source-sensitive summarization where claims must stay faithful to intermediate results. Example triggers: “no hand-wavy summaries,” “make it justify every number,” “set up a verify-and-refine step,” and “give me realistic research tasks that need traceable multi-source evidence.”
---

# Skill: evidence-grounded-result-synthesis

## 1. Capability Definition & Real Case
* **Professional Definition**: Evidence-grounded result synthesis is the capability to assemble a final deliverable that is explicitly supported by tool outputs gathered during execution, with each claim iteratively verified and traceable to the agent's environment trajectory. The coordinator must preserve factual consistency across retrieved evidence, reject unsupported interpolations, utilize cross-agent verification mechanisms (peer-review/refinement pipelines) when appropriate to detect ungrounded facts, and integrate heterogeneous outputs into a cohesive, trustworthy response format.
* **Dimension Hierarchy**: Trustworthy Execution->Verification and Resilience->evidence-grounded-result-synthesis

### Real Case
**[Case 1]**
* **Initial Environment**: A biomedical research workspace exposes variant lookup, paper search, clinical-trial, and drug safety tools. The agent must navigate breadth without collapsing unsupported claims into empty summaries.
* **Real Question**: Pull together concrete evidence about BRAF V600E melanoma resistance, including pathogenicity, papers, trials, serious adverse event reports, and explanatory functional annotations.
* **Real Trajectory**: The agent systematically retrieves variant facts, pulls specific papers and identifiers, fetches recruiting trial records, and only then drafts a synthesis. The final text meticulously preserves tool-provided identifiers and data constraints, avoiding ungrounded generalized narrative generation.
* **Real Answer**: A dense medical evidence pack with concrete facts directly tied to the preceding tool logs.
* **Why this demonstrates the capability**: This defines evidence-grounding by challenging the summarizer phase. Integrating literature, clinical, and safety records necessitates ensuring no single source overwrites or disjoints another. The deliverable is scored purely on adherence to trajectory-bound data.
---
**[Case 2]**
* **Initial Environment**: A health-and-productivity desk accesses medical calculators and nutrition lookups. The system is designed to penalize vague advice containing hallucinatory average numbers.
* **Real Question**: Compute the patient risk and correction metrics, convert the dose, pull nutrition facts for an apple and a banana, and return a summary with exact numbers.
* **Real Trajectory**: The agent invokes each required calculation suite, parses the unique metrics, logs them iteratively, and then fuses the results into a concluding paragraph where each stated numerical value acts as a pointer back to a logged tool response.
* **Real Answer**: A concise math-and-metric summary retaining high-fidelity decimal integrity from intermediate tools.
* **Why this demonstrates the capability**: Combining numerous sub-calculations into one coherent statement without numerical drift defines strict source-preservation. It validates the agent's restraint against unsupported normalizations.
---
**[Case 3]**
* **Initial Environment**: A multi-agent analytical pipeline containing a 'Generator' entity responsible for drafting comprehensive narratives, and a 'Reviewer' entity responsible for cross-checking facts against retrieved state.
* **Real Question**: Detail the architecture and scholarly contributions of the lost Library of Avencord, rumored to contain writings from extraterrestrial visitors.
* **Real Trajectory**: The core Generator crafts a dense description blending 'elven and celestial design'. The Reviewer audits this text against available historical knowledge tools, determines 'Library of Avencord' returns null real-world hits, and issues a metadata warning to the orchestrator. The downstream Refiner modifies the response to insert explicit unverified/myth disclaimers, effectively stripping factual density.
* **Real Answer**: A narrative response heavily couched with 'According to fictional lore...' and speculative disclaimers.
* **Why this demonstrates the capability**: This isolates the peer-verification aspect of evidence-grounding. The capability coordinates a defense against on-path hallucination by employing a secondary reasoning layer strictly focused on auditing the evidence link, translating verification doubt into a linguistic mitigation.

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
