# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Develop 'Multi-Attribute Fact Inquiries' that combine two or more specific, verifiable attributes (e.g., a duration and a name) about a very recent event post-2025. The wording should be designed so that Source A contains Attribute 1 and Source B contains Attribute 2, forcing at least two hops. For example, ask for the duration of a specific 2025 ceasefire and the name of the mediator presiding over it.
  - Formulate 'Underspecified Information Needs' that look like single-hop questions but require 2-4 hops of bridging logic. Deliberately strip out all bridging clues, intermediate dates, and role titles to form 'hint-free' requirements. A good example is asking 'Who was the guest of honor at the event where the [Topic X] treaty was signed?' rather than naming the year or location.
  - Construct 'Temporal Disambiguation Traps' where the starting entity has participated in several similar historical events (e.g., multiple states of emergency). The question must use a specific recent month/year and unique event context to force the agent to ignore its pre-trained knowledge in favor of fresh evidence. This ensures the synthesis evaluates the agent's ability to ground itself in the current web state.
  - Embed 'Terminology Discrepancy Traps' where the starting clue and the final answer use strictly different technical or regional vocabularies. The agent must discover the mapping between a layman term and a technical identifier (e.g., 'gang attack' vs 'December 15 Security Protocol 4') formally during an intermediate turn. This evaluates high-precision UI and terminal attribute grounding.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
