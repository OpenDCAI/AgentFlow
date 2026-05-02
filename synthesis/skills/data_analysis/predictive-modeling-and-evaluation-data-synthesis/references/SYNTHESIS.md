# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write prompts that make the predictive target and required artifact explicit. The user should ask for a forecast, prediction file, or modeled output in ordinary language, while the environment provides the necessary schema and evaluation format. This yields realistic but controllable modeling tasks.
  - Ensure the modeling step is necessary but not bloated. The question should not be solvable by a direct table lookup, yet it should also avoid excessive hyperparameter search that turns the task into pure optimization. A simple, defensible modeling path is ideal for data synthesis.
  - Bind evaluation tightly to the generated output. Good prompts mention the file to save, the metric to optimize, or the result format to produce. This teaches agents that successful modeling in analysis environments includes delivery, not just latent estimation.
  - Show the trajectory as read-build-predict-save-check. The JSON should make clear how the agent read the data, constructed or applied the model, generated predictions, wrote the output artifact, and performed a final sanity check. That ordered pattern is highly reusable for predictive tasks.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
