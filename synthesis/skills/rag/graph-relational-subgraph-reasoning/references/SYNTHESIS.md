# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Implement Bridge-Entity Concealment using relational descriptions. When formulating multi-hop queries, replace the name of the bridge entity with its associated attribute or relation from the first triplet in the chain. Instead of asking 'What is the capital of China, where FAW is from?', ask 'What is the capital of the country where the company that sold 2139 cars is located?'. This forces the agent to identify the company first and then the country, creating a true multi-hop traversal requirement.
  - Synthesize 'Intersection Phrasing' for conditional questions to enforce multi-constraint discovery. Generate questions that use conjunctions like 'and', 'also', or 'was both' to link two separate predicates to a single target subject. The phrasing must be natural but surgically precise, ensuring that only one subject in the entire corpus satisfies both descriptors. A classic example is 'Which writer won the 2024 literature prize AND was born in the same city as the protagonist of their novel?'.
  - Mandate exhaustive 'Set-Entity Packaging' for aggregation queries. When the subgraph indicates a one-to-many relation (Set template), the generated final answer must explicitly list all target entities in a comma-separated format or a structured list. The question should be phrased generally, such as 'List all the...' or 'What are the projects...', to trigger the agent's exhaustive extraction behavior. The ground truth must be verified to contain 100% of the matching entities found in the graph.
  - Utilize 'Inverse Relation' linguistic variants to test bi-directional graph agility. Generate questions that describe the relationship from the perspective of the object to see if the agent can traverse directed edges backward. For example, instead of asking 'Who voiced Morty?', ask 'Who is the person that performed the voice work for the character of Morty?'. This prevents the model from relying on simple keyword-ordering patterns and forces a deeper understanding of the relational semantics.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
