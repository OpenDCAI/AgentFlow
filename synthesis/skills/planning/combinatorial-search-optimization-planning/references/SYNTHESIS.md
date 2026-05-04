# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Non-Euclidean Asymmetric Contexts: Design routing and transport questions where the distance A-to-B is fundamentally different from B-to-A. Use natural language phrasing and industrial motifs like 'stacker crane mechanics', 'one-way canal systems', or 'wind-current affects on flight time'. This forces the agent to use its 'Structural Diagnostics' to bypass standard 2-OPT assumptions.
  - Extreme Scale Mapping (10k+ nodes): Compose questions involving massive-scale graphs that explicitly exceed the 'Greedy' or 'Neural' memory limits mentioned in the paper. Demand that the agent 'solve the entire 10-million city tour' or 'find the largest set in this 8-million node SAT challenge'. This compels the agent to synthesize reduction or hierarchical decomposition plans.
  - Steiner point discovery prompts: Architect tasks where the agent must connect terminals but *can* invent or select intermediate nodes to optimize cost. Use motifs like 'telecom relay setup' or 'pipeline plumbing' to emphasize that the goal is the *minimum cost connectivity*, not just a direct path. This forces the model to perform combinatorial search over an open node pool.
  - Algorithm-Selection Traps: Include prompts with 'hidden structural pitfalls' where a locally appealing path leads to a global disaster (e.g., SAT-logic conflicts). For instance, describe a graph that looks like a simple circle but contains logical constraints that prevent simple traversal. Demand a 'step-by-step search algorithm' to see if the agent can find the global solution through lookahead.
  - NP-Hard Optimization with Bounding: Create questions for Bin Packing or Facility Location where the user demands the 'theoretical minimum' number of bins. Provide a list of weights and a capacity, explicitly stating 'Find a way to use only 3 bins if at all possible'. This forces the synthesizer to utilize 'Branch and Bound' logic to check if a specific goal state is even reachable.
  - Grounded Plan-as-Primary-Artifact Output: Structure the prompt to mandate that the agent's FINAL answer is an executable sequence of selections or a specific topological layout (e.g., full Sudoku grid or TSP route list). Reject any open-ended advice; ensure the LLM must generate a highly deterministic JSON mapping of the variable assignments or path indices.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
