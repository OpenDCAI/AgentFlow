# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Create dynamic business work requests demanding multi-hop structural solutions. Require the construction of data artifacts demanding both pipeline ingestion steps and subsequent intricate transformations.
  - Embed necessary project-level abstractions such as complex macro directories, target credential files, or configuration blocks deliberately containing structural anomalies to compel rigorous documentation-led exploration.
  - Require specific logic gates rendering an intermediate artifact crucial. E.g., force a validation pause measuring a staging table before enabling downstream derivation to evaluate inter-step logic checks.
  - Ensure outputs demand rigorous trajectory narrations reflecting detailed discovery, monitoring state transitions, diagnostic queries, and the ultimate valid SQL outputs seamlessly.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
