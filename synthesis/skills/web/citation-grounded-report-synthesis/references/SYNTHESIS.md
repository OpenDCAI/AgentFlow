# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate 'Deep & Wide Reasoning Challenges' that specifically use a 'Lineage Hierarchy' to mask target entity names. The prompt should define the target via its ancestors or relationships (e.g., 'the 1989 device designed by the creator of X') and then ask for a 'Comparative Analysis' of technical attributes across siblings (e.g., 'Compare its battery and screen tech against Y and Z'). This forces the agent into a multi-hop deductive loop before it can even begin the aggregation phase.
  - Design 'Attribute-Grain Specification Frameworks' that require the agent to generate structured data outputs like tables with 4-8 distinct, high-precision columns (e.g., CPU Architecture, Restocking Fee, State Eligibility, Launch Price). The question should be phrased to ensure that no single 'Summary Snippet' in a search engine can answer the entire query, necessitating visits to multiple primary source pages. For example, ask for 'the specific U.S. state where a service is unavailable' which is often only found in a fine-print exclusion list.
  - Embed 'Negative Policy and Exclusion Traps' by asking the agent to identify countries or categories that are 'Prohibited' or 'Excluded' based on official terms and conditions. This evaluates the agent's ability to perform high-stakes fact-checking rather than just positive recall. The synthesis should specifically target 'fine-print' information that varies across different authoritative sources to test the agent's ability to reconcile conflicting or evolving web data.
  - Construct 'Temporal Alignment Requirements' where the question specifies a context-limited date range (e.g., 'based on the 2024 occupational profile' or 'the 1988 review by Pond'). This forces the agent to ignore its parametric memory of current events or later revisions and strictly ground its report in the requested historical or specific web-state. An example is asking for the 'runner-up' of a 2005 contest to see if the agent confuses it with the same contest from 2009 stored in its training data.
  - Embed 'Analytical Synthesis Directives' that move beyond simple aggregation by asking the agent to explain the 'Trade-offs' or 'Causal Influences' behind the data (e.g., 'how these specifications influenced portability'). This forces the 'Analysis' dimension of the skill, ensuring the output provides expert insights rather than just a shallow list of retrieved numbers.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
