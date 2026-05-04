# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Engineer 'Asymmetric Information Gaps' where the user request provides a high-level goal (e.g., 'gather all data from the latest health survey') but the environment contains no direct links or file paths. This forces the agent to use the 'Environment Exploration' and 'Research' phases to discover the starting point. Success is awarded when the agent uncovers the hidden API documentation or the nested site structure autonomously. For instance, hide the fact that data is stored in an S3 bucket accessible via an unindexed link.
  - Implement 'Multi-Modality Friction' by provided environments where the easiest path (e.g., a simple CSV export button) is broken or absent. The prompt should force the agent to use a more complex modality, like writing a recursive spider or an API harvester, to achieve the objective. The question rewards the agent for identifying the 'engineering wall' and choosing a robust technical solution. This ensures the synthetic data tests resilience over easy pattern matching.
  - Incorporate 'Symbolic-Style extraction' requirements where the agent must extract data into a specific, non-standard schema defined in the prompt. The user might ask for 'all papers where the primary author is from a specific university', requiring the agent to perform multi-hop reasoning between paper lists and author profile pages. This creates high-density training data for 'reasoning-intensive' data collection. A successful synthesis will result in a JSON showing how the agent 'connected the dots' between distinct web entities.
  - Design 'Scale and Rate-Limit Stressors' by specifying large requested datasets (e.g., '10,000 records') that would trigger standard anti-bot protections. The question should reward the agent for proposing and implementing 'Stewardship' features like exponential backoff, request batching, or header rotation. This allows the synthetic data to teach agents to operate responsibly in the open web. A specific requirement is: 'Your trajectory must explain why your script's delay settings are appropriate for the target server's safety policy.'
  - Require the final output JSON to include a 'Blueprint-to-Code Ledger' that maps specific HTML identifiers found during research to variables in the final script. For example, 'Variable: PaperTitle -> Selector: h3.title-text'. This documentation makes the synthesized data valuable for training models to verify their own web understanding. A requirement is: 'Every CSS/XPath selector used in the final script must be justified by an observed HTML fragment in the trajectory.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
