# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Construct 'Ambiguous Seed Challenges' by providing the LLM with three diverse personas (A, B, C) and requiring it to write a single-sentence starting message that fits A and B but excludes C. This forces the synthesizing agent to handle the 'Initial Indeterminacy' identified in InfoQuest. The question should be naturally worded like 'I need help navigating this tricky situation' to maximize the need for follow-up questions.
  - Embed 'Constraint Drip-Feed Triggers' in the multi-turn script. Design the user simulator to reveal only one of the 5 hidden constraints (e.g., 'Budget,' 'Time,' 'Distance,' 'Experience Level,' 'Equipment') per turn, and only IF the assistant specifically asks about it. The synthesized assistant turn must always perform a 'Pre-Act Thought' identifying which unknown constraint it is hunting for in the upcoming question.
  - Design 'Naive-Agent Mitigation Traps' where the user prompt explicitly asks for 'some suggestions' or 'pointers' early on. The synthesized gold behavior must show the assistant *resisting* the urge to provide a list, instead replying: 'I'd love to give you some pointers, but to make sure they're actually relevant to you, could I first ask...?' This provides the critical 'Instruction-Tuning' signal for information-seeking over generic verbosity.
  - Incorporate 'Success Checklist Metadata' in the JSON field: `{'hidden_constraints': ['C1: Budget', 'C2: Location'], 'resolved_in_turn': [1, 3]}`. This metadata allows secondary models to learn the 'Resolution Density' of a conversation. The synthesis must culminate in a 'Post-Hoc Solution' summary that explicitly shows how every discovered constraint from the checklist was incorporated into the final advice.
  - Implement 'Inquiry Funnel Pacing' where the assistant's questions move from 'High-Level Scoping' (e.g., 'What kind of connection?') to 'Granular Constraint' (e.g., 'What is your specific budget for this?'). This ensures the synthesized data supports a logical, human-like progression that reduces user frustration by establishing the 'Big Picture' before diving into the 'Details'.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
