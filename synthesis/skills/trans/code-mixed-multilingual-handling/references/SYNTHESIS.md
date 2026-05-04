# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate 'Discourse-CS' translation requests using multi-speaker chat transcripts. Synthesize prompts that feature 2-3 speakers alternating between English and a target Guest language (EN-ZH, EN-TA, EN-MS) at different granularities. The gold answer must be a pure-language translation that preserves all speaker roles and facts. For example: 'Translate this English-Malay WhatsApp chat into pure English and don't miss the details about the meeting location.'
  - Embed 'Minority-Span' traps where the key factual information is only in the non-English segment. Design synthetic dialogues where the English words are small-talk (e.g., 'hello', 'good') but the actual logic (e.g., 'the price is 50 dollars') is in the guest language. This evaluates if the agent can resist Code-Switching Loss (CSL). A target-aligned answer must show that the agent did not just copy the 'hello' but recovered the price.
  - Implement 'Speaker-Role' stressors involving contested actions. Create a dialogue where Speaker A suggests a plan in English, Speaker B disagrees in the guest language, and Speaker C proposes a compromise. The question should demand a'source-aligned result'. The gold answer must reflect the correct final agreement, proving the agent followed the logical shifts through the language changes.
  - Use 'Romanized/Phonetic' guest-language strings to test orthographic robustness. Synthesize questions where a language like Tamil or Malay is written entirely in Latin characters (Romanized) without standardized spelling. This forces the agent to demonstrate it can decode phonetic intents. A high-quality synthesis item would be: 'Translate this Romanized Tamil conversation into English; ensure you capture the local idiomatic phrasing.'
  - Require Serialized CS-Comprehension steps in the JSON trajectory. The synthesis rule mandates that every sample logs: 1) Identification of the Matrix Language, 2) Detection of all CS spans, 3) Speaker-Fact Correlation, and 4) Monolingual Synthesis. This provides a clear audit trail proving robustness against CSL and SMA errors. Step 1: 'Identified English-Mandarin mix'; Step 2: 'Detected Mandarin span regarding baggage'; Step 3: 'Attributed baggage details to Speaker 2'.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
