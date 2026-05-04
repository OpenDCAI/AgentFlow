# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate user requests using 'Cumulative Goal Hooks' combined with 'Conflict-Inducing Nudges.' Start the script with a set of 3 distinct, measurable rules (e.g., 'use B1 English', 'must use [tag]', 'limit to 50 words'). In Turn 3, have the user ask for extreme detail. The synthesized response must prioritize the initial structural constraints while handling the new detail elegantly.
  - Incorporate 'Explicit Goal-State Checkpoints' where the user acts as an evaluator mid-dialogue. Turn 5 of the script should have the user asking: 'Are you still following the tone and length rules we set at the start?' The synthesized response must demonstrate an 'Internal Audit' step: 'Checking rules... Rule 1: Met. Rule 2: Met... Response: Yes, I am adhering to...', creating a supervised checkpoint signal.
  - Construct 'Anaphoric Reversion Commands' where the user asks the agent to 'apply the formatting from our very first message to the latest draft.' This tests deep context traversal (15-20 turns) to retrieve and rigidly apply an ancestral instruction set that has been heavily buried by intermediate conversational noise. The output must perfectly resurrect Turn 1 logic.
  - Design 'Drift-Prone Personas' for the user simulator. Have the simulator change its mind entirely or add high-entropy 'side-goals' that compete for the agent's limited context attention. Every turn, the synthesized agent must output an internal 'State Ledger' JSON field: {'Original_Goal_Adherence': 0.95, 'Drift_Detected': False}. This explicitly defines exactly how instruction-tracking prevents goal erosion.
  - Integrate 'Syntactic-Leveling Triggers' requiring the use of complex multi-part grammar constraints. Engineer a prompt mandating 'Only use Superlative degrees' in subsequent conversational comparisons. If the user asks a tricky query about movie quality, the synthesized agent's response must smoothly embed 'It was the best movie I have ever seen' rather than violating the superlative requirement.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
