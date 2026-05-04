# Phase 1: Environment Exploration Guide
* **Exploration Strategy**:
  - Begin by harvesting candidate situations where Fuzzy Tool Retrieval is the true bottleneck rather than a side effect of another failure. Inspect tool documentation to verify different agents have overlapping capabilities but varied metadata constraints (like speed, policy, or cost).
  - Force the exploration process to expose at least one concrete decision point where the agent could plausibly make the wrong routing or control choice based on semantic ambiguity.
  - Map qualitative adjectives like 'ultra-secure', 'standard', or 'best-effort' to precise performance thresholds within the expert/tool definitions. The exploration should test mapping casual requests to specific node parameters.
  - During exploration, log the exact observations that make the target behavior verifiable. These observations should include the alternatives the agent could have chosen (distractors) and the moment the correct path became identifiable.
* **Target Trajectory Profile**:
  - A good trajectory for Fuzzy Tool Retrieval must contain a decisive branching point rather than a straight-line, obvious solution. The branch should be understandable from the recorded observations, verifying why the accepted path is semantic and policy compliant.
  - The trajectory must remain compact enough that the capability signal is not drowned out by unrelated complexity. Target 2 to 6 critical actions involving capability evaluation and dynamic routing.
  - The intermediate observations must preserve the evidence needed to reconstruct why the final action is valid. The agent must acknowledge evaluating a tool's internal metadata (e.g. latency/cost profile) against the prompt's fuzzy objectives.
  - The trajectory should admit a clear contrast between success and a plausible near-miss. A near-miss could be a wrong tool with similar semantics, or a highly accurate tool invoked despite failing a background SLO or policy constraint.
