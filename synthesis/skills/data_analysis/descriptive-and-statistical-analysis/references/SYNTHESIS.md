# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Design prompts that ask for the interpretation of latent structures or PCA axes rather than simple column lookups. For example, instead of 'find the mean', ask 'Which distinct sub-populations are separated by the coordinates in the first two principal components?'. This forces the agent to execute a dimensionality reduction pipeline and ground the abstract math in the dataset. An edge case is asking for the 'drivers' of a cluster, requiring the agent to perform both grouping and differential calculation.
  - Create synthetic environments where the 'Domain Calibration' of thresholds is the decisive factor for the final count. Produce a dataset with low-magnitude signals (like imaging-based counts) and a distractor column with high-magnitude noise. The prompt should ask for a summary statistic that will be wildly incorrect if the agent uses a standard 'sequencing-style' filter instead of a calibrated 'imaging-style' filter. This teaches the agent that data modality dictates the cleaning and statistical parameters.
  - Mandate a 'Distributional Comparison' output which includes both a numerical similarity metric and a qualitative mapping. The prompt should require an answer in the format: 'The Cosine similarity is 0.92, indicating a near-identical distribution between the two cohorts.' This ensures the synthesis reinforces the 'Step-by-Step Reporting' of evidence. An edge case is providing two groups that look similar but have a statistically significant p-value due to high sample size, testing the agent's nuance.
  - Include 'Topology-Aware' requests where the answer depends on interaction between related observations in a coordinate space. Use prompts like 'What is the most common neighbor cell-type for Category X?' or 'how does local density relate to the target variable?'. This forces the agent to build an adjacency graph or distance matrix, moving beyond row-independent analysis. A concrete example is a question about 'niche identity' where the agent must pool data from nearby x,y points.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
