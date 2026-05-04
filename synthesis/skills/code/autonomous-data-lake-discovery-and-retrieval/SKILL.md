---
name: autonomous-data-lake-discovery-and-retrieval
description: Use this skill when the user provides a data science question that requires finding the right files within a large and messy 'data lake' rather than having the data pre-specified. It is triggered by layman requests such as 'find the right data to answer this in our lake', 'search our huge project for information about X and analyze it', 'there are thousands of files, pick the relevant ones to solve Y', or 'I don't know which CSV has this info, please find it and calculate Z'. It is specifically for handling scale and heterogeneity in data environments where discovery is the first crucial bottleneck.
---

# Skill: autonomous-data-lake-discovery-and-retrieval

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to autonomously navigate large-scale, heterogeneous data environments (data lakes) containing thousands of files in diverse formats (e.g., CSV, GPKG, CDF, XLSX) to identify, retrieve, and integrate relevant information for complex data science tasks. This involves executing multi-modal reconnaissance across file namespaces, performing representative content sampling to infer schema structures, and utilizing iterative search and external grounding to resolve domain-specific ambiguities and achieve end-to-end task completion.
* **Dimension Hierarchy**: Data and ML Workflow Engineering->Enterprise Data Workflow Coding->autonomous-data-lake-discovery-and-retrieval

### Real Case
**[Case 1]**
* **Initial Environment**: A large-scale proteomics repository contains hundreds of Excel files and metadata tables. A user provides a question about health metrics that references an undefined acronym 'APP-Z'.
* **Real Question**: What is the age of the patient with the lowest APP-Z score?
* **Real Trajectory**: The agent first performs a web search to define 'APP-Z score' in the context of the specific medical study, identifying it as a derived z-score for Acute Phase Proteins. It then audits the repository to find clinical metadata files (e.g., mmc1.xlsx) and supplemental scoring files (e.g., mmc7.xlsx). Using a Python script, it loads the 'Age' column from the metadata and the 'APP_Z_score' from the identified supplement, joining them on unique patient IDs. After cleaning for missing values, it identifies the patient with the minimum score and reports their age.
* **Real Answer**: 60
* **Why this demonstrates the capability**: This illustrates data discovery because the agent had to bridge a 'semantic gap' (the definition of the score) and a 'structural gap' (finding the specific files containing the raw and derived data) across a large, heterogeneous folder structure.
---
**[Case 2]**
* **Initial Environment**: A data lake containing thousands of environment and wildfire datasets from different organizations, including NOAA and NIFC records, with inconsistent naming conventions and formats.
* **Real Question**: Which of the 10 NICC-defined geographic areas requested the most helicopters for firefighting in the provided datasets?
* **Real Trajectory**: The agent performs a recursive file listing to group datasets by source prefixes. It identifies a potential resource-request cluster and samples several files, discovering 'cleaned_helicopter_requests_by_region.csv'. It then writes a data-loading script to ensure the 'Region' names align with the NICC definitions. Finally, it executes an aggregation and sorting command to find the area with the maximum total requests.
* **Real Answer**: Great Basin Area
* **Why this demonstrates the capability**: The capability is tested because the agent must manage 'scale and noise'. It successfully navigates a data lake with thousands of distractor files to isolate the specific CSV that contains the pre-aggregated firefighting resource data.

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
