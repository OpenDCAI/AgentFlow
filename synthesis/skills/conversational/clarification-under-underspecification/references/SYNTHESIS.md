# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - **Write the final question in ordinary user language.** The generated question should evoke clarification under underspecification without naming the capability explicitly. Use everyday wording that a developer or end user could realistically type into a chat interface. For example, prefer a practical follow-up or reminder request over academic wording about memory, theory of mind, or policy adherence.
  - **Make the trajectory-dependent evidence do real work.** The final question should be impossible to answer well unless the model uses the earlier trajectory built around natural fragmented user requests where one or two clarifications are necessary before a correct final answer exists. This ensures the item teaches the right conversational behavior rather than generic response polish. If the gold answer could be guessed plausibly without consulting the trajectory, revise the question.
  - **Embed one explicit evaluation hook.** Include at least one feature that makes success or failure easy to inspect, such as a count, a named entity, a yes-no boundary, a required alternative, or a stable perspective target. This hook should remain natural to the dialogue and should not turn the question into a mechanical template. A good edge case is a referential phrase like 'the second example' or 'the most recent trip' because it exposes a concrete failure mode.
  - **Keep the synthetic item compact but not trivial.** The final question should be short enough that the difficulty comes from reasoning over the trajectory, not from reading an overengineered prompt. At the same time, avoid stripping away the detail that creates the capability signal. The design target is a natural user utterance backed by a rich trajectory rather than a long benchmark-style instruction block.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
