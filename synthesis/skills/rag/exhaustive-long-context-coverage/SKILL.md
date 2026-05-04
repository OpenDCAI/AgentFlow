---
name: exhaustive long-context coverage
description: Use this skill when the user wants questions that require reading the entire context window, ensuring no file or nested branch is left behind. Trigger it for requests like 'need reading everything', 'give me a full breakdown of this specific chapter', 'summarize the statistics for all entities found', or 'tell me all the subsections' occurrences'. It forces extreme entity density and global context accounting across both multi-document spreads and deep intra-document hierarchies.
---

# Skill: exhaustive long-context coverage

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to preserve coverage over extended multi-document contexts or deep intra-document hierarchical branches. This ensures no required localized document, sub-section, or dispersed entity is silently ignored, facilitating global aggregation, high-density entity extraction, mathematical categorization, and robust distribution analysis over dozens of scattered sources or massive singular reports.
* **Dimension Hierarchy**: Multi-Source Evidence Composition->Long-Context Coverage->exhaustive long-context coverage

### Real Case
**[Case 1]**
* **Initial Environment**: A long bounded bundle of company reports from the same domain. Each company’s non-current-assets figure is stored in its own document.
* **Real Question**: Which company has the highest non-current assets?
* **Real Trajectory**: The agent sequentially scans the entire bundle, logs the specific asset value for each individual company candidate, and globally evaluates the maximum value.
* **Real Answer**: HARTE HANKS
* **Why this demonstrates the capability**: This case punishes the agent if it reads only a convenient subset of documents or stops early, as it must evaluate every dispersed fact to compute an accurate extremum.
---
**[Case 2]**
* **Initial Environment**: A RAG environment containing a massive collection of Wikipedia-style biography pages for ACM Fellows. Each document records nationality, research field, and affiliation.
* **Real Question**: How many ACM fellows are from MIT, and what is the most common research field among them?
* **Real Trajectory**: The agent extracts the affiliation attribute across hundreds of documents, groups the subset matching 'MIT', and performs a statistical frequency measurement on the 'field' attribute.
* **Real Answer**: There are 42 ACM fellows associated with MIT; the most common research field among this group is Artificial Intelligence with 12 fellows.
* **Why this demonstrates the capability**: This involves cross-document statistical aggregation. The agent is forced to execute exhaustive scanning, build a dense property array, and generate an analytical deduction spanning massive scale.
---
**[Case 3]**
* **Initial Environment**: A long context containing a highly structured 50-page technical report on a biographical film. The document is hierarchically structured into 'Introduction', 'Production History', 'Casting', and 'Critical Reception' sections, with numerous subsections spanning thousands of tokens.
* **Real Question**: Provide a comprehensive overview of the supporting cast members involved in the 1994 biographical film Ed Wood and the specific roles they played.
* **Real Trajectory**: The agent scans the vast hierarchy and identifies the 'Casting' branch and its subsections. It traverses the entire branch for 'Supporting Cast', exhaustively assembling the names of Sarah Jessica Parker, Patricia Arquette, Jeffrey Jones, Lisa Marie, and Bill Murray from various paragraphs nestled deep within that specific section, refusing to stop after the first isolated hit.
* **Real Answer**: The supporting cast for 'Ed Wood' included Sarah Jessica Parker, Patricia Arquette, Jeffrey Jones, Lisa Marie, and Bill Murray. Each member contributes to the biographical narrative, specifically focusing on the period in Wood's life when he collaborated with Bela Lugosi.
* **Why this demonstrates the capability**: This case emphasizes exhaustive coverage localized to a deep hierarchical branch within a massive document. The answer cannot be retrieved from a single sentence; it requires the agent to recognize the tree structure, navigate to the correct branch, and extract dense information that is widely distributed across paragraphs without dropping completeness.

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
