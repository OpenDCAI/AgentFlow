# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate Fact-Dense, Colloquial Hypotheticals to force intentional discovery reasoning. Construct queries using the language a non-expert or frustrated user would use, such as 'Why did our monitoring station fail in the flood?' or 'Where did the money for the new radars go?'. Avoid using the expert terms found in the target RFC, Pilllar, or manual to force the agent into performing its semantic mapping capability. The more 'noisy' and descriptive the prompt is about the symptoms, the better it tests the mapping logic.
  - Embed Evidence-to-Pillar Mapping arrays in the final ground-truth format. The synthesized JSON ground truth must explicitly link each identified classification (e.g., Pillar 2) to its precise numerical amount and the specific grounded evidence spans from the PDF. Instead of just stating the category, it should follow a pattern of 'Category: X; Evidence Span: Y; Amount: Z'. This provides a granular supervisory signal for training the agent’s traceability and explainability during financial or legal auditing.
  - Synthesize Intent-Mapping Traps via Lexical Decoys to test discriminative precision. Infiltrate the knowledge bundle with 'topical distractors' that share keywords with the query but represent different expert domains. For example, if the query mentions 'protecting the coastline', include a document about 'Sea Walls' (Pillar 4 - Structural) and another about 'Coastal Risk Mapping' (Pillar 1 - Knowledge). A successful agent will use the context of 'planning' versus 'construction' to correctly discover the required blueprint category.
  - Incorporate Specific Source Attribution and Section-Level Headings as mandatory outputs. The generated answer must explicitly name the document ID and the specific section header it 'discovered' the classification in (e.g., 'According to the 'Component 2' section in the CREWS Project Document...'). This enforces strict groundedness and allows the auditor to verify the 'expert rule' against the original source text. It prevents the model from relying on hallucinated or generic principles by making citation an integral part of the response schema.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
