---
name: graph-relational-subgraph-reasoning-data-synthesis
description: Use this skill when the user wants 'questions over a graph', relation questions, path questions, scene-layout questions, or structured-knowledge questions. Trigger it for requests like 'chat with the graph', 'ask using nodes and edges', 'force the model to follow relationships', or 'test whether it hallucinates graph facts'. This skill assumes the environment is a bounded textual or structured graph store.
---

# Skill: Graph-Relational Subgraph Reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to answer questions over a bounded structured graph by retrieving query-relevant nodes and edges, constructing a connected subgraph, and reasoning over relations, paths, or spatial/semantic structure without hallucinating missing graph content. The distinctive challenge is relational structure rather than free-text proximity alone.
* **Dimension Hierarchy**: Specialized Knowledge Navigation->Corpus-Specific Retrieval & Reasoning->Graph-Relational Subgraph Reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A bounded explanation graph containing nodes and edges about rights, combat, and argumentative relations. The question asks whether two arguments support or counter each other.
* **Real Question**: Do argument 1 and argument 2 support or counter each other?
* **Real Answer**: counter
* **Why this demonstrates the capability**: The answer depends on relational structure encoded in the graph rather than on one isolated text span. The agent must retrieve the relevant nodes and edges and reason over their connections. This is a graph-relational reasoning task in its purest form.
---
**[Case 2]**
* **Initial Environment**: A bounded scene graph with nodes for woman, person, and computer, plus spatial relations such as 'to the right of' and 'in front of'.
* **Real Question**: Is there a woman to the right of the person behind the computer?
* **Real Answer**: yes
* **Why this demonstrates the capability**: The question requires composing spatial relations across multiple edges. A text-only bag-of-words view is insufficient because the decisive information lies in the graph’s relational layout. The capability is therefore subgraph retrieval plus relational composition.
---
**[Case 3]**
* **Initial Environment**: A bounded knowledge graph about Justin Bieber and family relations. The answer is reachable only after traversing parent/children or sibling-style links across several nodes.
* **Real Question**: what is the name of justin bieber brother
* **Real Answer**: jaxon bieber
* **Why this demonstrates the capability**: This case tests whether the agent can retrieve a connected subgraph and follow the right relation path to the answer entity. A hallucinating model may invent a family member not present in the graph. The skill therefore emphasizes structurally grounded answering.

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
