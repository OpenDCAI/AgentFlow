# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Construct 'Cinematographic Shot-Scale Retrieval Queries' that force the model to classify segments based on body-part visibility. Use templates like: 'Identify the shot type used between T=5s and T=15s (e.g., Close-up, Medium Shot, Full Shot) and explain how the visible body parts define this classification.' This prevents generic guesses and forces the model to use the geometric visibility logic identified during exploration.
  - Generate 'Intent-Driven Structural Boundary Tasks' asking for the exact timestamp a shot changes and how it aligns with the speaker's emotional state. Formulate questions such as: 'Locate the precise second the camera cuts to a tight close-up; based on the speaker's vocal tone at that moment, why was this transition necessary?' This secures the link between multimodal audio intensity and structural temporal analysis.
  - Implement 'Multi-Shot Sequence Ordering Challenges' where the agent must order a list of shot transitions and their corresponding types across a complex montage. You must package a query like: 'In what chronological order did the following shot types occur: (a) Medium Full Shot, (b) Close-up, (c) Wide Shot, and locate the boundary frames for each.' This tests the integrity of the unified structural timeline.
  - Design 'Counterfactual Transition Predictions' questioning the impact of omitting a specific shot change recorded in the trajectory. You must formulate prompts like: 'If the camera had remained in the Full Shot at T=20s instead of cutting to the Close-up, what aspect of the speaker's facial gesticulation would have been lost?' This validates the agent's understanding of cinematographic purpose and structural necessity.
  - Apply 'Format-Strict Boundary Regression' for the final ground-truth answer, specifically utilizing the 'second{t}s - second{t}s' syntactic alignment for shot durations. You must ensure the response is concise and mathematically grounded: 'Shot 1 (MS): 0.5s - 12.3s; Shot 2 (CU): 12.3s - 20.0s.' This establishes a standardized metric for evaluating temporal localization accuracy.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
