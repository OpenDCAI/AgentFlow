---
name: precise-localized-editing
description: Use this skill when the user wants to apply a highly targeted edit—such as deleting redundant filler, rephrasing a paragraph without losing exact technical facts, or filling in a missing logical gap—without rewriting the whole document. Trigger it for requests like “delete this placeholder,” “cut the fluff from the second paragraph,” “rephrase this medical report but keep the exact measurements,” or “fill in the missing bridge between these two sections.”
---

# Skill: precise-localized-editing

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to execute boundary-constrained textual modifications—encompassing subtractive pruning, semantic-invariant replacement, and contextual insertion—upon specific spans of a document. This requires preserving completely unrelated context, freezing mandatory factual anchors (like laterality or quantitative metrics) during stylistic rephrasing, and deducing logical bridges to insert missing text without inducing semantic drift.
* **Dimension Hierarchy**: Revision Fidelity->Direct Text Modification->precise-localized-editing

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is iteratively refining a business memo. By a later step, the draft has substantially expanded its word count by adding 'helpful' explanations, causing the memo to lose its original focus on 'Urgent Budget Cuts' and drift into tangential advice.
* **Real Question**: Continue refining this document to improve quality while ensuring it stays aligned with the original intent of a 'Concise Budget Alert.'
* **Real Trajectory**: The agent notices semantic drift where the memo now contains more text about future growth than immediate cuts. It performs a subtractive refinement pass, aggressively deleting the newly added growth paragraphs to restore the focus to the budgetary constraints without altering the core headings.
* **Real Answer**: A revised memo that removes three recently added paragraphs to restore the original concise tone and urgency, reversing the semantic drift caused by earlier additive increments.
* **Why this demonstrates the capability**: This demonstrates 'subtractive localized refinement.' The agent recognizes when a document's quality relies on targeted deletion rather than additive generation, pruning specific overgrown areas while maintaining the rest of the document's rigid structure.
---
**[Case 2]**
* **Initial Environment**: The agent is provided with an original, dense 3D CT radiology report containing complex medical terminology. The report notes 'No evidence of acute intracranial hemorrhage' and a '3mm nodule in the right lower lobe.'
* **Real Question**: Rephrase this report to be more concise and easier for a primary care physician to skim, while ensuring every clinical finding remains semantically identical.
* **Real Trajectory**: The agent extracts the clinical invariants: absence of hemorrhage, nodule size (3mm), and exact laterality/location (right lower lobe). It then performs stylistic rephrasing to move from a narrative format to a succinct summary, verifying that the rephrased version preserves the exact negation and directionality.
* **Real Answer**: Clinical Summary: 3mm nodule identified in the right lower lung lobe. Acute intracranial hemorrhage is absent. No other significant abnormalities noted.
* **Why this demonstrates the capability**: This illustrates 'semantic-invariant replacement.' While the text-based style and lexical overlap are altered to meet conciseness constraints, the required factual anchors (right vs. left, absent vs. present) are mapped immutably, ensuring targeted edits do not result in factual hallucination.
---
**[Case 3]**
* **Initial Environment**: The agent is provided with an academic essay discussing technology and socializing. The middle section of an argument—which logically transitions between the prefix (human social demands) and suffix (specifically using dating sites to find soul mates)—has been artificially withheld.
* **Real Question**: Please fill in the missing gap. Ensure the restoration maintains the author's specific stance and connects the desire for companionship with the use of dating sites mentioned later.
* **Real Trajectory**: The agent identifies the intent gap by analyzing the prefix and suffix. It deduces the intervening rhetorical step (that technology acts as a surrogate for traditional physical social spaces) and synthesizes a focused paragraph to functionally restore this specific bridge without repeating existing context.
* **Real Answer**: Many people associate technology with utopia. Those who lack time to go to social places may use online platforms to maintain a professional lifestyle. Companionship is complicated; technology exists to make life easy, forming the necessary bridge before individuals turn to specialized services.
* **Why this demonstrates the capability**: This showcases 'contextual insertion and text restoration.' The agent deduces the precise rhetorical intent missing from a localized empty span, perfectly sewing its generated output into the boundaries of the preceding and succeeding text blocks.

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
