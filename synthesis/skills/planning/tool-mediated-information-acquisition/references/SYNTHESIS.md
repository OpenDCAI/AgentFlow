# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Missing Interdependent Variables: Write the question explicitly so that the agent must acquire at least two different pieces of prerequisite information before it can even begin to formulate the target plan. You should start with the approved trajectory and expose a high-level goal, intentionally withholding the sub-variables that trigger the necessary multi-tool dependency chain. For example, prompt the agent to 'Find John's favorite color shirt and order it to his current location', forcing it to look up the color, then the warehouse stock, and finally John's address.
  - Global-Local Conflict Traps: Introduce a specifically controlled trap where an initial, broad tool query will return a plausible but incorrect or outdated hint. Set the environment so that only a subsequent, high-fidelity inspection tool provides the definitive truth, specifically punishing shallow planning attempts that stop at the first summary. An excellent scenario presents a summary claiming 'The building is empty', while zooming in on the security log API reveals a late-night access event.
  - Attribute-Aware Constraint Injection: Design descriptions where the retrieval mission involves finding a 'Structured Relation' alongside an 'Unstructured Case'. The prompt should specify: 'I need to know the formal connection between X and Y, and also see a real-world case of it.' This mandates the synthesis of a multi-source plan with distinct query formats for graph tools vs encyclopedic tools.
  - Tight Answer-Trajectory Coupling: Formulate the expected output format to be inextricably tied to the unique IDs, times, or configurations retrieved during the approved exploration trace. If the capability objective involves full-plan assembly from scattered facts, demand the exact action program populated by those specific retrieved tokens. Do not ask open-ended subjective advice; ensure the LLM must generate a highly deterministic JSON mapping of the tool results.
  - Lexical Misalignment Traps: Create a synthetic environment where using a 'jargon' term in a general wiki or a 'layman' term in a research corpus results in zero hits. This forces the agent to demonstrate 'Source Alignment' by translating its queries into the correct register for each target. A successful synthesis will result in a trajectory where the agent deliberately shifts its vocabulary between tool calls.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
