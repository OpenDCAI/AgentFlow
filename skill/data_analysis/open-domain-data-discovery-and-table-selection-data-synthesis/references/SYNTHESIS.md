# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write questions so the user names the business or analytical need, not the table name. The wording should mention entities, measures, and constraints in everyday language while withholding direct file identifiers. For example, ask for the highest eligible free rate in Alameda County schools rather than naming the exact dataset that stores the rate.
  - Place ambiguity in the retrieval step, not in the answer format. The answer should usually be a short number, string, or small list once the correct table is found. An edge case to avoid is a question that is ambiguous both about which table matters and about what final aggregation is wanted.
  - Ensure that at least one plausible distractor table exists in the explored environment. The distractor should share partial vocabulary with the target but differ on year, geography, metric definition, or level of granularity. This creates the “find the right sheet first” behavior that ordinary users often want without introducing arbitrary confusion.
  - Preserve a compact but faithful trajectory in the final JSON. The trajectory should show the retrieval hypothesis, candidate comparison, decisive inspection, and final extraction step. A good synthesized example feels like a careful analyst searched, verified, and then answered, rather than a model that guessed the table correctly on the first try.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
