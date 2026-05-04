# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Develop 'Granularity-Depth Challenges' by asking for a complex multi-part design (e.g., 'Design a sustainable power grid') where a standard one-shot response will inevitably produce shallow, non-executable stubs. The prompt must demand 'runnable code for every component' and 'alignment with industrial standards,' forcing the model to initiate a hierarchical MAS loop involving specialized Coder and Reflector roles. This ensures simple LLM chatter is punished while structured, iterated engineering synthesis thrives.
  - Incorporate a 'Mode-Collapse Trap' where the user explicitly requests at least three diverse design alternatives based on different priorities (e.g., 'cheap', 'fast', 'small'). The orchestrator must be pushed to demonstrate 'Pareto-Variant Generation'—maintaining three distinct DSGs in memory and refining each independently before a Ranker/Meta-Reviewer selects the winner. This perfectly tests the system's ability to avoid focusing on the first available answer and instead explore the full design-space.
  - Design 'Cahier des Charges (CDC) Inconsistency' puzzles where the provided requirement handbook contains two conflicting rules (e.g., 'Must be lightweight' vs 'Must exclude all aluminum'). The orchestrator must be judged on its ability to trigger a 'Refinement Debate' between specialists to resolve the conflict, eventually reaching a 'Consensus Document' that justifies the selected materials based on requirement priority. This confirms the system acts as a professional 'Clinical/Engineering Strategist' rather than a naive instruction-follower.
  - Use 'Requirement-ID Traceability' constraints by asking the agent to 'link every node to an SR-XX ID' from a massive provided requirements list. During the 'Synthesis' phase, intentionally provide a 'Distractor Requirement' (e.g., SR-99) that is irrelevant to the task to see if the Reflector/Meta-Reviewer catches the 'Traceability Hallucination.' This ensures the synthetic data captures the 'Audit and Grounding' aspect of refinement where precision on metadata is as important as the code itself.
  - Implement 'Level-1 to Level-2 Evolution' traps where the initial generation is correct in logic but contains a 'Dimensional Inconsistency' (e.g., missing a panel-area term in a W calculation). The Reflector must be prompted to catch this specifically, and the Coder must be judged on its ability to 'surgicaly fix' the math within the Python script without rewriting the rest of the valid CLI structure. This verifies high-fidelity state-preservation during the refinement cycles.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
