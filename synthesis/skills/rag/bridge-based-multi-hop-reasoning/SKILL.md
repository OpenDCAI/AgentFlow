---
name: bridge-based multi-hop reasoning
description: Use this skill when the user wants 'connect the dots' questions, hierarchical path-traversals, or questions about navigating a sequential process. Trigger it for natural-language requests like 'multi-hop questions', 'find a way to get to...', 'show me the steps to...', 'force the model to follow a shared thread across docs', or 'test if it can find the path even if some instructions are missing'. It targets structural traversal across documents, procedural manuals, or interface states.
---

# Skill: bridge-based multi-hop reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to answer by systematically traversing sequential bridge nodes, mediating causal variables, explicit hierarchical document pointers, or state-transition graphs (such as UI Transition Graphs). The agent must formulate a reasoning chain connecting sequential facts, linking intents to multi-step trajectories via intermediate milestones, or pivoting to transitive properties when direct primary links are fragmented.
* **Dimension Hierarchy**: Multi-Source Evidence Composition->Cross-Document Synthesis->bridge-based multi-hop reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A bounds news corpus containing one article about the Federal Reserve raising interest rates after booming home prices and another article about future Federal Reserve rate decisions depending on incoming economic data. The shared bridge entity is the 'Federal Reserve'.
* **Real Question**: Does the article from Fortune suggest that the Federal Reserve's interest rate hikes are a response to past conditions, such as booming home prices, while The Sydney Morning Herald article indicates that the Federal Reserve's future interest rate decisions will be based on incoming economic data?
* **Real Trajectory**: The agent identifies the shared bridge entity (Federal Reserve) across both distinct documents. It aligns the past-condition claim to Document A and the future-condition claim to Document B, combining them over the single bridge node to evaluate the joint premise.
* **Real Answer**: Yes
* **Why this demonstrates the capability**: The answer emerges only after the agent explicitly identifies that both articles independently discuss the same bridge entity and then compares the two bridged claims. Neither article alone settles the combined question, making it a canonical bridge-based multi-hop evaluation.
---
**[Case 2]**
* **Initial Environment**: A RAG environment containing a transition graph of a technical application represented as structured text. Nodes are 'Screens' containing button labels and edges are 'Interactions'. One path leads from 'Home' to 'Privacy Policy' through several nested menus.
* **Real Question**: How can I view the Privacy Policy for the Pomodoro Reading App?
* **Real Trajectory**: The agent identifies the 'Home' screen, finds the 'Me' button to access the profile. Inside Profile, it identifies 'Settings', then navigates through the 'About' section to finally locate the 'Privacy Policy' leaf node.
* **Real Answer**: Click 'Me' -> Click 'Settings' -> Click 'About Tomato' -> Click 'Privacy Policy'.
* **Why this demonstrates the capability**: This illustrates intent-to-trajectory pathfinding as a form of multi-hop bridging. The agent must traverse four distinct hierarchical levels where the final answer is deeply embedded, requiring it to follow explicit structural anchors rather than a single-hop keyword match.
---
**[Case 3]**
* **Initial Environment**: A fragmented knowledge graph of a financial app where the direct link between 'Search Result' and 'Purchase' is missing. The graph provides 'intent-milestone' pairs that suggest sub-goals for various tasks.
* **Real Question**: Show me the operations required to find and select a US stock fund.
* **Real Trajectory**: The agent identifies the high-level intent. It decomposes it into milestones: [Enter Financial Menu], [Open Search], [Locate Fund]. It retrieves the steps for each milestone from the graph, bridging the missing direct transitions via logical step interpolation.
* **Real Answer**: 1. Click 'Financial Management', 2. Click Search Bar, 3. Input 'US Stock Fund', 4. Select the matching fund from the list.
* **Why this demonstrates the capability**: This demonstrates 'Intent-guided Milestone Decomposition'. The agent overcomes a fragmented graph by breaking a task into sub-goals and finding the sequential actions to satisfy each, proving it can navigate a multi-hop traversal even when the corpus has breaks requiring milestone bridging.

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
