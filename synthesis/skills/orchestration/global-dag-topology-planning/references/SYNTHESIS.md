# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate the prompt as a 'Multi-Level Dependency Puzzle' where the user wants a final result that depends on several nested layers of information retrieval. Use phrases like 'I need to know X, but to find X you'll need Y, and Y is only reachable via Z.' This intentionally forces the model into a global planning state because it cannot even formulate a valid search query without understanding the 'leaf-to-root' dependency chain of the entire problem.
  - Incorporate a 'Parallelizable Constraint' by asking for a comparison of multiple entities that are logically independent (e.g., 'Compare the weather in three different cities and find the average'). This tests if the orchestrator can generate a branched DAG with three parallel root nodes instead of a lazy, sequential chain. The synthesis should judge the agent on its ability to maximize efficiency by dispatching all independent branches in the first level of the plan.
  - Design a 'Structural Trap' where two superficially similar tools exist, but only one is compatible with the downstream nodes in the DAG. For example, include 'General Search' (returns text) and 'Technical Search' (returns a JSON ID), where the next node *requires* a JSON ID. This forces the model to engage in 'Advanced Edge Prediction,' ensuring the selected node matches the exact data-flow expectations of its children in the graph topology.
  - Use 'Layman Graph Descriptors' like 'make a complete game plan,' 'draw me a map of how you'll solve this,' or 'show me the steps and how they connect.' This aggressively tests the translation layer, ensuring the agent maps casual human requests for 'planning' to the formal Directed Acyclic Graph architecture. To elevate difficulty, add a constraint like 'no more than 3 steps of latency,' which forces the agent to optimize the DAG's depth versus its width.
  - Implement 'Incomplete Parameter Baits' where the user asks for a result but 'forgets' one piece of required data that must be inferred from the tool schemas. The orchestrator should be pushed to autonomously insert a 'Discovery Node' into the DAG to retrieve that missing variable before the final synthesis node. This verifies 'Proactive Structural Planning,' where the agent builds a plan to find the 'keys' to the tools it wants to use, mirroring real-world complex orchestration.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
