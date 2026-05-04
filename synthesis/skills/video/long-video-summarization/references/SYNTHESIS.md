# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Construct Comparative Longitudinal Queries that specifically ask about the delta between a character's state or the video's plot across massive temporal gaps. First, anchor the question at two specific timestamps: 'Comparing the situation at T1 with the final state at T2, what developments occurred?' to force long-horizon integration.
  - Build strong but fair distractors around overly generic summaries that mention the topic but omit the decisive turning points, or provide plot-logic distractors that follow standard tropes instead of the video's true outcome. First, make wrong options compatible with the start state, but logically incorrect based on the unique middle events. For example, a plausible distractor implies the mission failed naturally, while the true video proved a specific twist saved it.
  - Preserve answer faithfulness to the trajectory by calibrating a Step-by-Step Plot Justification. First, require the response to cite at least three specific progression points. For example, require the answer to say: 'The situation evolved because [Event 1], which was resolved by [Event 2], resulting in [Final State]', ensuring adherence to the verified path.
  - Calibrate linguistic difficulty without destroying verifiability by implementing Causal Block Reasoning Prompts. First, ask the agent to explain a mid-video event by referencing a Hidden Rule or Anchor Fact from the start. For example, phrase it as 'Based on the briefing at 5 mins, why is the action at 45 mins necessary?', locking the summary directly to the dependencies.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
