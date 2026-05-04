# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Incorporate 'Ontology Disambiguation Challenges' by providing documents that contain terms with multiple meanings across domains. Specifically, ask the agent to extract these terms into a schema that requires a 'Canonical ID' (e.g., UBERON or MeSH). This tests the agent's ability to use context to resolve polysemy. A practical prompt is: 'Extract all mentions of brain structures and link them to their UBERON IDs, ensuring you distinguish between anatomical regions and general clinical symptoms.'
  - Design 'Hierarchical Meta-Extraction' tasks for scientific instruments. Generate prompts that require converting a complex, multi-page PDF questionnaire into a nested JSON structure (e.g., ReproSchema). The schema must include parent-level info (title, author) and child-level info (item prompts, response triggers). This tests 'Multi-level Reasoning' over document structures. An example is: 'Convert this MFQ-LV assessment into a machine-readable schema, making sure to capture the branch logic for question 4.'
  - Embed 'Noise-Robust Spatial Extraction' scenarios using degraded or layout-heavy forms (e.g., scanned registration forms). The question should target specific fields that are spatially distant from their headers or are partially obscured by OCR noise. This forces the agent to use its 'Spatial-to-Logical Anchoring' capability. A synthesis rule is: 'Require the agent to pull the "Signer Name" and "File Date" from this scanned Amendment document, ensuring the date is normalized to YYYY-MM-DD.'
  - Task the agent with 'Relational Edge Discovery' across clinical trial abstracts. Formulate questions that require the agent to produce a 'Relational Graph' JSON output, including the Subject, Object, Direction, and 'Novelty' of the finding. This tests the agent's ability to map grammatical cues to a rigid relational schema. For instance: 'Identify all drug-to-effect relationships in this report and classify each as either a "Background Fact" or a "Novel Finding" based on the section header.'
  - Enforce 'Regex and Format-Clean' constraints in the synthesis prompt. Require the agent to provide the output strictly within a JSON wrapper, where specific fields (like IDs, dates, or currency) must follow a rigid string pattern. This creates high-pressure conditions for checking 'Output Refinement' and 'Data Normalization'. A strong prompt is: 'Extract the Line Items from this invoice into a JSON array, but ensure all prices are formatted as a float without currency symbols and all dates use ISO 8601.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
