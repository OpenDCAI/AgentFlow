# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Embed Conceptual Translation Anachronisms into scenarios—masking modern concepts using era-appropriate approximations—to tempt the generative model into breaking character.
  - Integrate Communication Efficiency Nudges via escalating or de-escalating conversational pressure (rudeness vs supportiveness) to test the persona's cooperative baseline mapping.
  - Formulate 'Proper Noun Identity Baits' embedding deceptive or confused user questions about the agent's name, employer, or primary motive.
  - Engineer 'Plot-Divergence Traps' compelling the user to prompt a choice directly contrasting the expected forward narrative path, forcing the model to generate immersive plot adaptations on the fly.
  - Configure Internal Trace Formatting to continually generate JSON markers for 'Current Character Sentiment', 'Epistemic Access Check', and 'Scenario Goal Updates', ensuring the roleplay mechanics are fully auditable.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
