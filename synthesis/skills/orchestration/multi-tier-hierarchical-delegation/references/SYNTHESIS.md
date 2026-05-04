# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate 'Cross-Domain Dependency' prompts that require information from both a professional/private source and a timely/public source to succeed. For example, ask about 'the current market price of the chemical mentioned in Project Alpha's internal specs,' forcing the delegator to call the Local Agent first and then the Web Agent. This setup ensures that if the model doesn't partition the task, it will either miss the internal spec or the real-time price.
  - Incorporate an 'Action-Space Trap' by providing a toolset of 20+ specialized search tools (e.g., 5 graph tools, 5 chunk tools, 10 web tools) and judging the model on whether it partitions them into specialized sub-agents. The user-facing prompt should be complex (e.g., 'research this topic across all our sources'), and the model is penalized if it attempts to manage all 20 tools within a single flat context window. This rigorously tests the 'Hierarchical Advantage' for managing complex tool ecosystems.
  - Design 'Ambiguity-to-Expert' puzzles where the user's question contains a term with different meanings in Local and Web contexts (e.g., 'Project X' might be an internal file and a public movie). The orchestrator must be pushed to dispatch to *both* agents simultaneously to disambiguate the intent through consensus. Success is defined by the agent identifying the correct 'Project X' based on the environmental cues provided in the sub-agent observations.
  - Use 'Layman Team Directives' like 'put your research team on this' or 'check the corporate records and then the internet' to test the translation of casual requests into hierarchical agent calls. This aggressively tests whether the agent maps human 'team-based' metaphors to functional `<local_agent>` and `<web_agent>` code implementations. To elevate difficulty, supply a prompt like 'don't bore me with the search logs, just give the outcome,' which mandates the use of the Refiner mechanism.
  - Implement 'Source Conflict' scenarios where the Local Agent provides a secure fact and the Web Agent provides a popular but incorrect 'hallucinated' fact. The model must be judged on its ability to prioritize the Local Source (Private Data) as the authoritative ground truth while using the Web source only for supplementary context. This verifies that the hierarchical delegation includes a 'Source Priority' logic that protects the reliability of the terminal result.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
