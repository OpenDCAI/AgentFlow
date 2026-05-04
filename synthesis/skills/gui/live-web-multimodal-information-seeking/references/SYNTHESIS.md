# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - E-commerce Deep Intelligence Prompting: Design instructions focusing on 'actionable intelligence' that resides on specific interactable subpages, such as 'Verify the HS code on the official customs tracker' or 'Extract the merchant license details from the business registry'. Use phrasing that implies the data is 'hidden' or 'deep,' forcing the agent to navigate through the site's structural layers. For example: 'Find the ECCN classification for this part; you may need to check the technical compliance tab on the product page.'
  - Stateful Variable Dependency Seeding: Formulate multi-step questions where the 'target' for the second step depends on a variable extracted in the first step (e.g., find a part number, then find that part's regulatory status on a different site). This creates a mandatory cross-site information handoff. For instance: 'Identify the company name on this landing page, then go to the WHOIS registry and find who registered that company's domain.'
  - Thinking-Action-Observation Loop Synthesis: Construct the trajectory JSON to follow a rigorous thinking-heavy format. Each step must define a <Thinking> block (analysing the screen), a <Memory> block (storing extracted IDs), and a <Next Goal> block (planning the deep jump). This ensures the training data replicates the RISK-R1 reasoning framework. For example, a step should record: 'I see a Specs tab; I will click it to find the ECCN which isn't on the summary page.'
  - Factual Answer Multi-Constraint Binding: Require the final answer to include at least two distinct factual attributes (e.g., 'Price' and 'HS Code' or 'Status' and 'Inspector Name') to ensure exhaustive extraction. This prevents the agent from finishing prematurely after finding a single piece of evidence. A concrete question would be: 'What is the current logistics status of shipment X, and what is the exact delivery date mentioned in the internal logs?'
  - Difficulty-Grated Curriculum Seeding: Categorize synthesized tasks into 'Easy' (1-2 clicks), 'Moderate' (3-5 clicks), and 'Difficult' (6+ clicks/multi-site). Use these labels to apply 'Level Reweight' logic during selection to prioritize high-complexity reasoning paths. Framing a task like 'Reconcile this logistics status with the customs inspection result' ensures a long-horizon, high-difficulty information retrieval chain.
  - Attribute-Dense Distractor Placement: Place visually similar but functionally incorrect data points near the target extraction node (e.g., placing a 'US HS Code' next to a 'Global HS Code'). This tests if the agent follows specific technical constraints over simple keyword matching. For example, if the prompt asks for 'Part X,' the environment should show 'Part X-Pro' and 'Part X-Lite' to test fine-grained grounding precision.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
