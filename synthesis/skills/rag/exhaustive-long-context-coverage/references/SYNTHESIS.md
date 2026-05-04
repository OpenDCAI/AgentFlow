# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write questions aggressively penalizing partial skipping behaviors. Synthesize queries involving complex grouping, exact statistical occurrence counting, or global maximum/minimum identification to strictly enforce full context traversal. Using these mathematical operations absolutely ensures that failing to read the last 10% of the prompt yields a visibly incorrect response. Examples include asking 'What is the absolute highest recorded velocity among all tracked aerospace launches detailed in the complete archive?'
  - Construct long bundles using highly cohesive, same-domain templates. Assemble expansive payloads by binding dozens of highly repetitive templates, such as serialized financial reports or chronological clinical summaries, to prevent naive topic shifting navigation shortcuts. Uniformity across the distractors forces the model to actually read variable values rather than merely relying on shifting topic embeddings. An excellent synthesis targets 50 functionally identical SEC filings differentiated only by the raw fiscal numbers hidden inside item 6.
  - Mix extremity, broad counting, and hierarchical categorizing queries deliberately. Elicit varied statistical aggregation capabilities to test the limits of long-context comprehension, preventing the model from overfitting to simple 'find the maximum' tasks. Diverse synthesis ensures the prompt logic tests counting frequencies as effectively as sorting elements into rigid qualitative buckets. A strong mixed query might ask, 'Categorize the 50 personnel files into three performance tiers, then state which tier contains the highest density of software engineers.'
  - Enforce strict provenance chains tying aggregated summaries to source files. When logging the final synthetic JSON, forcefully trace the generated aggregated entities back to their parent files or specific hierarchical branch paths inside the trajectory generation logic. This enables rigorous human supervision and automated pipeline scoring for model faithfulness. The final data output must resemble: 'Entity A (found in Doc 3), Entity B (found in Doc 12), achieving a combined total of 400.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
