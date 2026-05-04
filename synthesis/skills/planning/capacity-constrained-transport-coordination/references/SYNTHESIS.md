# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write the question so that the target capability, **Capacity-Constrained Transport Coordination**, is the shortest path to success. Start from the approved trajectory and expose just enough of the environment that the solver must reconstruct the same dependency chain, while hiding any gratuitous hints that would collapse the reasoning. For example, give the real state facts or tool-accessible fields, but do not narrate which option is best.
  - Introduce one controlled trap that specifically punishes shallow planning. The trap should be a realistic near-miss, such as a locally convenient but globally invalid move, a retrieved option that fails one hard constraint, or a sequence that becomes impossible because an enabling step was skipped. For example, a hotel with the wrong minimum-night policy or a tempting direct placement that violates reachability works well.
  - Keep the answer format tightly coupled to the approved trajectory. If the capability is about full-plan generation, ask for the valid plan or the next several actions; if it is about plan validation, ask for the corrected or feasible sequence and ensure the answer can be matched against the exploration trace. For example, do not ask for open-ended advice when the seed supports a precise action program.
  - Preserve realism and scoring clarity at the same time. Use ordinary language that a non-expert would naturally write, but make sure the hidden grading logic still depends on the approved state changes, retrieved facts, or constraints rather than on style. For example, 'Help me plan this trip without flights and under budget' is better than a benchmark-style formal instruction if both remain equally auditable.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
