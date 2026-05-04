# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Variable-Dependency Prompting: Design instructions strictly demarcating the primary information 'source' explicitly from the execution 'sink'. Utilize sequential conjunctions outlining precisely how data captured must fuel the backend steps. For example: 'Lookup the ISBN number on the Amazon tab, and subsequently log that exact number into the blank Excel ledger.'
  - Document-to-Form Conversational Instruction: Impose natural dialogue requests describing large-scale abstractions without providing key-value instructions artificially mapping the interface context. Prompt standard users behaviors invoking holistic form-completing terminology. For instance, requesting: 'Here is my portfolio PDF, please navigate to the job portal and apply to the Software Engineering role using my background.'
  - Implicit Milestone Structuring: Instill implicit operational sequence cues like 'after you locate it', or 'once obtained' generating robust pressure for the agent to actively evaluate Short Term Memory states. Enforce logical check-gates to prevent blind rushing. For example: 'Find out the hotel check-in time first, then draft a text to my friend providing that time.'
  - Information Distractor Seeding: Cultivate visual environment states rendering several closely related proxy details requiring razor-sharp memory distillation to overcome. Guarantee the source application hosts highly viable trap elements demanding rigorous variable sifting. For example, prompting selection of an employee's mobile number, while purposefully leaving an adjacent desk number clearly visible.
  - Verification-Locked Handoff Results: Author tasks where the definitive solution rests solely inside an unguessable proprietary parameter contained exclusively inside the source app context. Make hallucinated shortcuts completely mathematically infeasible. For example, fetching an ephemeral 6-digit 2FA confirmation token generated dynamically via an internal security web container and migrating it to a desktop application.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
