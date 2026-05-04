---
name: graph-structured relational reasoning
description: Use this skill when the user wants to analyze how different items are connected or identify important 'hub' entities in a network. Trigger it for requests like “who is the middle-man here?”, “find the quickest path between these two points,” “group these users into communities based on their links,” or “tell me which node is the most influential.” Plain-language examples: “Ask which city is the main bottleneck for travel,” “find the shortest route skipping these roads,” “group these accounts by who talks to whom,” or “measure how closely linked these two people are.”
---

# Skill: graph-structured relational reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to map natural language inquiries onto formal graph-theoretic algorithms—specifically pathfinding (Dijkstra, Yen’s), centrality (PageRank, Betweenness), and community detection (Louvain, k-cut)—to quantify and interpret patterns of connectivity, influence, and topology within a relational dataset. It requires the agent to translate qualitative goals (e.g., 'bottleneck', 'influence') into precise mathematical parameters like edge weights, damping factors, and k-neighbors while navigating relational schemas.
* **Dimension Hierarchy**: Analytical Transformation->Analytical Inference->graph-structured relational reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A transport dataset is loaded into the sandbox as a graph (e.g., stations as nodes and tracks as edges). The nodes have properties like 'name' and 'zone', while edges have 'distance' and 'time' weights.
* **Real Question**: What are the three quickest ways to go from Paddington to London Bridge?
* **Real Trajectory**: The agent identifies the source and target nodes by searching for 'Paddington' and 'London Bridge' in the station name records. It recognizes that 'quickest' requires minimizing the 'time' attribute on edges. It invokes a k-shortest path algorithm (like Yen’s) with the parameter k=3, using 'time' as the weighting property. It extracts the resulting path sequences and their total costs, then summarizes the routes for the user.
* **Real Answer**: Route 1: Paddington -> Edgware Road -> Baker Street -> ... -> London Bridge (18.0 mins); Route 2: [Alternative Path 2]; Route 3: [Alternative Path 3]
* **Why this demonstrates the capability**: The agent must perform pathfinding reasoning by choosing a specific multi-path algorithm and mapping the layman's term 'quickest' to the correct numerical 'time' property. This demonstrates the transition from a spatial intent to a constrained graph-search operation.
---
**[Case 2]**
* **Initial Environment**: A social interaction network is provided where nodes represent users and edges represent interactions (calls, messages).
* **Real Question**: Identify the top five most influential users who act as critical bottlenecks in the communication flow.
* **Real Trajectory**: The agent interprets 'influential' and 'bottleneck' as a request for centrality measures. It decides to run Betweenness Centrality to identify nodes that lie on the most shortest paths and PageRank to identify global importance. It executes these algorithms, sorts the results by the betweenness score, and selects the top five user IDs. It then cross-references these IDs with user metadata to return their names and explains their role as network bridge nodes.
* **Real Answer**: 1. User A (Score X), 2. User B (Score Y)... these users are critical bridges connecting disparate groups.
* **Why this demonstrates the capability**: Identifying 'bottlenecks' requires understanding relational influence (Betweenness) rather than simple count-based importance (Degree). The agent demonstrates relational reasoning by selecting the appropriate centrality metric to satisfy the user's specific workflow requirement.
---
**[Case 3]**
* **Initial Environment**: A complex historical dataset contains people and battles, forming a bipartite-style graph where edges link people to the events they participated in.
* **Real Question**: If we divide this network into three distinct communities, are 'Moat Cailin' and 'Shield Islands' placed in the same group?
* **Real Trajectory**: The agent identifies this as a community detection problem with a fixed cluster count. It selects an algorithm capable of partitioning the graph (like Louvain or an approximate k-cut) and sets the parameter k=3. After running the partition logic, it queries the group membership for the 'Moat Cailin' node and the 'Shield Islands' node. It compares their group IDs and finds they reside in different clusters, concluding with a negative answer.
* **Real Answer**: No, they are in separate communities.
* **Why this demonstrates the capability**: The task requires partitioning the global topology based on relational density. The agent demonstrates the capability by applying an unsupervised community detection algorithm to answer a specific membership query about hidden structural groups.

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
