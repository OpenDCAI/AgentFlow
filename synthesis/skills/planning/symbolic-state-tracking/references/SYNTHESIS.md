# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write the question so that the objective of Symbolic State Tracking is the shortest and most necessary path to success. Start from the approved trajectory and expose just enough of the beginning environment layout that the solver must reconstruct the strict sequence of changes. For example, supply initial state conditions but strictly do not narrate the intermediate configurations required to solve the puzzle.
  - Introduce semantic cross-wiring, obfuscated entities, or randomized gibberish tokens (e.g., 'String_001') for objects or geographic nodes to challenge pure planning logic. This forces the solver to rely entirely on the provided interaction rules rather than its vast pre-training associations with everyday words. Instead of asking to 'Pick up the apple', ask to 'Apply function lambda to entity beta' while defining the precondition effects.
  - Embed one controlled logical trap that specifically punishes a shallow planning attempt lacking robust state-tracking. The trap must be a realistic near-miss, such as a locally convenient placement that immediately fails a hard availability constraint or a spatial corridor that looks direct but is blocked later. Placing a block exactly where an upcoming large block needs to rest serves perfectly here to trick simple LLMs.
  - Formulate questions that explicitly require the agent to 'update its mental map', 'print its state array', or 'sketch its progress' at specific intervals (e.g., every 3 steps). Use natural language such as 'Tell me where you are and show me your path so far after every few turns' to trigger the interleaving of text and latent state storage. This ensures the synthetic data captures the persistent internal state tracking mechanic.
  - Preserve rigorous formatting and scoring simplicity without sacrificing user-facing realism. Keep the answer format tightly coupled to the approved trajectory, requesting either validation of an exact sequence or the specific subsequent chain of valid moves. The generated data must read casually yet harbor hidden mathematical or relational grading logic totally reliant on continuous predicate checks.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
