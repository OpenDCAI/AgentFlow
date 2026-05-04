# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate 'Action-Dense' Composite Instructions: Create user queries that demand a series of repetitive or logically linked sub-tasks, such as 'Add these 4 different books to cart' or 'Update my address and then my phone number and then my password.' This structure forces the solver to utilize programmatic macros to keep the plan horizon manageable and efficient. A successful response will show the agent iterating over the list of items using a single macro call for each.
  - Incorporate Layman Macro-Triggers: Use casual, non-expert language to describe the need for a shortcut or routine, such as 'Find a way to do this for all my entries' or 'Save the steps for searching here so you can do it for the others.' This tests the agent's ability to map vague NL needs to its expert-level programmatic skill library. For instance, the prompt 'Do the address thing for both billing and shipping' should trigger the `update_address_details` logic.
  - Introduce 'Structural Divergence' Traps: Design scenarios where the same macro works for items A and B but fails for item C because of a website design change (e.g., a missing button or a different popup). The question should require the agent to execute the macro, observe the failure, and then 'Update' or 'Refine' its plan either by creating a new skill or reverting to primitives. This targets the 'online adaptive' and 'skill revision' mechanics noted in the research.
  - Embed Mandated Verification Checkpoints: Explicitly ask the agent to 'Verify that each item was correctly added before moving to the next' within the question prompt. This ensures the synthetic data reinforces the closed-loop, verified planning paradigm where each macro execution is gated by a success observation. For example, 'Check order #1, then check order #2...' forces a sequential, state-dependent trajectory.
  - Structure the Output with Explicit Macro Syntax: Ensure that the synthesized trajectory in the QA pair uses pseudo-code or Python-like function calls (e.g., `search_and_add("Mug")`) rather than English descriptions for its actions. This reinforces the 'Plan-as-Primary-Artifact' constraint by making the programmatic abstraction the center of the agent's output. A failure to use the skill-library syntax results in a non-compliant synthetic data point.
  - Simulate 'Cross-Website Generalization' Scenarios: Create questions where the agent is on a new website (e.g., 'Target' instead of 'OneStopMarket') and must decide which of its previously learned skills are still applicable. The prompt should mention 'You've searched for products before on other sites; try doing it here.' This forces the agent to demonstrate 'Common Skill Transfer' or 'Incompatible Skill Identification' as described in the benchmark.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
