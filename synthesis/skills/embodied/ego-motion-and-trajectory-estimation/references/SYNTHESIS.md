# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  * **Choose one dominant dynamic target.** Each synthesized question should focus on one dominant dynamic variable such as rotation angle, path length, final pose, or natural-language trajectory summary. This makes the supervision sharp and lets the accepted trajectory map cleanly to one capability. For example, use a left-turn hallway clip to ask about yaw shift rather than mixing in unrelated speed estimation.
  * **Ground motion language in the scene.** Trajectory questions should mention scene anchors or task-relevant destinations when that improves clarity. The agent should describe motion in embodied terms such as 'into the room' or 'stopped in front of the cabinet' while preserving quantitative content when needed. This produces data that can later generalize into actual navigation or manipulation settings.
  * **Use realistic distractor answers.** For multiple-choice dynamic questions, generate negatives that correspond to common embodied errors such as underestimating turns or confusing rotation with translation. Distractors should be close enough to require reasoning but separated enough to preserve a unique answer. A 47-degree rotation question might use 19, 33, 47, and 82 degrees rather than absurdly unrelated values.
  * **Preserve temporal ordering explicitly.** When a question depends on multiple events, phrase it so that the order of motion matters. The agent should include wording like 'from 1s to 18s' or 'after turning left into the room' to prevent static-scene guessing. This is especially important for path-length and trajectory-description tasks.
  * **Keep the answer format compact and operational.** Final answers should be short descriptions, vectors, angles, poses, or scalar distances that can be checked automatically. Avoid free-form long essays unless the task is explicitly trajectory description, in which case the expected answer should still mention ordered motion segments. This keeps the dataset faithful to embodied control and evaluation needs.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
