# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Engineer 'Multi-Stage Knowledge Gaps' by providing a user prompt that lacks both the 'Symptom' (e.g., missing error log) and the 'Target' (e.g., missing file path). This forces the agent into a multi-turn dialogue where the first turn might identify the file and the second turn might identify the logic error. Success is rewarded when the agent recovers the ground truth requirements through a structured 'Observation-Inquiry-Action' chain. For example, the user proxy should hold the file `astropy/utils/misc.py` and the fact that `@property` is the issue.
  - Include a 'User Proxy Configuration' in the environment that is instructed to be 'Helpful but Passive'. The proxy should only reveal 100% of the information if the agent's question is specific and technical. If the agent asks 'What's the bug?', the proxy should give a vague answer; if the agent asks 'Which class is causing the metaclass error?', the proxy should provide the file name. This creates a realistic 'clarification pressure' that rewards precise questioning.
  - Design 'Red Herring Files' in the repository that share identical names with the target but are functionally unrelated. For instance, have two `utils.py` files in different subdirectories. The agent must interact to clarify which specific module the user is concerned with to avoid a 'wrong file' patch. This tests the agent's 'Navigational Specificity' and ensures it doesn't just guess based on the first search result.
  - Require the final output JSON to include an 'Information Gain Log' that explicitly lists which pieces of information were moved from the 'User Proxy' to the 'Agent's Context' during the interaction. Each trajectory step involving a user response must record the specific detail acquired (e.g., 'Retrieved: Python version 3.7'). This provenance data is critical for evaluating how well the agent is 'leveraging' the interaction to bridge the underspecificity gap.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
