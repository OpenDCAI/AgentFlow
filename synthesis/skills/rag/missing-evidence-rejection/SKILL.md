---
name: missing-evidence rejection
description: Trigger this skill when users want to test if an agent can say 'I don't know' or 'not enough info' when the facts are missing, semi-missing, or when the question itself is a trick. Use it for requests like 'make the model deflect from unanswerable questions', 'test if it gets caught by false assumptions', 'give me questions that ask for too much detail', or 'hide the answer and see if it guesses'. It teaches the agent to resist 'shortcut reasoning' and identify when evidence is insufficient, contradictory, or lacks the required specificity.
---

# Skill: missing-evidence rejection

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform grounded insufficiency judgments and formal abstentions when the retrieved corpus lacks the comprehensive evidence required to satisfy a query's constraints. This capability encompasses three critical dimensions: 1) Total Absence (the answer is not in the text), 2) Uncertain Specificity (the query asks for finer-grained details than the evidence provides), and 3) False Premise Detection (the query contains assumptions that directly contradict the retrieved facts). Robust performance requires resisting 'shortcut reasoning'—the tendency to guess an answer based on topical overlaps or internal parametric knowledge rather than explicit grounded evidence.
* **Dimension Hierarchy**: Grounded Response Reliability->Retrieval Robustness->missing-evidence rejection

### Real Case
**[Case 1]**
* **Initial Environment**: A RAG context containing a fictional news timeline about a dessert pop-up. Document A describes how food critic Selvia Renek published an investigative piece on her blog questioning the 'transparency' and 'ingredient origins' of a shop called Amber Glaze Delights.
* **Real Question**: What did the author of an investigative piece associated with the hashtag #SourcingScandal question about the cost of the ethical certification program?
* **Real Trajectory**: The agent identifies the subject (Selvia Renek) and the event (investigative piece on blog). It retrieves Document A which confirms she questioned 'robustness' and 'systemic issues' regarding a certification program, but finds no mention of 'cost'. The agent recognizes that the premise of the question (that she questioned the cost) is a false assumption relative to the provided text.
* **Real Answer**: Unanswerable
* **Why this demonstrates the capability**: This is a False Premise case. The agent must detect that while the topic (Selvia Renek / Certification Program) is present, the specific attribute asked about (cost) contradicts the qualitative concerns (robustness) expressed in the evidence.
---
**[Case 2]**
* **Initial Environment**: A RAG environment containing professional profiles. A news article mentions that a pilot community center project will conduct 'performance metric collection' starting in March 2027.
* **Real Question**: What specifically were the three categories of performance metrics collected by the pilot community centers during their first evaluation phase?
* **Real Trajectory**: The agent scans the document and finds the mention of 'performance metric collection' and the date 'March 2027'. However, it observes that the text never lists the 'three categories' or even any specific metric names. It identifies a specificity gap where the question is more granular than the evidence.
* **Real Answer**: I cannot answer this question because the provided documents state that metrics were collected but do not list the specific categories of those metrics.
* **Why this demonstrates the capability**: This demonstrates Uncertain Specificity detection. The agent avoids 'shortcut reasoning' (guessing common metrics like 'cost' or 'usage') and accurately identifies that the information exists at a high level but lacks the required granularity.
---
**[Case 3]**
* **Initial Environment**: A RAG environment containing a multi-hop news chain. Document 1: Alveris Culinary Guild announces a mentorship program. Document 2: A mystery person from the Guild says the program will launch in August. The bridge entity (the mystery person's name) is missing from the retrieved set.
* **Real Question**: Who is the representative of the Alveris Culinary Guild who confirmed the August launch date for the mentorship program?
* **Real Trajectory**: The agent finds Document 1 (mentorship program) and Document 2 (August launch confirmed). It realizes that while it knows *what* happened and *when*, the 'representative's name' (the bridge) is not mentioned in either document. Instead of guessing a likely candidate from other documents, it identifies the broken link in the reasoning chain.
* **Real Answer**: Unanswerable
* **Why this demonstrates the capability**: This demonstrates Incomplete Chain Rejection. It specifically tests resistance to shortcut reasoning where a model might guess a famous person name provided in the context regardless of whether they were the one who made the specific announcement.

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
