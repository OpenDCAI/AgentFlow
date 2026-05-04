# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Construct 'Ablation-Guided Anomaly Description Prompts' that ask for a detailed event breakdown with and without knowing the anomaly category. First, use an 'Unconditioned' template: 'Is there anything abnormal in this video? Describe the events in detail'. Then, use a 'Conditioned' template: 'We believe a [Crime Type] occurs; please describe the specific evidence and humans involved'. This forces the agent to demonstrate both detection ability and high-fidelity descriptive auditing.
  - Generate 'Investigation-Centric Multiple-Choice Questions' focusing on causal roles, object details, and outcome recognition. First, author questions such as: 'Who was the main perpetrator, and what action did the police officer take towards them?'. Distractors should be 'Plausible Normative Behaviors' (e.g., 'they were just talking', 'the officer walked away') to test if the agent can resist biased 'Safe-Environment' priors.
  - Implement 'Temporal Grounding Localization Tasks' that require the model to output start/end times in a strict JSON format for an identified anomaly. First, anchor the question: 'Locate the start and end time of the [Crime Name] event in this video.' The ground truth must be derived from the exact frame where the illegal/dangerous act initiates and the frame where the scene resolves or cuts.
  - Apply 'Causal-Role Identification Prompts' that force the model to distinguish between perpetrators and victims based on the initial interaction. First, identify a 'Conflict Zone' and ask: 'Identify the person in white; are they the aggressor or the bystander, and what kinetic evidence supports your choice?'. This cements the link between geometric pixels (the person) and abstract social categories (the perpetrator).
  - Design 'Anomaly Classification Challenges' using a top-N accuracy format where the model must choose the correct crime category from a provided inventory. First, provide a list of categories like [Abuse, Arrest, Arson, Assault, Burglary...]. Then, ask the agent to select the one that fits the causal evidence, ensuring the logic is tied to the 'Key Evidence' (e.g., 'Assault' because of the hitting action).
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
