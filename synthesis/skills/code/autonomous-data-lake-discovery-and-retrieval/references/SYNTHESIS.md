# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Engineer Asymmetric Knowledge Gaps by providing a broad, business-oriented goal while withholding the specific file paths and schema details. The question should specify what information is needed (e.g., 'find the correlation between fires and humidity in 2024') but use an environment where the data is nested 3-4 levels deep in cryptic directories. Success is only awarded when the agent uses its reconnaissance tools to uncover the hidden data sources autonomously.
  - Incorporate Semantic Granularity Lures where the data lake contains multiple files with similar names but different levels of aggregation. For example, provide 'daily_stats.csv', 'monthly_stats.csv', and 'raw_sensor_logs.csv' simultaneously. The question should reward the agent for identifying through sampling which file provides the exact granularity (e.g., hourly) required by the user's analytical constraint.
  - Design Multi-Modality Format Stressors where the correct answer requires combining info from at least two different file formats (e.g., metadata from an XLSX and raw values from a CDF). The instruction should force the agent to orchestrate different library drivers in a single Python script. This creates high-density training data for 'tool-switching' and 'cross-format integration' capabilities relevant to professional data science.
  - Implement Implicit Terminology Traps by using underspecified or acronym-heavy requests that require a web search discovery turn. The prompt might mention 'Generally Unsafe Air Quality Days' without defining the AQI threshold, forcing the agent to find the EPA definition online before it can process the local sensor files. A successful synthesis results in a JSON showing the agent using external grounding to calibrate its local data processing logic.
  - Require the final output JSON to include a Discovery-to-Implementation Ledger that maps every data source used back to a specific tool observation. The synthesis instructions mandate that the reasoning records: 'Found cluster X -> sampled file Y -> matched column Z to user requirement'. This documentation makes the synthesized data valuable for training models to verify their own evidence-based retrieval trajectories.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
