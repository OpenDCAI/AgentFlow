# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate the question using a 'Logic-Dense Narrative' that requires the agent to handle multiple recursive or conditional dependencies simultaneously. Use prompts like 'Create a complex procedure for X and then dry-run it with an example to ensure it works.' This forces the agent to use its 'Perception' layer to verify its own drafting logic, mirroring the CODESIM framework.
  - Incorporate a 'Semantic Ambiguity Trap' where a common term (e.g., 'even integers') has a subtle domain-specific restriction (e.g., 'even digits within the numbers'). The user request should be slightly vague, requiring the agent to use its 'Problem Understanding' and 'Simulation' phases to uncover the true constraint. For example, 'Find the squares of 10 to 20' could mean the squares of the numbers OR the squares of the individual digits.
  - Design cases with 'Incomplete Specification' where the user's provided examples imply a rule (like tri(0)=1) that is not explicitly stated in the formula text. The agent must be forced to 'Refine' its plan after its first simulation fails to match the provided examples. This targets the 'Plan Validation' loop where the agent learns the true goal from the I/O mismatches discovered during dry-running.
  - Structure the required output to include a 'Step-by-Step Simulation' block and a 'Decision Format' (e.g., No Need to Modify vs Plan Modification Needed). This ensures the synthetic data captures the 'Verification' artifact required for training. A failure to output the decision token 'Plan Modification Needed' when a flaw is present makes the synthetic data non-compliant.
  - Include 'Counter-Intuitive Initialization' requirements where the starting state of a task (like starting a list with [1, 3] instead of [3]) is non-obvious. The prompt should ask for a multi-step plan, encouraging the agent to realize the deficiency of a simple 'Direct' approach during the simulation phase. An example is a task where the results must be returned in descending order but only even positions are allowed, creating a complex ordering dependency.
  - Use 'Layman Trigger Phrases' to hide the scientific intent of the capability, such as 'double-check your work in your head first' or 'run an example through your instructions to see if they hold up.' These requests must trigger the expert-level 'simulation-driven-stepwise-refinement' pipeline. This ensures the agent is actually performing 'Visual/Internal Trace' work rather than just following a conversational prompt.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
