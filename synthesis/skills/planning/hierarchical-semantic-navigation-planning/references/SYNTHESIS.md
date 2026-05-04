# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate 'User Demand Scenarios' by providing a detailed User Role Profile (Age, Occupation, Lifestyle) and an abstract high-level goal. The prompt must force the agent to use its 'Scene Tree' to translate the vague lifestyle need into a specific topological destination. For example: 'I am a Graphic Designer who needs an inspiring afternoon; find a spot where I can work with natural light and guide me there.'
  - Implement 'Hierarchical Retrieval Triggers' in the synthesis pipeline, requiring the agent to output its search progress: Rough Instruction -> Target Zone -> Target Viewpoint -> Target View -> Refined Instruction. This ensures the synthetic data contains the internal 'coarse-to-fine' reasoning trace. Commands like 'Retrieve the best functional area from the scene tree before listing the objects' enforce this structural goal.
  - Insert 'Semantic Contrast Traps' where the house contains two similar rooms (e.g., two bathrooms), but only one satisfies the specific user constraint (e.g., 'the one with the vessel sink'). The synthesized QA must show the agent uniquely identifying the correct room through attribute-aligned retrieval. This specifically punishes shallow planning that stops at the first 'Bathroom' zone it finds.
  - Embed 'Connectivity-Aware Routing' instructions that require the agent to describe navigation as a transition between functional zones. Instead of 'Turn right', the instructions should read 'Exit the living room and enter the hallway connected to the study.' This target's the agent's ability to interpret global layout and zone connectivity rather than just local pixel-level movement.
  - Structure the JSON output to include 'Ground Truth Trajectories' calculating the shortest path geodesic distance between the starting node and the destination viewpoint. This reinforces the 'Plan-as-Primary-Artifact' constraint by tying the semantic language instruction to a verifiable spatial-temporal movement program. A compliance failure occurs if the synthesized trajectory skips nodes or violates environment physics.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
