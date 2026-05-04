# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Phrase the primary prompt leveraging casual, actionable vocabulary heavily implying a requirement to divide, simultaneously execute, or independently structure information retrieval. Synthesize queries specifically structured to omit explicit tool nomenclatures while firmly entailing that execution must involve multiple divergent facts.
  - Intentionally introduce Structural Template requisites, obligating orchestrators to map comprehensive procedural documents demanding asynchronously fetched baseline data variables seamlessly inputted within.
  - Design 'Shared Resource Bottlenecks' where multiple players in the request all depend on a single, time-varying variable (like a budget or global timeframe). Success must require the agent to fetch that variable once and concurrently use it as a 'Golden Source' for parallel sub-agents.
  - Construct double-disambiguation prompts deliberately requiring distinction across entities sharing identical nomenclatures originating from deeply disparate sources mandating simultaneous external fetches.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
