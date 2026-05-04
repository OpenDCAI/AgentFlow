# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  * **Explicit physical quantity phrasing.** Formulate questions with a precise geometric target such as depth, height, width, length, or nearer/farther relation. Use wording that forces a measurement interpretation, not a semantic size judgment, and include the marked point or object identifier explicitly. For example, ask 'What is the height of the desk?' rather than 'Is the desk tall?'
  * **Anchor each target unambiguously.** Questions should name the exact object or point using visible context, labels, or marked coordinates. During synthesis, attach the measurement target to a localizing phrase such as 'the desk commonly visible in these images' or 'the point marked on the front edge of the bed frame.' If multiple desks appear, add a relation like 'the desk beside the monitor wall' so the answer remains unique.
  * **Use realistic error bands for distractors.** Multiple-choice options should reflect common embodied estimation errors such as underestimation under foreshortening or confusion between nearby depth planes. Generate distractors around the true value with scene-appropriate spacing instead of absurd random numbers. A good desk-height question might use 820, 950, 1080, and 1320 mm rather than 95, 950, 9500, and 95000 mm.
  * **Couple numeric demand to evidence strength.** The answer format and tolerance should reflect how much evidence the trajectory actually provides. If the observation supports only ordinal comparison, synthesize a nearer/farther question; if it supports quantitative geometry, synthesize a numeric question. Do not force a millimeter answer when the views only support reliable ranking.
  * **Keep answers checkable and compact.** The final answer should be a single number with unit, a discrete option, or a brief relative-depth statement. During generation, avoid long explanations inside the answer field so the resulting supervision remains easy to evaluate automatically. An answer like 'approximately 950 millimeters' is preferable to a paragraph explaining why desks are usually that height.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
