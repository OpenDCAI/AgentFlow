# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - **Ask for answers that depend on relations.** Generate questions whose answers require following edges, composing relations, or extracting a connected subgraph rather than reading one attribute in isolation. This is the simplest way to make the graph structure matter. Layman triggers often sound like 'who is connected to whom' or 'what is related to what'.
  - **Keep the support graph small but connected.** When synthesizing a final sample, ensure the needed nodes and edges form a manageable support subgraph that can be verbalized in the trajectory. This improves explainability and reduces annotation burden. Huge diffuse graphs weaken supervision quality.
  - **Introduce plausible structural decoys.** Include nearby nodes or edges that are semantically related but not part of the correct reasoning path. This trains the agent to avoid inventing or following the wrong relation chain. Decoy structure is the graph analogue of textual distractors.
  - **Vary argumentative, spatial, and factual relation styles.** Produce a balanced mix of stance graphs, scene graphs, and knowledge graphs so the skill captures several flavors of relational reasoning. This prevents overfitting to only family-tree or only spatial cases. A broad relation mix best reflects real graph QA workloads.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
