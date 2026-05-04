# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate 'Veracity-Challenged Verification Tasks' that provide the agent with a plausible-but-wrong trajectory and ask it to find the error. The prompt should include a 'Trajectory Summary' laden with specific failure modes (e.g., generic searches, reliance on blogs) and require the agent to produce a 'Corrective Instruction' list. This forces the agent to use the 'DeepVerifier' methodology to audit existing work.
  - Design 'Asymmetry-Dependent Inquiries' where the correct answer is hidden behind a complex technical matrix or a long-horizon 8.2M token document. The question should be: 'Based on the provided messy browser logs, identify if any Premature Conclusions were made regarding [Topic X] and issue sub-questions to fix them.' This evaluates the agent's ability to decompose a large, confusing context into atomic, verifiable sub-tasks.
  - Construct 'Rubric-Guided Self-Evolution Loops' where the agent is asked to solve a task, then verify its own work, and provide 'Feedback Instructions' for a retry. The synthesis must evaluate if the 'Feedback' contains suggest-answers and 'How-to-Fix' directions (e.g., 'Search site Y instead of Z'). This tests the 'Self-Evolving' capability by requiring the agent to generate high-leverage corrections from the environment's feedback.
  - Embed 'Authority-Based Triage Challenges' where two web sources provide different dates or figures for the same event. The agent must use 'Source Identification' and 'Decomposition' to determine which one is the primary registry. The prompt should look for a 'structured verdict' that explains WHY one source was discarded (e.g., 'Source A is a news summary; Source B is the original PDF filing').
  - Create 'Deception-Resistant Logic Scenarios' where the agent's previous answer was tricked by a 'Hallucinated or Overconfident' claim found on a social media page. The verifier must identify this 'Failure Point' and issue a corrective navigation path to a neutral, official clearinghouse. The final answer must be a verified JSON report mapping each claim to a 'Provenance-Checked' URL.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
