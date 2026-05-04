# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Design prompts that use domain-specific 'layman goals' like bottlenecks, gatekeepers, echo-chambers, or power-brokers to describe graph targets. The user might say 'Find the person who controls the flow of information' while the data requires a Betweenness Centrality calculation. This forces the agent to use its mapping logic to bridge the gap between intent and relational math.
  - Create synthetic environments with 'Hidden Topological Distractors' where simple importance metrics conflict with sophisticated ones. For instance, include a node with the highest degree (most links) but very low PageRank (links lead to dead ends). Ask for the 'most influential' node to see if the agent blindly picks the busiest one or correctly uses PageRank for prestige.
  - Incorporate 'Pathing Trade-Offs' where different weights lead to different answers. Provide edges with both 'Distance' and 'Toll_Cost' and ask for the 'cheapest' route. This tests whether the agent integrates specific user-defined cost constraints into its algorithmic selection rather than defaulting to the shortest physical distance.
  - Mandate a 'Schema Audit -> Graph Projection -> Algorithm -> Interpretation' trajectory format in the synthesized JSON. The agent should first check if nodes and links exist, then define its graph object, then run the algorithm, and finally explain the IDs in natural language. This logical chain reflects the 'topology-aware' strategy required for complex relational data.
  - Include 'Community Membership Traps' where entities look connected but belong to different clusters due to low modularity links between them. Ask if two entities are in 'the same social circle,' forcing the agent to run a community detection algorithm like Louvain to see the hidden partitioning. This ensures the agent relies on the algorithm results rather than visual proximity in a small table sample.
  - Design 'Capacity/Flow Bottleneck' challenges where the agent must identify the limiting factor in a network. For example, provide a pipe network with 'diameter' attributes and ask for the 'maximum amount that can pass from A to B'. This tests if the agent can identify the 'narrowest' link on the primary path, measuring a specific kind of relational constraint reasoning.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
