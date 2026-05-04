# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Engineer 'Implicit Logic Gaps' by providing a user prompt that specifies a data-quality goal (e.g., 'label all the transactions') but withholds the specific rule manual location. This forces the agent to use the 'Environment Exploration' phase to discover the manual and map its contents to the data. Success is awarded when the agent uncovers the hidden 'decision_tree.md' or 'business_rules.txt' autonomously. For instance, hide the threshold for 'suspicious activity' and see if the agent recovers it from a deep subdirectory.
  - Implement 'Dimensionality and Dependence Lures' where a dataset has multiple missing columns, but one is a direct function of the others. The prompt should require the agent to implement an imputation logic that respects this 'physics' (e.g., if A + B = C, and C is missing, the agent should calculate it rather than predicting it). This tests the agent's 'Relationship Sensing' over simple pattern matching. A successful synthesis results in a JSON showing the agent using a specific 'Check-and-Calculate' step before applying a model.
  - Incorporate 'Noise and Outlier Stressors' by provided data where naive imputation (like mean-filling) would significantly degrade the project's target accuracy. The question rewards the agent for identifying the 'skewed distribution' and choosing a more robust method like a KNN or Diffusion imputer. This ensures the synthetic data captures the 'high-precision engineering' identified in advanced ML benchmarks. The final answer must show that the agent confirmed the skew before choosing the algorithm.
  - Require the final output JSON to include an 'Imputation-to-Source Ledger' that explicitly records the statistical delta for every recovered variable. The synthesis instructions should mandate that the trajectory records the 'Standard Deviation Shift' observed after the imputation. This documentation makes the synthesized data valuable for training models to verify their own data-handling integrity. A requirement is: 'Every data change (e.g., a batch of 5000 labels) must be justified by an observed rule or model output in the trajectory.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
