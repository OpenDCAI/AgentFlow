# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Engineer 'Asymmetric Verifier Challenges' where the agent is provide a functionally correct solution and a user-reported bug description that basic tests can't find. The quest rewards the agent for identifying the 'subtle fault' and synthesizing a minimal set of inputs that reveal it. This forces the agent into a 'Differential Analysis' loop where success is awarded only when the verifier accuracy (VAcc) reaches 100%. For example, hide a floating-point precision error that only occurs at specifically large exponents.
  - Implement 'Multi-Dimensional Constraint Lures' where the problem description contains multiple conflicting or adjacent limits (e.g., $N=2 imes 10^5$ and $A_i=10^9$). The prompt should require the agent to generate cases that specifically 'stress-test' the interaction between these limits, such as a maximum-length array filled with maximum-value integers. This creates high-density training data for 'integrated testing' rather than isolated boundary checking. A successful synthesis will result in a JSON showing the agent documenting the 'interaction risk' in its math explanations.
  - Incorporate 'Implicit Dependency Traps' by providing problems where the 'correct' behavior for certain extreme inputs is only discoverable from the ground-truth solution's implementation, not from the text. For instance, the text might not specify what happens if the input is a null graph, but the reference code handles it as a zero-weight case. The agent must use its 'Exploration' phase to discover this 'unwritten rule' and synthesize tests that enforce it.
  - Require the final output JSON to include a 'Test-Pattern-to-Signature' ledger that maps every generated input to a specific logical category. The synthesis instructions mandate that the trajectory records: 'Input Cluster 1 -> Targets: Integer Overflow; Input Cluster 2 -> Targets: Negative Cycle Detection'. This documentation makes the synthesized data valuable for training models to understand the 'intent' behind their own test-suite design. A requirement is: 'Every numerical test case must be accompanied by a logical justification for the specific values chosen.'
  - Design 'Strategic Adversarial Targets' by selecting problem instances where humans often produce 'False Positive' solutions in contests. The question should provide the agent with a 'Human Bug' distribution and reward it for maximizing its 'Detection Rate' on that specific dataset. This allows the synthetic data to teach agents to operate offensively against the specific mistakes human programmers typically make.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
