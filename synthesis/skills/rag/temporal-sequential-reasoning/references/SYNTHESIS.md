# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Phrase queries around 'Constraint-Duration Entanglement' to force window search. Ask for the result of finding a specific condition ('volume < 500') that must persist for a defined duration ('1 hour') within a certain horizon ('before 09:00'). Using phrases like 'Find the earliest gap' or 'Is there any time I can avoid...' naturally triggers iterative temporal reasoning. For example, 'Can I find a 2-hour window where the temperature is below 25 degrees?' forces a scan of multiple points.
  - Synthesize 'Chronological Shift Inquiries' targeting postponement and pre-emption. Formulate questions that request the 'earliest postpone' or 'latest leave early' time based on a failure in the initial plan. This forces the agent to identify a violation first, then seek its negative (the resolution) forward or backward in the timeline. A classic prompt is: 'If I can't avoid the rain at 13:00, when is the first time I can leave late until there is no rain?'
  - Embed 'Misleading Recency Traps' to stress-test version and update handling. Actively saturate testing scenarios with reverse-ordered narratives or 'recent' publication dates attached to obsolete factual schemas. Forcing the model to discriminate between 'the most recent document' and 'the document covering the most recent event' significantly heightens the diagnostic value. A strong case involves a 2024 report discussing 2022 stats, while a 2023 report discusses 2023 stats; the agent must pick the latter for 'latest data'.
  - Construct 'Multi-Leg Comparative Timelines' across disparate documents. Design questions that require extracting events from File A and File B to determine which happened first, or if they overlapped. This forces the agent to normalize two independent temporal strings onto a single shared axis before calculating the delta. For example, 'Did the software patch in Document A go live before or after the server crash described in Document B?' ensures the agent doesn't just look at one file.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
