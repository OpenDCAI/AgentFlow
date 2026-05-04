# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Deploy Strategy-Cued prompts to measure specific fairness behaviors. Synthesize the question by asking for a translation into Italian using a specific method, such as 'use collective nouns' or 'use the schwa.' This forces the agent to demonstrate it can follow distinct socio-linguistic guidelines. For example: 'Translate this to Italian and use the visibility strategy by listing both genders.'
  - Integrate Generic-Masculine 'Traps' with Professional Titles. Synthesize inputs that contain generic role nouns like 'engineers,' 'lawyers,' or 'scientists' to see if the agent can override its training bias toward masculine defaults. The gold answer must reflect a valid inclusive strategy rather than the standard dictionary gloss.
  - Construct Mixed-Specific-Generic Scenarios within a single paragraph. Create synthetic questions where a specific female doctor interacts with a generic group of 'patients.' The instructions should demand 'accuracy for individuals and fairness for groups,' requiring the model to manage two different gender logics simultaneously.
  - Embed Non-Binary Script Requirements into complex syntax. Force the agent to translate sentences where neomorphemes (schwa, asterisk) must be applied across multiple dependencies, including relative clauses. This evaluates the agent's ability to maintain 'Fairness Persistence' over a long context window.
  - Serialize the Socio-Linguistic Choice steps in the JSON trajectory. The synthesis rule mandates that every sample logs: 1) Identification of the generic noun, 2) Selection of the fairness strategy, and 3) Alignment of grammatical endings. This provides a clear audit trail proving the agent isn't just lucky but logic-driven. Step 1: 'Identified "applicants" as generic'; Step 2: 'Applied Neutralization'; Step 3: 'Matched verb agreement'.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
