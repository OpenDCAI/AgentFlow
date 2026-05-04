# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Multi-Granular Spatio-Temporal Requests: Compose questions that require the agent to produce a 'Point of Interest List' with exact timestamps, transit stop IDs, and distances for 3-day to 7-day itineraries. The prompt should explicitly ask for a 'holistic representation' of the journey including meals and lodging. For example: 'Develop a 5-day plan providing an ordered sequence of all activities with starting and ending minutes.'
  - Natural Language Parameter Injection: Incorporate natural language descriptions of the mathematical distributions (μ, σ) for meal times and attraction counts in the one-shot example or task definition. This forces the agent to demonstrate 'Constraint-Aware Reasoning' by aligning its output with provided temporal guidelines (e.g., 'Lunch is best planned for 2:20 PM'). This ensures the synthetic data is high-fidelity and matches the TripCraft benchmark setting.
  - Persona-to-Action Divergence Traps: Design scenarios where a specific 'Purpose of Travel' (e.g., 'Nature-Focused') conflicts with a local city environment (e.g., 'Dense City'). The question should require the agent to perform 'Deep Search' to find the rare nature-related POIs that satisfy the persona without violating city proximity rules. This tests the agent's ability to refine sub-goals when the obvious path is blocked by user preference.
  - Conjunctive High-Intensity Bounding: Create prompts that bundle multiple hard constraints (e.g., 'Strict Budget', 'Pet-Friendly', 'No Self-Driving', 'Sports Events') to reach the 'Criticality Zone' of task planning. This forces the model to use its internal state-tracking to ensure no constraint is dropped while building the timeline. A sample setup is a 7-day trip across 3 cities where every meal must have a 4-hour gap and every lodging must be near a GTFS stop.
  - Implicit Chronological Scaling: Structure the question to gradually increase the number of cities or days to test the agent's performance in long-horizon consistency. As the number of days increases, the question should emphasize the 'Multi-City Itinerary Reasoning' needed to maintain coherent inter-city transitions. A concrete instruction is 'Coordinate our travel through 3 cities in California while managing our flight costs and time-sensitive football game.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
