# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate highly coupled multi-entity retrieval prompts demanding the extraction of independent facts prior to initiating a cross-entity logic summation point. Employ heavy comparative bounds or aggregative instructions like 'Total the combined annual revenue spanning these distinct corporate entities' to mandate forced parallel-forking. This rigid instruction structure naturally targets the core agent's overarching capacity to exploit independent operational lines concurrently.
  - Incorporate overlapping variable dependencies where the most optimal scalable parallel secondary tasks are strictly identifiable only following the successful execution of an initial sequential anchor step. For example, craft an instruction like: 'First isolate the serving CEO of Corporation X, then simultaneously trace the individual birthplaces belonging to all their currently sitting board members.' This explicitly enforces a single sequential chokepoint preceding a massive parallel fan-out.
  - Inject dynamic failure constraints immediately into the task environment dictating that a mid-journey execution operation will predictably crash returning an 'insufficient records' trace. The framing user instruction must proactively demand that the model 'dynamically patch the operational plan and achieve alternative goal completion', triggering the structural workflow modification behaviors. This validates the agent's robust recovery capacity allowing node removal and reassignment when high-volume parallel operations hit broken infrastructure.
  - Introduce restrictive conditional parameters restricting operational availability enforcing deep graph-level prerequisite checking logic. Supply scenarios asserting the agent must isolate retail assets maintaining strict stock requirements alongside negative exclusion rules such as 'zero refurbishments allowed'. If the underlying solver implements ultimate purchase procedures failing to structurally retrieve pricing limits and stock-flags asynchronously firsthand, it breaches constraints and must be discarded.
  - Mandate rigorous JSON-level artifact structuring demanding the finalized generation explicitly utilizes direct '$id' placeholder syntaxes for sequential tracking blocks. Commands formatted like 'Provide the full task node dependency architecture utilizing proper pointer tokens' ensures resulting arrays capture valid computational DAG semantics. Synthesized trajectories lacking these hardcoded linking signatures before the final mathematical consolidation step represent defective unparseable plans.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
