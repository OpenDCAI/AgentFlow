# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  * **Force object-plus-anchor wording.** Questions should refer to the target through both object identity and anchored context, so the agent must ground rather than guess. Compose prompts such as 'the red suitcase near the bed' or 'the marked corner on the blue box beside the mug,' and avoid naked category references. An edge case is a scene with only one suitcase; in that case add a relation or part description so the second view remains necessary.
  * **Prefer transferable local references.** Question wording should name transferable local structure such as corner, handle, edge, rim, or marked point when possible. When generating data, describe the exact local site in view one and require the agent to resolve it in view two or in 3D space. For example, 'Which point in Image-2 matches the front-left corner of the box in Image-1?' is stronger than 'Which object is this?'
  * **Build distractors from plausible confusions.** Wrong options should come from same-category instances, nearby regions, or symmetric parts that are genuinely confusable under viewpoint change. Construct distractors only after the correct chain is known, so that every negative option reflects a realistic failure mode. A good negative is the rear-left corner of the same box; a poor negative is a random point in the sky.
  * **Require cross-view reasoning explicitly.** The final question should be impossible or highly unreliable to answer from a single frame alone. Check this by mentally hiding one view; if the answer remains obvious, rewrite the prompt to incorporate the second observation or 3D relation. A concrete edge case is when the target is centered and isolated in both images; add a point-transfer or anchored disambiguation requirement.
  * **Keep answers atomic and verifiable.** The answer should resolve to a unique label, coordinate, region description, or grounded object phrase that can be checked unambiguously. During generation, avoid open-ended prose when a discrete grounded output is available, because diffuse wording weakens evaluation quality. For example, 'Point A' or 'the suitcase beside the bed' is preferable to a long narrative that mixes extra details with the answer.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
