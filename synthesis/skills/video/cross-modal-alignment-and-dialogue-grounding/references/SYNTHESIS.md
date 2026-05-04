# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Construct 'Implicit Modality-to-Modality Queries' that use the description of one stream as the search key for the other. You must utilize templates like: 'Can you describe the visual information corresponding to this audio information: <Audio Segment Caption>?'. This forces the model to perform audio retrieval, temporal localization, and visual decoding.
  - Construct 'Disambiguation-Driven Retrieval Queries' that force the model to solve a problem answerable only by combining a corrected audio cue with a visual detail. For example: 'Based on the speaker's discussion of the software (which was misidentified in the initial transcript), what specific spelling is written on the screen?'.
  - Generate 'Explicit Bi-Directional Grounding Tasks' that require outputting start/end times in the 'second{t}' format. You should alternate between 'V2T' (Video-to-Time for UI interactions with sound) and 'A2T' (Audio-to-Time for sound effects). For example: 'What are the start and end time of the video segment corresponding to this audio: <Audio Caption>?'.
  - Design 'Ambiguity Resolution Distractors' for multiple-choice formats offering plausible descriptions from the wrong temporal segments. Create incorrect options that describe the visuals from Segment 1 but pair them with the audio context from Segment 2. This mandates following the strict temporal bridge identified.
  - Apply 'Step-by-Step Multimodal Chain-of-Thought' in the final answer to document the grounding logic. Structure the response as: 'Step 1: Identified the target audio at [T1-T2] correcting spelling to [X]. Step 2: Synced with visual frames at [T1-T2]. Step 3: Observed visual attribute [Y].'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
