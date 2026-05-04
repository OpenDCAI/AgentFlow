# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate 'High-Throughput GUI Requests' that explicitly demand the agent perform multiple operations in a compressed timeline (e.g., 'Batch the next few steps to minimize wait time'). Use phrases like 'Do it in one go' or 'Don't wait for the refresh' to trigger the speculative orchestration. An example is: 'Change the font, color, and size of the title immediately without pausing between steps.'
  - Synthesize 'Composite UI Workflows' where the user describes a goal using a series of 3-5 interdependent GUI actions in a single sentence. For example: 'In the settings menu, find the privacy tab, toggle the location switch, and then save.' This structure naturally targets the agent's ability to group actions based on the initial 'Settings' observation, minimizing the number of planning cycles.
  - Introduce 'Efficiency-Weighted Scoring Traps' into the answer requirements, where a 'Correct' answer is only one that completes the task in under a specific step threshold (texp). Specify: 'Humans do this in 4 steps; try to match that speed.' This punishes agents that default to cautious1-step-at-a-time logic and rewards those that successfully use speculate-batching to reach the human baseline.
  - Embed 'UI-State Divergence Traps' where a batch of 3 actions is plausible, but the 2nd action triggers a minor unexpected change (like a different sub-menu). The synthesized QA must show the agent attempting the batch, detecting the diverged state via its control-validator, and immediately halting for a 'Reactive Repair.' This ensures the agent learns that efficiency must be balanced with environment-grounded awareness.
  - Structure the JSON output to include a 'Batch Artifact' key that clusters sequential `action` objects under a single `reasoning` thought. The synthesized trajectory must use this format rather than a flat step-by-step list to reinforce the 'Plan-as-Primary-Artifact' rule. A compliance failure occurs if the generated data shows one thought per click for a predictable GUI routine.
  - Design 'Search-and-Apply' scenarios where the agent must fetch a variable (like a code or name) and then apply it across several fields (e.g., filling a form). The prompt should request: 'Pull the data from the first app and fill it into all these fields in the second app in a single burst.' This targets cross-app batching efficiency, using the extracted variable consistently across several grouped actions.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
