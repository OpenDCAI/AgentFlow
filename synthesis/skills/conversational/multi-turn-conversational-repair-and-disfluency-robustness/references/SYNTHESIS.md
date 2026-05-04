# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate initial user prompts using 'Drip-Fed Constraints' combined with 'Linguistic Fog' (fillers, stutters, code-switching). Generate a script where Turn 1 is 'I want to... uh... find a... um... restaurant', and Turn 2 is 'Actually, wait, make that... uh... specifically a sushi place, you know, muy auténtico'. This forces the synthesizing agent to perform 'Progressive Slot Extraction' across phonetic noise and bilingual barriers.
  - Incorporate 'System-Side Failure Baits' where the prompt commands the assistant to intentionally interrupt the user or provide a completely mismatched answer in Turn 2. Turn 3 must then feature the user's 'Disruptive Interruption' using markers like '[Interrupts]: Stop, I wasn't done yet!'. This contrastive data structure teaches the model exactly how to immediately halt execution and deploy a task-focused de-escalation.
  - Design 'Social-Signal Pressure' hooks where the simulated user uses raw emotional grounding to flag a systemic mismatch. Turn 5 of the script should be the user saying, '(Sighs) I've said this twice now, I need the report to be BRIEF.' The synthesized agent's internal reasoning must explicitly show: 'Detection: Intent Mismatch; User Tone: Frustrated; Corrective Action: Summarize aggressively and apologize.'
  - Build 'Code-Switched Semantic Integrity' requests where the user seamlessly drops crucial constraint nouns in a secondary language. For example, 'Book the flight, but make sure it includes el equipaje facturado.' The synthesized logic must map the embedded L2 term ('checked luggage') to the L1 task workflow without batting an eye, proving linguistic diversity doesn't degrade logical API execution.
  - Embed 'Slot-Correction Traps' in multi-turn sequence scripts. Design Turn 3 where the user says 'Book the 5 PM... no, make it 6 PM,' and Turn 4 where the user says '[Interrupts]: Wait, my partner just said 6:30!'. The synthesized assistant response for Turn 5 must skip 5:00 and 6:00 entirely and securely finalize the 6:30 parameter, verifying terminal 'Sequential Priority' logic.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
