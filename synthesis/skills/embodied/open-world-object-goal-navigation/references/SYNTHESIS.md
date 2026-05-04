# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate Multi-Layer Target Prompts: Structure the synthesized question to deliberately blend object nomenclature with spatial and descriptive bounds. Utilize templates mimicking: 'Seek out the targeted object matching category = [Class], utilizing parameters: [Size], [Hue], positioned structurally near [Anchor]'.
  - Enforce Non-Target Distractor Contexts: To force maximum exploitation of semantic filtering, actively simulate alternative identical objects stationed in wildly incorrect geographic contexts (e.g., a blue cup sitting uselessly on a distant floor alongside the designated blue cup sitting naturally on the table).
  - Synthesize Memory-Dependent Handoff Logic: Compose internal reasoning sequences establishing the associative memory bridging metric. The generated textual trace must contain segments narrating: 'Visualized a refrigerator; internal ontology maps refrigerator closely with target: fruit; prioritizing current spatial cluster for granular inspection.'
  - Ensure Pure Egocentric Constraint Boundaries: Frame the textual outputs so that responses rely completely upon sequentially acquired visual updates, aggressively avoiding the usage of omnipotent phraseology like 'Looking at the entire house map'. Vocabulary must strictly anchor into first-person exploration transitions.
  - Document Precision Stop Validations: The terminal data generation string must explicitly justify the termination event based on physical proximity scales, phrasing the 'Goal Met' logic strictly around: 'Target parameters visually corroborated, proximity constraint threshold breached, initiating halt sequence.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
