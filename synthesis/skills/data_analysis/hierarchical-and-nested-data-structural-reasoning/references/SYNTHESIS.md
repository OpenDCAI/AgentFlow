# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Design synthesis prompts that use casual, layman language to describe technically nested targets. The user might say 'Get the scanner results' while the file contains a long path like '/projects/mri/raw_data/scans/pixel_matrix'. This forces the agent to use its disambiguation logic to bridge the gap between user intent and technical nesting.
  - Create synthetic environments with 'Structural Near-Misses' where similar data exists in different versions or groups. For instance, include a 'raw_counts' and a 'normalized_counts' attribute within the same object and write a prompt that specifies the 'preprocessed' version. This ensures the agent is forced to use its hierarchical navigation logic to select the correct candidate.
  - Incorporate 'Attribute-Dependent Traps' where the final answer is mathematically incorrect unless a specific nested metadata field is utilized. For example, provide a dataset where the values are integers but a hidden attribute 'units_multiplier' is set to 0.001. This tests whether the agent integrates the nested metadata instructions into the final mathematical outcome.
  - Mandate a 'Scan -> Plan -> Execute' trajectory format in the synthesized JSON output for these tasks. The agent should first call a tool to see the hierarchy, then think about which path or linked component matches the user's intent, and finally write the code. This logical loop reflects the 'structure-aware' strategy required for complex scientific data formats.
  - Include 'Relational Linking' requirements where a filter from one part of the hierarchy must be applied to a matrix in another part. For example, ask for the 'average measurement for Group A' where 'Group' is an attribute in the row-metadata folder and the measurements are in a separate dense array. This mandates multi-point navigation and ensures the agent can maintain context across different branches of the data tree.
  - Design 'MissionBio/ParseBio Platform-Style' traps where the data modality (e.g., RNA vs Protein) is hidden in a non-obvious metadata column. The prompt should ask for a generic 'expression' value, forcing the agent to check the metadata to see which layer or column actually contains the requested modality. This mimics real-world single-cell analysis footguns where agents often confuse different feature types stored in the same file.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
