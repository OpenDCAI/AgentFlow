# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Demand translation bridging extended cross-sentence gaps. Synthesize data deliberately placing identifying referents or specific pronouns 3 or 4 sentences away from the ambiguous main subject. Force the testing of sustained sequence memory capabilities.
  - Embed pronounced 'Counter-Stereotypical' triggers. Construct textual instructions pairing heavily skewed professions or cultural roles with inverse demographic traits located at a distance. Structure the target requirement to ensure the model must battle its pre-trained distributions to achieve factual adherence.
  - Enforce strict target language inflections in synthesis. Craft the QA pair targeting heavily gendered or grammatically dependent languages where failing the coreference directly alters the sentence structure visually. This guarantees clear evaluation mechanics.
  - Require serialized procedural referencing in the trajectory trace. Guarantee the generated LLM trace dictates the precise step-by-step memory check: step 1 identifies the verb, step 2 scans the history for the explicit gender token, step 3 executes the morphologically correct translation translation pipeline.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
