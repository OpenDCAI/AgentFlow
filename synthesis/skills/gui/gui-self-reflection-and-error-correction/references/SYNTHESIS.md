# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Input Context Pollution Seeding. Design the synthetic environment to have the target input field pre-filled with a 'Stale Metadata' string or a prefix (e.g., 'http://', '#', or a default username). You should prompt the agent with a goal that requires the literal full string, forcing it to decide whether to clear or append to the existing text. For example: 'Change the URL to https://example.com' when the box already has 'http://' written inside.
  - Hostile UI Interstitial Seeding. Assemble the GUI environment to automatically trigger a large, non-closable interstitial advertisement or pop-up modal that covers the primary target button. You must ensure the modal has a small but visible 'Close' or skip-link to test the agent's patience and obstacle-removal logic. A concrete question would be: 'Update the settings to Portuguese, but deal with any advertisements that might get in the way first.'
  - Widget Format Constraint Injection. Formulate tasks using complex widgets like date-pickers where the prompt specifies a date, but the environment's internal logic requires a specific non-standard format (e.g., YYYY/MM/DD). You should include a subtle hint in the placeholder text to see if the agent picks it up. For instance, 'Set the arrival to May 5th' on a screen where the box shows 'DD-MM-YYYY' helps test format-aligned reflection.
  - Simulated Action-Failure Retries. Construct the trajectory JSON such that the agent's first click on a target 'fails' to trigger a state change (simulating a lag or misclick), requiring a retry. Turn 1 should show a valid click but no UI update, and Turn 2 should show the agent reflecting: 'The state didn't change; I will click 'Save' again'. This ensures training for one-shot failure resilience.
  - Post-Action Format Verification. Design the 'Answer' to require a character-perfect extraction of the result to prove the agent resolved any formatting conflicts correctly. The answer should not be a guess; it must be the string as rendered in the corrected widget. Use phrasing like 'Tell me exactly what is in the box now' to ensure the agent verifies that clearing the pre-filled text was successful.
  - Suboptimal Strategy Trap. Place a button that looks correct but is 'disabled' or 'read-only' in the environment, with a secondary 'Edit' mode required to unlock it. This tests if the agent reflects on the 'Greyed-Out' state and searches for an 'Unlock' button rather than clicking the disabled target. For example, 'Edit the profile' when the save button is disabled until 'Edit' is toggled, measuring state-aware self-correction.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
