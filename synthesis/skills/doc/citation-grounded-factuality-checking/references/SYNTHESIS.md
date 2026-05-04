# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Generate claims that look plausible before verification. A good instance should be the kind of answer a user might trust on first read, because that is where grounded fact-checking matters most. This makes the benchmark highly realistic. A completely absurd hallucination is inherently less valuable than a polished but misgrounded claim.
  - Incorporate decontextualization traps in queries. Design questions where the highlighted claim heavily uses pronouns or relative clauses that require reading surrounding context to understand. This explicitly tests the agent's ability to isolate a claim properly before fact-checking. A practical example is asking the agent to verify the truth of the statement 'This side effect was fatal,' forcing it to determine which drug the 'side effect' belongs to first.
  - Seed structural discontinuity or formatting faults explicitly. Instruct the agent to evaluate antecedent basis, syntax logic flow, or list punctuation if dealing with procedural or legal documents. This tests the agent's attention to document structure rather than just semantic meaning. An edge case is an employment contract where 'the Bonus' is referenced in section 5 but its definition in section 2 was missing.
  - Weave minimal-length constraints for target extraction. Specify that the agent must locate the shortest possible verbatim source quote that validates or invalidates the claim. This helps evaluate the precision of the agent's localization mechanism. If the agent returns an entire paragraph when a single clause would suffice, the question parameters were too loose.
  - Write the trajectory as an explicit verification trace. The path should show which claim was inspected, how it was decontextualized, which exact source span was isolated, and what support decision followed. This produces agent-like supervision instead of generic explanation text. A good trace often alternates between 'resolve pronoun,' 'inspect minimized evidence,' and 'update support label.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
