# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Synthesize the story aggressively around one central, fresh narrative move or non-linear displacement rather than clustering many weak novelties.
  - Apply 'Concept-to-Consequence Synthesis' by placing every speculative concept into a causal chain (Concept -> Resulting Constraint -> Character Action) ensuring world-building is 'active' rather than 'decorative'.
  - Implement 'Perspective-Locked Phrasing' that limits the narrative voice to the specific 'Cognition Node' of the active character to constantly reinforce information asymmetry and suspense.
  - Execute 'Structural Weaving' mid-generation by surgically inserting 'Recall' (flashbacks) and 'Thread' (foreshadowing) markers directly into the dialogue or internal monologues to connect current prose to narrative history.
  - End the generation sequence strictly with a narrative payoff, avoiding the temptation to provide an immersion-breaking meta-explanation to the reader about the thematic meaning of the climax.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
