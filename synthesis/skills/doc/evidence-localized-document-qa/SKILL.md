---
name: evidence-localized document qa
description: Use this skill when the user wants to locate exact evidence within a document to answer a question, particularly when the user's natural language phrasing differs significantly from the document's formal terminology (e.g., paraphrased queries). This skill helps the agent bridge the lexical gap between everyday questions and official documents like institutional norms, regulations, or scientific reports. Trigger it for requests like 'find the rule for X', 'summarize the eligibility criteria in this ordinance', 'where in the statute does it mention Y', or 'answer this based on the university regulations', especially when the user uses casual language to describe formal concepts.
---

# Skill: evidence-localized document qa

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to execute high-precision evidence localization and hierarchical multi-abstraction level (MAL) retrieval within complex multimodal document environments, with specific robustness against lexical and syntactic variability (paraphrasing). This capability involves mapping informal user queries to formal document structures—such as multi-sentence, paragraph, and section levels—by constructing semantic representations that transcend surface-level keyword matching. It utilizes chunk-size optimization (e.g., 2K-8K character weighting) and map-reduce summarization to identify the optimal context granularity, ensuring accuracy even when official terminology is absent from the initial query.
* **Dimension Hierarchy**: Document Grounding & Reasoning->Evidence Use->evidence-localized document qa

### Real Case
**[Case 1]**
* **Initial Environment**: A collection of institutional normative documents from a large public university (University of São Paulo), including statutes, ordinances, and resolutions regarding student benefits.
* **Real Question**: What are the requirements for a student to keep getting financial help according to the 2024 university rules?
* **Real Trajectory**: The agent identifies the user is asking about 'financial help' (informal) which maps to 'Financial Aid' or 'Institutional Grants' in the normative corpus. It retrieves a 2K-character chunk from a 2024 Ordinance regarding student permanence. The agent notes that while the user said 'keep getting,' the document uses the term 'periodicity of renewal' and 'academic performance criteria.' It maps these concepts and extracts the specific GPA and attendance requirements.
* **Real Answer**: According to Ordinance No. 79/2024, students must maintain a minimum weighted average of 7.0 and a minimum attendance of 75% in all enrolled courses to renew their institutional grants.
* **Why this demonstrates the capability**: This case demonstrates 'Paraphrase-Robust Semantic Retrieval.' The agent successfully bridged the lexical gap between the user's casual phrasing ('keep getting financial help') and the document's formal regulatory language ('periodicity of renewal of institutional grants'), identifying the correct grounding despite low keyword overlap.
---
**[Case 2]**
* **Initial Environment**: A scientific paper focused on Glycoscience, containing structural markers for 'Introduction', 'Results', and 'Discussion' sections.
* **Real Question**: What are the primary challenges in characterizing glycan-protein interactions as discussed in the 'Results' section?
* **Real Trajectory**: The agent identifies the 'Results' section within the document's hierarchy. Instead of retrieving 20 individual raw paragraph chunks, the agent retrieves a pre-computed 'Section-Level Summary' chunk. This summary identifies the key constraints regarding sensitivity and molecular complexity while excluding tangential experimental details.
* **Real Answer**: The primary challenges include high molecular micro-heterogeneity and the low-affinity nature of glycan bindings, which complicate standard mass spectrometry characterization.
* **Why this demonstrates the capability**: This illustrates 'Section-Level Abstraction Retrieval.' By using a summarized section chunk rather than fragmented sentences, the agent captures the high-level background needed to answer a section-specific query without information dilution.
---
**[Case 3]**
* **Initial Environment**: A large-scale SEC 10-K document that has undergone grainy OCR processing, introducing substantial character noise.
* **Real Question**: What are the details of the purchase agreement for the property mentioned in the filing?
* **Real Trajectory**: The agent applies a fuzzy-match proximity search to compensate for OCR artifacts, mapping the corrupted string 'Purchale Agrement' found in the document to the user's intent. It narrows the search to the localized paragraph containing property details.
* **Real Answer**: The Purchase Agreement (dated December 4) granted an option to purchase a 413-acre group known as the Langtry Property.
* **Why this demonstrates the capability**: This scenario proves robustness handling real-world OCRed contexts where exact-keyword matching fails, requiring semantic localization and error-tolerant parsing.

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
