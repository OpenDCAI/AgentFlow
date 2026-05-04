# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Incorporate 'Journalistic 5W1H' prompts that force the agent to categorize its response into standardized investigative bins. The question should demand a summary that explicitly identifies the Who, What, Where, When, and Why of the events described. This tests the agent's ability to selectively retrieve information based on established structural importance rather than simple word frequency. For instance: 'Write a news summary that answers the 5W questions specifically for this local event report.'
  - Embed 'Hard Character Limit' constraints (e.g., 'maximum 700 characters') to test the agent's ability to perform extreme data compression. This forces the model to move beyond simple paraphrasing and into strategic clause-pruning. A practical prompt would be: 'Provide a bulleted list of the key facts, but ensure the entire response is under 500 characters including spaces.' This creates a high-pressure environment for checking state-tracking and budget management.
  - Design 'Style-Shift' requirements that force the agent to adapt the tone and vocabulary for a specific reader (e.g., 'layman terms' or 'non-expert audience'). Synthesize questions that provide a highly technical or academic document and require a summary meant for a high-school student. This tests the semantic-mapping capability of the agent. An example is: 'Explain this medical study on vaccination in plain language while keeping the summary to exactly three points.'
  - Seed 'External Knowledge Traps' by using documents about famous events but with slightly altered details compared to real-world facts. The prompt should ask the agent to summarize the document *only* based on the provided text, punishing the use of outside information. This measures the agent's 'Factual Faithfulness' to the source context over its internal memory. For example, provide a modified report about a space launch and check if the agent corrects it with its own knowledge (a failure).
  - Enforce 'Bulleted Format' constraints to verify internal structural formatting controls. The question should command the agent to avoid prose and strictly use a list format for its output. This ensures the data is suitable for training models on structured, bite-sized information consumption. A strong synthesis prompt is: 'Identify the three most impactful causes of the production drop listed in this report and present them as a clean bulleted list.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
