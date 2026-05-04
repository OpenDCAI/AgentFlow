# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Engineer 'Multi-Table Alignment Tasks' where a single user instruction requires extracting information that must be distributed across at least two or three linked tables. For instance, ask to 'Add information for a new scientific discovery' where the agent must update a 'Discoveries' table, a 'Researchers' table, and an 'Institutions' table using foreign keys. This forces the agent to demonstrate stateful multi-file and multi-table reasoning. Success is awarded when the agent maintains referential integrity throughout the extraction loop.
  - Implement 'Semantic Granularity Lures' where the text describes an attribute at a different level of detail than the database expects. The prompt might provide a news report referencing 'northern France' while the database consistently uses 'City, Regional Dept, France'. The question rewards the agent for identifying this mismatch through DB analysis and choosing a normalization strategy (e.g., searching for the city name in the text or using a placeholder). This tests the 'Critical Data Sensing' capability of the agent.
  - Incorporate 'Implicit Format Requirements' by provided a database where the data format is defined only by examples in existing rows, not by explicit documentation. For example, all dates in the table are 'DD-MM-YYYY' and all prices are floats. The agent must use the 'Observer' phase to identify these patterns and apply the same normalization to its new extractions. This forces the agent to use 'environmental cues' rather than relying on standard libraries.
  - Design 'Asymmetric Task Scaffolding' by providing a broad natural language goal (e.g., 'Enrich our database with recent events') but withholding the specific documents until the agent identifies which entities are already present. This forces a multi-turn 'Discovery-then-Extraction' workflow where the agent first audits the DB to see what is missing and then requests or navigates the provided text set to find those specific values. A successful synthesis will result in a JSON showing how the agent 'connecting the dots' between existing gaps and new evidence.
  - Require the final output JSON to include an 'Integration Mapping Ledger' that maps every value in the updated database back to a specific sentence index in the source text. For example, 'Column: Budget Value: 170000000 Source: "The film grossed $714 million worldwide based on the budget of 170 million..."'. This documentation makes the synthesized data valuable for training models to verify their own extractions. A requirement is: 'Every numerical transformation (e.g., scaling or reformatting) must be explicitly recorded in the reasoning trajectory.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
