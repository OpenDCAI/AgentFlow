---
name: dependency-aware-tool-chaining
description: Use this skill when the user wants to automate a multi-step objective that spans different servers, apps, and domains without naming the tools, or when they provide 'deep research' tasks requiring solving layers of sub-questions. It is triggered by requests like 'find the data and use it to update my records,' 'connect the dots across my science apps,' 'solve these nested clues to find the answer,' or 'narrow down the list using multiple filters sequentially.' This skill is essential for HCSPs (Hierarchical Constraint Satisfaction Problems) where the agent must identify facts at one layer (like finding a specific threshold or city) to serve as mandatory input filters for the next layer. Trigger it for casual needs like 'find the link between these two sources,' 'handle everything for this project step-by-step,' and 'only stop when the goal is fully met.'
---

# Skill: dependency-aware-tool-chaining

## 1. Capability Definition & Real Case
* **Professional Definition**: Dependency-aware tool chaining is the capability to coordinate a series of autonomous computational actors to resolve complex, long-horizon tasks and Hierarchical Constraint Satisfaction Problems (HCSPs) that are unsolvable through single-turn knowledge. This requires the orchestrator to: 1) resolve intermediate 'research trees' where parallel filters prune a candidate set to unlock upstream queries; 2) identify target tools in environments containing similar-looking distractors; 3) manage data-flow dependencies where outputs from one server (e.g., a paper abstract or a city's demographic data) strictly define the parameters for another (e.g., a database query or person-search); and 4) execute conditional fallback tracks. Success requires total maintenance of state topology without prematurely collapsing the search hierarchy.
* **Dimension Hierarchy**: Workflow Orchestration->Dependency and Schedule Management->dependency-aware-tool-chaining

### Real Case
**[Case 1]**
* **Initial Environment**: A containerized workspace exposing an Arxiv search server for academic papers and a Notion workspace containing internal advertising databases. The environment includes distractor tools such as 'memory_search' and generic 'fetch' utilities to test tool selection precision.
* **Real Question**: I’m researching papers on advertisement effectiveness and comparing it to our own online database advertising data. There’s a 2024 paper by Jane Castleman that deals with ad control effectiveness, can you get me the abstract? I believe it mentions ad locality, for which I will also need to ask you for the date of our campaign with the biggest engagement rate, started during the 2015-2023 period, and its locality.
* **Real Trajectory**: 1. The agent identifies the dual nature of the task and calls `arxiv_search_papers("Jane Castleman ad control effectiveness 2024")`. 2. It extracts the abstract. 3. Recognizing it now needs internal data, it ignores the memory-search distractors and uses `notion_API-post-search("advertising")` to locate the correct database. 4. It identifies the 'Campaigns' database and calls `notion_API-post-database-query` with a filter for the 2015-2023 period. 5. It retrieves the dates and localities for the 15% engagement campaigns.
* **Real Answer**: The 2024 paper by Jane Castleman is titled 'Why am I Still Seeing This...'; its abstract discusses Meta's shift toward AI-mediated targeting. Regarding your internal data, there is a three-way tie for biggest engagement (15%) with campaigns started on 2022-06-24 (National), 2019-09-20 (International), and 2017-09-09 (International).
* **Why this demonstrates the capability**: This case demonstrates heterogeneous cross-server orchestration by linking academic research (Arxiv) with proprietary data (Notion). It tests the agent's ability to maintain subgoal persistence—not stopping after finding the paper—and discovery precision by selecting the correct tools over distractors.
---
**[Case 2]**
* **Initial Environment**: A multi-agent environment with a primary web-search server (Brave), a fallback search server (DuckDuckGo), and an internal Knowledge Graph. The agent is tasked with finding a definition that defines the logic for a subsequent computation.
* **Real Question**: Find the EPA's definition for 'unhealthy' air quality days (AQI threshold). Using that specific threshold, search our 2024 wildfire logs to determine the total land area affected only on days that met that 'unhealthy' criteria.
* **Real Trajectory**: 1. The agent calls `brave_search("EPA unhealthy air quality AQI threshold")`. 2. The observation identifies 'Unhealthy' as AQI > 150. 3. The agent queries the `wildfire_log_server` and uses the newly discovered '150' as a filter parameter in the query. 4. It iterates through the results to aggregate the land area for 2024.
* **Real Answer**: The EPA defines an 'unhealthy' air quality day as having an AQI exceeding 150. Based on your 2024 logs, a total of 425,000 hectares were affected by fires occurring during these high-risk days.
* **Why this demonstrates the capability**: This case highlights conditional branching and dynamic parameterization. The orchestrator must extract a specific variable (150) from an external search and use it to define the filter for a downstream internal database. This prevents 'partial task completion' by ensuring the agent continues until the numerical synthesis subgoal is satisfied.
---
**[Case 3]**
* **Initial Environment**: A multi-agent environment with access to a global web-search engine, a Wikipedia retrieval tool, and a fact-verification worker.
* **Real Question**: This mathematician, born in a European city whose official language is English and whose population exceeds five million, studied at Cambridge and later earned his PhD at Princeton University in 1938. Who is he?
* **Real Trajectory**: The orchestrator treats this as a Hierarchical Constraint Satisfaction Problem. 1) It treats the 'Birthplace' as a sub-problem, dispatching a search for European cities combining the language and population filters (Result: London). 2) It identifies 'Princeton PhD' as a second constraint and researches the context of the 1938 degree. 3) It passes the 'Birthplace (London)' and 'Education (Cambridge + Princeton 1938)' as mandatory input arguments to the final candidate-filtering tool. 4) It confirms the identity of the mathematician who satisfies all sequential constraints.
* **Real Answer**: Alan Turing
* **Why this demonstrates the capability**: This demonstrates dependency chaining through a deep research tree. The agent cannot skip directly to the entity; it must resolve an upstream constraint (the city) via parallel filtering to extract the prerequisite string needed to power the downstream query (the person).

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
