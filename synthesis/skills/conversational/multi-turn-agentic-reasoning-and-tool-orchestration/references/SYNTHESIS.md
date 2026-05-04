# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate initial user prompts using 'Workflow Triggers' that imply a logical sequence of events, such as 'I want to find a file, edit the date, and then send it to my boss'. This forces the synthesizing agent to generate a 3-step 'Next Steps' plan at the very first turn. Avoid single-goal prompts like 'What is the time?' which do not provide enough complexity for the agent to demonstrate multi-step reasoning capabilities.
  - Incorporate 'Implicit Dependency Hooks' by describing a task where the second part is only reachable once the first part is finished. For example, 'Check if item #123 is in stock, and if so, give me the discount code for it'. This ensures the synthesized trajectory must show the agent gathering the 'Stock Status' (Observation 1) before it can even plan to look up the 'Discount Code' (Action 2).
  - Design multi-turn JSON scripts where the user's intent is 'Iteratively Refined' by adding new constraints in the middle of a planned sequence. If the agent has planned steps 1, 2, and 3, have the user interject at turn 2 with 'Wait, actually make it express shipping'. The synthesized 'Thought' must then show the agent 'Revising' the 'Next Steps' to accommodate the new parameter mid-plan.
  - Embed 'Observation-Driven Branching' in the synthesis where the tool result is a variable 'Success' or 'Failure' node. The synthesized answer must be conditional; for a 'Failure' observation, the agent should suggest the next best available step in its updated plan (e.g., 'That flight is full, but I can look for a train instead'). This tests the agent's ability to 'Refine' its plan as identified in the Pre-Act research.
  - Ensure the final QA pair includes the 'Full CRA Trace' as part of the assistant's JSON response, using the specific labels 'Previous Steps:' and 'Next Steps:'. The synthesized assistant block must contain the detailed reasoning tokens that summarize history and outline the future roadmap. This provides the 'Instruction-Tuning' signal required for smaller models to match the reasoning performance of GPT-4 as described in the paper.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
