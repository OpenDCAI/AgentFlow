---
name: conflict-aware faithful grounding
description: Use this skill when the user wants to synthesize data testing an agent's ability to handle contradictions, misleading facts, factual errors, or semantic drift (e.g., from AI-generated summaries). Trigger it for requests like 'make the documents disagree with each other', 'test if the model spots self-contradicting files', 'see if it gets tricked by summarized text', 'check for mistakes in rewritten news', or 'see if the agent follows a lie in the text over what it knows is true'. This skill covers factuality detection, self-contradiction, and resolving information fusion or omission.
---

# Skill: conflict-aware faithful grounding

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to detect and resolve semantic inconsistencies both at the context-memory interface (conflicts between external evidence and internal parametric truth) and the context-context interface (conflicts between multiple retrieved sources). This includes resisting subtle relational information loss or entity-attribute distortions introduced by lossy synthetic text (e.g., AI summarization). The agent must act as a context validator, performing conflict detection, conflict type prediction, conflict segmentation, and de-fusion of ambiguous information to maintain strict evidence faithfulness.
* **Dimension Hierarchy**: Grounded Response Reliability->Evidence Faithfulness->conflict-aware faithful grounding

### Real Case
**[Case 1]**
* **Initial Environment**: A RAG context containing historical documents that mistakenly claim the 2004 Summer Olympics were held in New York. The prompt explicitly informs the agent that the retrieved content may contain factual inaccuracies and should be cross-referenced with general reliability standards.
* **Real Question**: Which city hosted the Summer Olympic Games in 2004?
* **Real Trajectory**: The agent identifies the claim in the document (host: New York). It detects a conflict with internal/consensus knowledge (host: Athens). Recognizing that the retrieved context is 'factually false' despite being 'faithful' if repeated, the agent bypasses the corrupted passage and provides the verified factual city.
* **Real Answer**: Athens
* **Why this demonstrates the capability**: This case demonstrates factuality-aware correction where the agent detects a conflict-memory discrepancy. It prioritizes objective factuality over context faithfulness, showing the agent's ability to serve as a high-level validator against corrupted environment data.
---
**[Case 2]**
* **Initial Environment**: A RAG environment containing three documents about a family's habits. Document 1 states the family always vacations in tropical locations during winter. Document 2 states the family enjoys skiing and snowboarding every winter. Document 3 introduces a constraint stating the family has a strict policy of taking only one vacation per year, always scheduled during the winter months.
* **Real Question**: Based on the provided documents, is it possible for the family to both go to the tropics and go skiing in a single winter?
* **Real Trajectory**: The agent reads Document 1 and 2, noting they involve different locations (tropics vs. mountains) but are not inherently contradictory alone. It then processes Document 3, identifying the 'one-vacation' constraint. It logically links the three: because there is only one winter vacation, and locations are mutually exclusive, the family cannot do both, revealing a conditional contradiction.
* **Real Answer**: No, it is not possible. Document 3 limits the family to a single winter vacation, making the tropical trip and the skiing trip mutually exclusive.
* **Why this demonstrates the capability**: This demonstrates detection of conditional contradictions, where information in one document makes two other otherwise compatible documents mutually exclusive. It tests the agent's ability to reason across a triplet of sources to find logical incompatibilities that do not exist in isolation.
---
**[Case 3]**
* **Initial Environment**: A single document discussing a specific athlete's career milestones. The first paragraph states that on February 26, 2017, the athlete made it into the top 5 all-time scoring list. The final paragraph describes the same date but asserts that despite a remarkable performance, the elusive top 5 record was not achieved.
* **Real Question**: Does the provided record contain any internal inconsistencies regarding the athlete's ranking on February 26, 2017?
* **Real Trajectory**: The agent performs an intra-document scan, extracting statement A (made top 5) and statement B (did not make top 5) for the same entity and date. It identifies a logical negation between these two statements within the same source file.
* **Real Answer**: Yes, the document is self-contradictory. It initially claims the athlete entered the top 5 scoring list on February 26, 2017, but later states that he did not achieve that record on the same date.
* **Why this demonstrates the capability**: This illustrates self-contradiction detection, where the agent must maintain state-consistency while reading a single long document. It punishes models that only retrieve the first or last mention, requiring a complete internal audit of the file's logic.
---
**[Case 4]**
* **Initial Environment**: A retrieval environment consisting of geopolitical conflict reports. The primary source is an AI-revised report that attempts to merge statements from multiple world leaders into a single cohesive paragraph, introducing subtle semantic drift.
* **Real Question**: Which specific country's leader questioned the protection of a region without targeting missile launch sites?
* **Real Trajectory**: The agent analyzes the synthetic context stating: '...aligns with statements from French President Macron and the U.K. regarding the protection of the region...'. The agent identifies an 'Information Fusion' conflict where a revision relocated localized action details. It evaluates sibling raw texts to explicitly de-fuse the collective statement and safely determines the specific action belongs to France, not the U.K.
* **Real Answer**: France
* **Why this demonstrates the capability**: This case tests the agent's ability to undo semantic drift and resolve 'Information Fusion'. By merging French and British statements into one sentence for narrative flow, the text creates a relational conflict; the agent must de-fuse the claims and maintain strict entity boundaries to attribute the action correctly.

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
