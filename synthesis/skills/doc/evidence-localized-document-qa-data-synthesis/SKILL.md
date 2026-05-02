---
name: evidence-localized-document-qa-data-synthesis
description: Use this skill when the user wants the agent to find the exact place in documents that answers a question, not just give a general summary. Trigger it for requests like "find where the file says this," "which page has the number," "answer only from the document," or "look through the slides and tell me the exact figure." This is especially useful for long PDFs, reports, contracts, papers, or slide decks where the answer is localizable to a page, paragraph, table cell, chart, or layout region.
---

# Skill: Evidence-localized document QA

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to answer a question by locating the exact local evidence span that contains the answer inside a document corpus, preserving page- or region-level grounding rather than relying on diffuse gist. It covers text-native documents and visually rich pages, and it requires the agent to distinguish true answer-bearing regions from nearby distractors such as repeated numbers, similar headings, or visually similar charts.
* **Dimension Hierarchy**: Document Grounding & Reasoning->Evidence Use->Evidence-localized document QA

### Real Case
**[Case 1]**
* **Initial Environment**: A large archive of Wikipedia articles is loaded into a searchable document store, and the agent must pull only the relevant snippets into working context before answering.
* **Real Question**: "Who won the first Nobel Prize in physics?"
* **Real Trajectory**: The agent searches for "nobel physics", inspects paginated results, issues a follow-up search on the second result page, and then reads the snippet containing the award recipient.
* **Real Answer**: "Wilhelm Conrad Roentgen"
* **Why this demonstrates the capability**: The answer is not produced from generic background knowledge alone; it is recovered by narrowing to a specific retrieved span in a large archive. The trajectory matters because the first search page is insufficient and the correct span appears after another retrieval step. This demonstrates precise evidence hunting, not broad summarization.

---
**[Case 2]**
* **Initial Environment**: A multi-document financial-report bundle is presented in one long context, with many companies and many similar accounting fields acting as noise.
* **Real Question**: "What is the Basic Earnings Per Share for Dominari Holdings Inc.?"
* **Real Answer**: "$(0.91)"
* **Why this demonstrates the capability**: Only one local region contains the target field, while the surrounding documents contain semantically similar accounting entries that are irrelevant. The task therefore tests whether the agent can isolate one answer-bearing span instead of blending nearby values. It is a clean example of page- and field-level grounding inside noisy long context.

---
**[Case 3]**
* **Initial Environment**: A large visually rich slide corpus contains many pages with text, charts, tables, and layouts, and each query has a unique answer tied to specific reference pages.
* **Real Question**: "What is the peak value of the data?"
* **Real Answer**: "529"
* **Why this demonstrates the capability**: The answer is visually anchored and must be recovered from the correct page rather than inferred from a textual paraphrase alone. The benchmark design makes reference-page grounding explicit, which is exactly the failure mode a document agent must overcome on slides and dashboards. This demonstrates evidence localization in a multimodal document space.

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
