# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Streaming Multi-Task Narratives: Design overarching instructions establishing consecutive linked objective streams traversing diverse functional requirements executing sequentially across dynamic temporal progression loops. Employ explicit user directives mandating the central model to 'synthesize incoming assignments referencing your cataloged prior experiences to iterate subsequent action reliability'. Structuring progressive series evaluating Task A (Find Object), Task B (Verify Condition), escalating into Task C (Composite Action) tests aggregate continuous knowledge retention securely.
  - Scenario-Grounded Intent Phrasing: Formulate primary user questions using abstract 'Usage Scenarios' (e.g., 'a relaxed gathering with friends', 'focusing on a difficult project') rather than listing explicit physical attributes. This phrasing forces the agent to enter a mandatory 'Intent-to-Attribute' conversion phase by mapping the vague scenario against historical interaction templates. For example, 'I need some ambient audio for introspective moments' perfectly triggers the necessity for phased template retrieval prior to direct querying.
  - Contrastive Success/Failure Scenario Seeding: Synthesize deep operational environments granting access to contrasting historical trace pairs specifically highlighting one optimally executed sequence alongside a matching parallel failure manifestation. Prompt the core modeling engine deriving corrected algorithmic maneuvers leveraging the successful architecture concurrently avoiding heavily documented negative friction vectors reliably. Forces explicit engagement processing targeted diagnostic evaluations refining strategic implementations pre-execution effectively.
  - Strategic Ambiguity Injection: Explicitly embed colloquial phrases that broadcast extreme user uncertainty within the natural language prompt, such as 'I'm entirely unsure about the specific venue' or 'I don't know what components are typically needed.' This explicitly targets the agent's 'Thought-Augmented' capacity forcing it to dynamically subdivide the necessity into 'Potential Sub-Scenarios' based on generalized pattern memory. A failure here constitutes an agent outputting a single deterministic list without utilizing retrieved multi-pronged templates.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
