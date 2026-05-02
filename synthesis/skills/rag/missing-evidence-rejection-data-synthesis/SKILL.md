---
name: missing-evidence-rejection-data-synthesis
description: Use this skill when the user wants questions where the docs look relevant but still do not contain the answer. Trigger it for requests like 'make the model say it can't tell', 'give me questions with not enough information', 'test whether it refuses instead of guessing', or 'include related documents but no real answer'. This skill is for data that teaches evidence-bounded abstention in a read-only RAG setting.
---

# Skill: Missing-Evidence Rejection

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to refuse answering when the retrieved corpus does not contain the required evidence. The emphasis is not on passive abstention alone, but on making a grounded insufficiency judgment despite topical overlap or user pressure.
* **Dimension Hierarchy**: Grounded Response Reliability->Retrieval Robustness->Missing-Evidence Rejection

### Real Case
**[Case 1]**
* **Initial Environment**: A bounded retrieval set about Nobel Prize literature winners, but every retrieved passage discusses years other than the one asked about. The passages are relevant in topic and entity type, yet none contains the requested answer.
* **Real Question**: Who was awarded the 2022 Nobel prize in literature?
* **Real Answer**: I can not answer the question because of the insufficient information in documents.
* **Why this demonstrates the capability**: The retrieval set is intentionally tempting because it contains true prize-related information. The correct behavior is to reject, not to interpolate from adjacent years or prior knowledge. This capability therefore measures evidence-bounded abstention under realistic topical pressure.
---
**[Case 2]**
* **Initial Environment**: A bounded report corpus in which the question refers to a non-existent company and asks for yearly figures. Retrieved documents may still discuss similar report structures and company metrics, but no document can ground the requested entity.
* **Real Question**: What are the sales of company ABCD as reported in its 2022 and 2023 annual reports?
* **Real Answer**: Insufficient information.
* **Why this demonstrates the capability**: This case tests whether the agent recognizes that the bridge entity does not exist in the knowledge base, even though the query format resembles ordinary report questions. A weak model may hallucinate a plausible sales answer or borrow numbers from a nearby company. A strong model should conclude that the corpus cannot support any answer at all.

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
