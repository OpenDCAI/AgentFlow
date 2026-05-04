---
name: context-aware-criteria-guided-revision
description: Use this skill when you need to fix a specific part of a document (like an intro or a method section) to make it follow professional 'best practices' or official guidelines. Trigger it for requests like 'make the motivation stronger,' 'clarify our main contribution,' 'check if this section still makes sense with the rest of the paper,' 'align this with the reviewer guide,' or 'fix the flow between these two chapters.' It is essential when a simple grammar check isn't enough and the writing needs to be more persuasive, logically sound, and consistent with the global context of the whole document.
---

# Skill: context-aware-criteria-guided-revision

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to perform instruction-driven, section-level revisions by aligning local text spans with explicit professional writing criteria while strictly preserving global document coherence. This involves 'Rationale-Driven Revision' where the agent identifies content gaps relative to academic or professional norms (e.g., ICLR reviewer guides) and 'Context-Aware Conditioning' where the revised output is explicitly constrained by the global narrative, terminology, and evidence found in the full paper draft (context T).
* **Dimension Hierarchy**: Revision Fidelity->Professional Standard Alignment->context-aware-criteria-guided-revision

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is provided with a full research paper draft regarding 'Generalizable Graph Learning' and the corresponding Abstract. The current Abstract contains a generic mention of experiments but lacks specific quantitative results and clear summaries of key innovations.
* **Real Question**: How can we effectively summarize our key innovations and their contributions to the field? What specific results and comparisons should we include to demonstrate the significance of our findings? Please also improve how the experiments reflect the effectiveness of the CVG framework.
* **Real Trajectory**: The agent first performs 'Context-Aware Modeling' by scanning the Evaluation section of the full paper. It extracts specific metrics: a '22% improvement in performance' and a '4.3x increase in search speed.' It then identifies the 'Key Innovations' criteria for Abstracts, noting the need to explicitly mention the Graph Information Bottleneck (GIB). Finally, it rewrites the abstract to replace vague 'demonstrated superiority' with these extracted technical anchors while ensuring the tone remains consistent with the Introduction's terminology.
* **Real Answer**: ...The key innovations of our CVG framework include Constrained Variational Generation and Graph Information Bottleneck (GIB) Optimization. Our experimental results demonstrate that CVG achieves a 22% improvement in tensor operator performance and a 4.3x increase in search speed compared to baselines, validating its effectiveness in mitigating distribution shifts.
* **Why this demonstrates the capability**: This case demonstrates the agent's ability to move beyond surface-level polishing to deep, context-aware revision. The agent had to reach into a different section of the document (Evaluation) to find the 'missing rationale' and specific evidence needed to satisfy the user's high-level instruction, proving it can maintain global coherence while improving local content.
---
**[Case 2]**
* **Initial Environment**: The agent is editing an Introduction section. The 'Motivation' paragraph is currently 'belabored' and lacks a specific explanation of the 'research gap' in Large Language Model (LLM) workflows.
* **Real Question**: Strengthen the motivation of our work by more clearly articulating the research gap. Make sure it sounds persuasive to a top-tier conference reviewer.
* **Real Trajectory**: The agent identifies the target paragraph as 'Introduction -> Motivation.' It cross-references the ICLR reviewer guide for 'argumantative rigor.' It finds that while the draft mentions LLMs are used for generation, it omits that they aren't 'feedback-centric' in revisions. The agent deletes the 'surface-level' sentences and inserts a specific claim about 'iterative revision-driven processes' not being supported by direct prompting.
* **Real Answer**: While LLMs are increasingly used for generating content, scientific writing is inherently iterative and revision-driven. Current prompting-based paradigms treat each interaction in isolation, failing to support the context-sensitive modeling required for high-quality scientific drafts.
* **Why this demonstrates the capability**: This case demonstrates 'Criteria-Guided Intent Alignment.' The agent used the 'Clarify Motivation' and 'Research Gap' criteria to transform a vague paragraph into a targeted, professional argument. It proves the agent can interpret high-level user 'intent' (be persuasive) through the lens of established professional norms.

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
