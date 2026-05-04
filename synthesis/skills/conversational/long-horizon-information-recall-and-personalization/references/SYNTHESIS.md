# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate user questions employing 'Implicit Contextual Hooks' that refer to a broad category (like 'weekend plans') without mentioning the precise historical preference. Use prompts such as 'I have some free time this summer and want to do something that aligns with my professional goals—got any ideas?' to necessitate deep contextual searching. This guarantees the synthesized agent actively queries its metadata databanks to inform an otherwise unanswerable query.
  - Incorporate 'Voice-Bait or Identity-Bait' by seeding the structured prompt with two or more participants displaying similar demographic markers but harboring distinctly separate fact-checkable interests. Engineer scripts where User A and User B discuss overlapping general subjects but register contradictory preferences to test stringent attribute mapping. The resultant generated answer must utilize the correct identifying tokens to parse individual intent continuously throughout the dialogue format.
  - Construct 'Schedule Conflict Traps' by creating a conversational turn where the user explicitly requests an activity overlapping with a previously confirmed historical timeslot. The synthesized gold response must aggressively prioritize a 'Proactive Warning' directly challenging the temporal collision instead of yielding to a literal confirmation action. This firmly establishes a supervised learning instruction teaching intelligent models to respect historically anchored timeline objects perpetually.
  - Include 'Topic-Context Relevance Bridges' simulating a natural multi-turn evolution where the user provides an unstructured organic thought referencing an earlier session's core theme. The synthesis must forcibly output an internal 'Thoughts' JSON reasoning field documenting the precise logical connection derived between the immediate turn and the historical database. This constructs explicit reasoning logic teaching smaller models exactly how to pivot socially utilizing parsed memory traces.
  - Embed 'Fragmented Intent' sequences where the simulated user incrementally updates their detailed profile across strictly non-adjacent conversational rounds (Turn 1: Job, Turn 5: Goal, Turn 9: Hobby). Output generation must culminate in a final intricate question demanding the simultaneous coordination of all three dispersed elements. This methodology enforces 'Sequential Accumulation' behaviors, entirely preventing the model from learning to index solely the most recency-biased character introductions available.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
