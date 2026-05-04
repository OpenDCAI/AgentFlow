# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Incorporate 'Masked Span Prediction' tasks to target intrinsic hallucination thresholds. Generate questions that present a sentence from the document with a numerical value masked (e.g., 'Revenue increased by [MASK] in 2023') and require the agent to recover it from the tables. This forces the model to stay 'faithful' to the document context. A practical prompt is: 'Using the provided tables, fill in the masked blank in the Management Discussion section regarding operating expenses'.
  - Embed 'Latent Variable Obstacles' requiring multi-step financial logic. Design scenarios where the answer is NOT in a single cell but requires inferring a variable through other table entries (e.g., calculating equity by subtracting debt from purchase price). This tests the 'Multivariate Calculation' capability (Scenario D). An example prompt is: 'Based on the mortgage debt and ownership percentages in Table 4, calculate the total equity value associated with the Mohawk Commons acquisition'.
  - Use 'Scale-Error Traps' by varying the units used in text vs tables. Create a document where a table is in 'millions' but the question asks for the answer in 'units' (dollars) or 'billions'. This forces the agent to demonstrate 'Scale Audit' capabilities and prevents common magnitude hallucinations. A concrete synthesis prompt is: 'Report the total net income for FY2024 in billions of USD, even though the source table provides the data in thousands'.
  - Introduce 'Hint-Dependent Uniqueness' prompts for ambiguous metrics. Synthesize questions where a field like 'Revenue Growth' can be expressed as either a percentage or an absolute dollar amount, and provide a hint (e.g., 'Hint: The answer should be a percentage'). This tests the agent's ability to follow complex formatting instructions and ensures a unique correct answer. A success signal is a QA pair that resolves a potentially ambiguous cell match through a clear prompt constraint.
  - Design 'Temporal Alignment' challenges across multi-year reports. Formulate questions that require the agent to find 2024 data in one table and 2022 data in another to perform a three-year average calculation. This confirms the agent can navigate long-context (8k+ tokens) environments without mixing up different fiscal years. An edge case is asking for a 'Three-Year CAGR' (Compound Annual Growth Rate) which requires finding the start and end values across distant tables.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
