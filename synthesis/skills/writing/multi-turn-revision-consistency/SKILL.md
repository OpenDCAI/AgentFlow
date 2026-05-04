---
name: multi-turn-revision-consistency
description: Use this skill when a user provides follow-up feedback to a previously generated document, such as 'shorten the intro,' 'now add a section on pricing,' or 'tweak the formatting to use bullets.' It is triggered when writing is an iterative dialogue where the agent must integrate new instructions without 'breaking' or regressing on the content, citations, or presentation quality already established in earlier turns.
---

# Skill: multi-turn-revision-consistency

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to perform multi-turn, iterative document refinement by successfully incorporating localized content or formatting feedback while ensuring 'Regression-Free Stability.' This requires high Multi-Turn Intent-Consistency, where the agent minimizes the 'Break Rate' (the accidental deletion or corruption of previously satisfied content coverage) and prevents 'Citation Degradation' (the loss of evidentiary grounding or in-text markers) that frequently occurs when language models perform global rewrites instead of localized, delta-aware editing.
* **Dimension Hierarchy**: Revision Fidelity->Direct Text Modification->multi-turn-revision-consistency

### Real Case
**[Case 1]**
* **Initial Environment**: The agent has generated a multi-thousand-word research report about Palantir Technologies, covering its history from 2003, its Gotham and Foundry platforms, and its 2020 IPO. The current draft is high-quality but uses very long, dense paragraphs throughout.
* **Real Question**: To enhance reader engagement throughout this detailed article, try varying sentence length and structure more deliberately—mix shorter, punchy sentences with longer, complex ones to create a natural rhythm that keeps the reader's attention from start to finish.
* **Real Trajectory**: The agent receives the formatting request for 'sentence variety.' Instead of performing localized stylistic adjustments or a 'surgical rewrite,' it generates a new version of the report. While the sentence variety is improved, the agent accidentally omits the entire concluding paragraph regarding the significance of the 2020 IPO and the company's future reach.
* **Real Answer**: [A version of the report with varied sentence lengths but missing the pre-existing 150-word concluding section on IPO implications and market signals.]
* **Why this demonstrates the capability**: This demonstrates a high 'Break Rate' failure in multi-turn consistency. The agent successfully incorporated the 'Format Feedback' (incorporation success) but failed to preserve 'content outside the feedback's scope.' It proves that without specific multi-turn state-management, agents tend to drop previously covered information when focused on new stylistic constraints.
---
**[Case 2]**
* **Initial Environment**: The agent is revising an 8-page technical report about the DeepSeek V3 model architecture. The Turn 1 report includes dense in-text citations [1][6][7] for every technical claim and a complete bibliography at the end.
* **Real Question**: The report could be improved by explicitly highlighting DeepSeek R1's standout creative task performance and diving deeper into the specialized domain optimization strategies it uses.
* **Real Trajectory**: The agent identifies the new content targets (R1 performance and optimization). It inserts several new paragraphs discussing these strategies. However, in the process of re-synthesizing the document, it removes most of the numeric in-text citation markers for the original V3 architecture section and fails to update the bibliography with the new R1 sources.
* **Real Answer**: [A revised technical report that adds R1 details but contains 'Citation Degradation,' where most claims now lack verifyable grounding or references.]
* **Why this demonstrates the capability**: This demonstrates 'Citation Degradation,' a primary failure mode of multi-turn revision. The agent prioritizes adding 'New Content' (from the feedback) at the expense of 'Factuality' (established in Turn 1). It highlights that preserving existing evidentiary chains is a distinct, hard constraint during the refinement cycle.
---
**[Case 3]**
* **Initial Environment**: The agent is helping a researcher develop an article on 'Agent Technologies.' The current draft includes a section on 'Strengths' (Retrieval/Reasoning) and 'Limitations' (Context Length/Error Propagation).
* **Real Question**: Add a point about how LLMs ignore tool outputs if they clash with what they already know (Preference for Internal Knowledge).
* **Real Trajectory**: The agent focuses on the 'Internal Knowledge' request and adds a sub-point under 'Limitations.' While doing so, it rewrites the section and inadvertently deletes the 'Error Propagation' heading and its associated text, which was a core component of the Turn 1 comprehensiveness.
* **Real Answer**: II. Limitations of Current Agent Technologies: - Context Length Constraints [...] - Preference for Internal Knowledge [New]. (OMITTED: - Error Propagation).
* **Why this demonstrates the capability**: This illustrates a 'Comprehensiveness Regression.' The agent addresses the user's specific feedback target but disrupts content that was already 'satisfied' in Turn 1. This prevents the cumulative accumulation of report quality over multiple rounds of feedback.

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
