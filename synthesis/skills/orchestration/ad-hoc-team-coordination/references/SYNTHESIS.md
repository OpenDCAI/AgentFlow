# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate the prompt as a 'Dynamic Teaming Challenge' where the goal is complex (e.g., 'Launch this pharma product') and the team composition is guaranteed to change mid-way. Specify that 'new experts will join and some will leave,' forcing the agent into a 'Monitor and Re-delegate' loop. This setup ensures that if the model doesn't use its 'get_available_agents' and 'AssignTask' tools reactively, it will fail to leverage the new expertise or find itself blocked by a missing worker, failing the completion metric.
  - Incorporate a 'Preference Drift Trap' where the user request starts with one clear priority (e.g., 'Do it cheap') but the stakeholder sends a message mid-run changing the priority to something conflicting (e.g., 'Actually, we need this done safely and by the book'). The model must be judged on its ability to notice the communication, update its internal preference vector ($U$), and immediately re-calibrate the task graph (e.g., adding a 'Safety Audit' node). This perfectly tests the 'Non-Stationary Multi-Objective Optimization' aspect of the management challenge.
  - Design 'Opaque Dependency Puzzles' where the high-level goal (e.g., 'accrue university accreditation') cannot be solved in a flat pass. The environment should contain a 'Hierarchy of Credentials' discovered only through inspection, requiring the agent to build a multi-layered DAG ($G$). Success is characterized by the agent identifying that it needs the 'Admin records' before it can assign the 'External Reviewer' task, mandatorily testing the compositional reasoning for hierarchical decomposition.
  - Use 'Layman Project-Management Phrasing' to describe the need for coordination, such as 'take charge of this group,' 'make sure the right people are doing the right things,' or 'give me a clear map of how the work is moving.' This ensures the system maps disorganized human ambitions onto the formal POSG architecture of task graphs and worker sets. To elevate difficulty, add a hard constraint like 'no human worker can be assigned more than two tasks at a time,' pushing the agent toward intelligent parallel scheduling across its AI-worker sub-pool.
  - Implement 'Adversarial Resource Failures' where one crucial AI worker 'crashes' or returns an error during a major task. The orchestrator must handle the failure, identify the 'Impediment,' and communicate a recovery plan to the stakeholder (e.g., 'The analyst failed, so I am moving the human consultant to the analysis track'). This verifies the agent acts as a professional 'Manager' that provides resilience and transparent oversight rather than just a simple tool-caller that stops when things go wrong.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
