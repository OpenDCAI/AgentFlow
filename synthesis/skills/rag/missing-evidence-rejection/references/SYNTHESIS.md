# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Synthesize 'Uncertain Specificity' questions by asking for hyponyms or specific attributes absent from the evidence. If the article mentions 'a major donor', the question should ask for the 'donor's middle name' or 'the exact USD amount up to two decimal places'. This forces the agent to realize that while the 'Donor' entity exists, the requested granularity does not. A robust synthesis rule involves taking a noun from the text and asking for a more specific sub-type (e.g., 'poodle' when 'dog' is used).
  - Formulate 'False Premise' queries by injecting a contradictory property into the question. Identify a fact, such as 'The center opened in July', and phrase the query as 'Why did the center open in December?'. This forces the agent into a conflict-resolution mode where it must prioritize the retrieved evidence over the question's stated premise. Forcing the answer to 'Unanswerable' creates a high-precision evaluation signal for evidence faithfulness.
  - Design 'Bridge-Entity Omission' multi-hop samples for diagnostic testing. Create a question that requires two hops (A -> B, B -> C) and provide news articles for (A -> B) and (C), but omit the document for (B -> C). Ask about the relationship between A and C to see if the agent correctly flags the gap. This directly helps identify and mitigate 'shortcut reasoning' where agents guess connections based on co-occurrence in a long-context window.
  - Implement 'Multi-Choice Deflection' answer templates with scorable justifications. Every synthetic QA pair must include an 'Unanswerable' option along with 5 plausible distractors derived from other facts in the fictional timeline. This ensures that the agent's task is not just to refuse, but to choose the *correct* refusal among competing facts. The ground truth answer should be paired with a 'Logical Trace' explaining why the other options were bypassed.
  - Construct 'Assumption-Leakage' guardrails in time-span questions. When generating questions about durations (e.g., 'How many days passed between event X and Y?'), ensure the question does not restate the dates or spans found in the evidence. If the question says 'Given event X happened on Monday...', it leaks evidence. The synthesis must remove these assumptions to force the agent into a two-pass chronometric extraction before calculating the span or rejecting it.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
