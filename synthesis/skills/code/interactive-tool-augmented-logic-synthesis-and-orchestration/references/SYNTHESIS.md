# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Engineer 'Asymmetric Information Gaps' where the user prompt provides a qualitative goal (e.g., 'Find the outlier') but withholds the dataset values, forcing the agent to discover them. The environment should contain a large, cryptic array or object where the outlier is hidden at a non-obvious location (e.g., index 412 out of 500). Success is awarded only when the agent uses its 'Observe' and 'Scan' tools to locate the anomaly. For example, hide the fact that 'Price' in a financial task is stored as a string that needs parsing before comparison.
  - Implement 'Incremental Difficulty Augmentation' by scaling the parameter magnitudes of the baseline coding tasks beyond 'easy' reasoning levels. The synthesis loop should generate task configurations where array lengths are N=10,000 or numerical values are >10^12, ensuring the agent cannot simple 'simulate' the result in its head. The question should explicitly state: 'Perform this task using the tools provided to find the exact result for the large-scale input currently in the environment.' This forces the agent into a 'tool-augmented' mode of operation.
  - Design 'Multi-Step Logic Gated Pipelines' where a terminal answer can only be reached by calling tools in a specific dependency chain. For instance, ask to 'Calculate the weighted sum' where the weights are stored in one tool and the values in another. The agent must first query the weights, store them in its context, then query the values and perform the multiplication. This creates high-density training data for 'contextual state management' and helps the model learn to 'connecting the dots' between modular tools.
  - Incorporate 'Implicit Error Triggers' where the environment contains distractor data that causes a tool to crash if not handled correctly. The question might ask to 'Find the mean of the list', while the list contains a 'None' or an invalid string at a middle index. The agent must use its 'CheckValue' tool to identify the noise, filter it out, and then compute the answer. A successful synthesis results in a JSON showing the agent documenting the 'None' detection and adjusting its calculation logic proactively.
  - Require the final output JSON to include a 'Tool-to-Evidence Matrix' in the trajectory that explicitly records the information gain of each action. The synthesis instructions mandate that every thought block after a tool call must state: 'Observation X updated known variable Y'. This provides a high-density reasoning signal for training reward models to distinguish between 'lucky calls' and 'informed investigations'. A requirement is: 'Every numerical decision in your logic must be justified by identifying the responsible tool output in the trajectory.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
