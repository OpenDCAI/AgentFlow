# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Draft 'Multi-Domain Composition' questions that implicitly require bridging information across 2 or more distinct servers (e.g., pairing academic papers with internal company reports). Intentionally use natural language that avoids naming the servers (Arxiv, Notion, etc.) to force the model to identify the tools based on functional descriptions. This tests if the agent can resolve 'Unknown-Tools' by mapping the goal to its provided toolkit.
  - Inject 'Conditional Subgoals' and 'Deep Research Trees' where the user request provides a hint that requires a research step to unlock a secondary query parameter (e.g., 'Find the scientist born in a city with >5M English speakers...'). This forces a 3-6 step trajectory where the intermediate observation strictly locks the required argument for the final turn. This ensures the synthetic data captures deep multi-hop constraint pruning.
  - Incorporate 'Distractor-Heavy Tool Surfaces' by providing a tool-set configuration where 50% of the tools are similar in name to the target tools but have slightly different functions. For example, include a 'search-history' tool alongside a 'search-messages' tool to see if the agent can correctly identify the one that fits the prompt's context. This pushes the model toward higher 'Discovery Precision'.
  - Use 'Layman Goal Descriptions' that are tool-dependent and time-invariant, focusing on 'Actionable Results' rather than technical requests. Instead of saying 'Use the Arxiv tool to find...', say 'I need to know what the current consensus is on X according to the 2024 literature.' This tests the agent’s ability to map a messy human desire into a professional multi-step tool workflow.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
