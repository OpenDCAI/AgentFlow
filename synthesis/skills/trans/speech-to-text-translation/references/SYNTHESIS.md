# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Embed Multi-Level Acoustic Stressors by combining 'Babble' and 'Disfluencies' in a single source. Synthesize prompts that force the agent to perform 'Signal Separation' while simultaneously resolving 'Stuttering' patterns. Example: 'Translate this audio where a man is stuttering in a busy restaurant into formal German.'
  - Command Register-Prosody Mismatches to test Affective Awareness. Formulate tasks where the lexical content is polite (e.g., 'Everything is fine') but the instruction specifies provide a translation that matches the 'sarcastic tone' of the audio. This forces the agent to demonstrate it can prioritize paralinguistic cues over literal text-dictionary definitions.
  - Construct 'Insertion-Trap' Prompts using low-resource acoustic segments. Design questions featuring audio with heavy background wind or machinery static that mimics the 'Phonetic Footprint' of valid words. The instructions should demand a 'clean and accurate translation,' requiring the model to utilize semantic context to filter out the false acoustic triggers.
  - Implement 'Spontaneous Real-World' dialogue scenarios. Create questions utilizing audio clips of natural, non-scripted communication—including 'umms', 'ahrs', and self-corrections (e.g., 'I want the blue, no, the red one'). The synthesized gold answer must reflect the 'final corrected intent' (the red one) rather than the discarded error.
  - Strictly mandate Tri-Stage Trajectory Documentation in the JSON output. The synthesis rule ensures the agent logs: 1) Identification of the Noise/Disfluency profile, 2) The strategy for Filtering/Resolution, and 3) The target-language Mapping. This provides a clear audit trail proving robustness against the acoustic phenomena highlighted in contemporary ST benchmarks.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
