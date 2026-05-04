---
name: graph-relational subgraph reasoning
description: Use this skill when you need to navigate structured knowledge bases, relational triplets, or knowledge graphs to connect different facts. It is triggered by requests like 'connect the dots between these news updates', 'find the person who meets all these shared conditions', 'what are all the projects this artist is linked to', or 'who is the owner of the company that sold the most units'. This skill emphasizes traversing explicit symbolic paths (like Subject-Predicate-Object) to find intersections or multi-step connections that a single search cannot reveal.
---

# Skill: graph-relational subgraph reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform multi-hop reasoning and intersection-based discovery over structured knowledge repositories (e.g., Knowledge Graphs) or relational triplets. This includes executing structural reasoning templates such as Multi-Hop chains (navigating via bridge entities), Conditional intersections (finding a unique entity satisfying multiple predicates), and Set-based aggregation (collecting all entities sharing a common relation). The agent must maintain symbolic grounding by verifying the integrity of each relational edge and prioritizing novel, corpus-specific facts that cannot be resolved through internal parametric memory.
* **Dimension Hierarchy**: Specialized Knowledge Navigation->Corpus-Specific Retrieval & Reasoning->graph-relational subgraph reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A RAG environment containing a periodically updated news corpus focused on the automotive industry and fiscal reports.
* **Real Question**: In which country is the company located that sold 2139 cars in 2023?
* **Real Trajectory**: The agent identifies the specific metric '2139 cars sold in 2023'. It retrieves a facts triplet linking this metric to the company 'FAW'. It then performs a second hop to retrieve the 'country of origin' for the 'FAW' entity, which lists 'China'.
* **Real Answer**: China
* **Why this demonstrates the capability**: This case demonstrates Multi-Hop reasoning using a bridge entity. The agent cannot find the country directly from the sales metric; it must first identify the company (FAW) as the intermediate bridge and then traverse the 'origin' relation to reach the final answer.
---
**[Case 2]**
* **Initial Environment**: A RAG context containing cultural news and event logs regarding public performances and meetings.
* **Real Question**: Who performed at M-bar and met with Dmitry Dibrov?
* **Real Trajectory**: The agent identifies two independent constraints: 'performed at M-bar' and 'met with Dmitry Dibrov'. It performs a parallel search for both conditions, retrieving a list of performers for the first and a list of associates for the second. It calculates the intersection of these two sets to isolate the unique subject.
* **Real Answer**: Roman Miroshnichenko
* **Why this demonstrates the capability**: This illustrates Conditional intersection reasoning. The agent must find a single entity that satisfies two distinct relational triplets in the graph, ensuring that the answer is the common 'Subject' node for both provided 'Object' constraints.
---
**[Case 3]**
* **Initial Environment**: A bounded repository of entertainment news and professional discographies.
* **Real Question**: What projects has Ryan Otter composed music for?
* **Real Trajectory**: The agent identifies the subject 'Ryan Otter' and the relation 'composed music for'. It scans the corpus to extract every unique entity (object) connected to this specific subject-relation pair.
* **Real Answer**: Trigger, Method
* **Why this demonstrates the capability**: This demonstrates Set-based aggregation. The agent is forced to perform an exhaustive relational scan to ensure it collects all valid entities in the subgraph, testing the completeness of the RAG system's information alignment.

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
