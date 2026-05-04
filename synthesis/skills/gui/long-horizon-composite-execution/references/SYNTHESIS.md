# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Unstructured-to-Structured Planning Tasks: Design synthesis questions from intentionally low-quality, ambiguous, or incomplete real-world 'Reports' (like bug reports or project briefs). You should force the agent to use its 'Step Synthesizer' logic to reconstruct a detailed plan from 1-2 sentences of vague text. For example: 'Reproduce this crash: [User says it crashes when I jump near water]' requires the agent to find the specific mob/version context.
  - External Documentation Dependency Seeding: Formulate tasks where the final success depends on a specific technical detail only found in a provided auxiliary 'Wiki' or 'Manual' file. You must make the task impossible to solve through general knowledge alone, forcing the agent to use RAG. For instance, a task requiring a specific 'Item Tag' that only exists in version 24w44a.
  - Complexity-Layered Milestone Scheduling: Create tasks that require at least 3 distinct sub-goals across a single or multiple applications with dependencies (e.g., Check Date -> Set Alarm -> Recommend Activity). You should structure the environment so that the output of step 1 is the mandatory input for step 3. This tests the durability of the agent's 'Memory' and 'Causal Reasoning' over 30+ steps.
  - Command-Line Shortcut Incentivization: Design environments that offer both a 'Difficult GUI' path and a 'Simple Command' path for the same outcome. You should phrase the question to imply a need for 'reliability' or 'repeatability,' rewarding the agent for choosing the command shortcut. For example, 'I need a 100% reliable way to set this world to Rain every time' encourages the use of `/weather rain` over searching menus.
  - Version-Locked Intent Injection: Craft synthesis questions that mention a specific software version or build, requiring the agent to audit the environment before acting. You must ensure the environment matches or mismatches the version to test 'Grounded Infeasibility' alongside 'Long-Horizon Execution'. A concrete challenge is: 'Reproduce this bug for version 1.20; first, verify if we are in 1.20 or 1.21.'
  - Reasoning-Heavy JSON Formatting: Explicitly require the 'trajectory' sections of the JSON output to include a 'Thought' block for every action that analyzes naming conventions, hierarchy depth, and causal intent. You should provide examples where the agent justifies its 'Decision Making' (e.g., 'Choosing command over click to avoid aiming error'). This ensures the synthetic data trains the agent to activate its internal self-refinement and planning mechanisms.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
