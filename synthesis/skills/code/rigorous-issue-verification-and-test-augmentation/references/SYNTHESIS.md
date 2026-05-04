# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Engineer 'Asymmetric Knowledge Gaps' by providing a user prompt that describes a behavioral symptom (e.g., 'the app crashes on large files') but withholds the exact line location. This forces the agent to use the 'Localization' and 'Action Planner' phases to bridge the gap. Success is rewarded when the agent recovers the ground truth repro-logic through a structured 'Search-Plan-Implement' chain. For example, hide the fact that the error happens in 'io_utils.py' and see if the agent discovers it.
  - Implement a 'Heterogeneous Prompting Requirement' in the synthesis loop to generate diverse ensemble candidates. The instructions should command the agent to generate multiple test variations by selectively including or excluding 'Focal' versus 'Test' context. This mimics the successful 'Otter++' ensembling strategy, where the best test is selected based on execution feedback. This creates high-density training data for 'Inference Scaling' where agents learn to pick the best logic from multiple attempts.
  - Incorporate 'Implicit Dependency Traps' by provided issue descriptions that require specific third-party libraries not mentioned in the existing test file. The question should reward the agent for correctly identifying the need for 'numpy' or 'pandas' and using the 'Import Fixing' step to resolve it. This ensures the synthetic data captures the 'real-world messiness' of repository maintenance where requirements often diverge from the current environment state.
  - Require the final output JSON to include a 'Fail-to-Pass Verification Matrix' in the trajectory that tracks the status of the new test on the 'Cold' (buggy) versus 'New' (fixed) code. Each trajectory step involving an execution must record the exit code and exception type. This provides a high-density signal for reward models to distinguish between 'Syntactic Success' and 'Logical Reproduction'. A requirement is: 'Every reproduction test must be justified by an observed stack-trace on the baseline version.'
  - Standardize the desired response to follow a 'Prior Function Pointer' format for test insertion. The agent must specify the name of the existing function after which the new test should be added. This forces the agent to maintain a precise mental model of the test file's structure and ensures the resulting patch is 'ready-for-review'. A specific instruction is: 'Identify the exact class name and neighboring function to ensure your patch integrates seamlessly into the legacy suite.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
