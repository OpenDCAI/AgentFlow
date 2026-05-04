# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept a trajectory only if the 'Fact-to-Conclusion Integration' is explicitly visible and bidirectionally robust within the synthesized text. The agent must prove that for absolutely every high-level conclusion reached, a specific condition or factual instance was visibly mapped.
  - Accept a trajectory only if 'Source Diversity Cardinality' matches the prompt's complexity. A multifaceted global framework analysis must convincingly invoke disjointed source domains (e.g., Law, Business, Science) where present.
  - Accept a trajectory only if factual aggregation reaches an exceptionally high coverage saturation. Massive documentation requirements must manifest a dense distribution of precise entities or numeric metrics across the synthesized output.
  - Accept a trajectory only if it proactively addresses 'Alternative Interpretations' or plausible counter-arguments encountered within the raw evidence to prove it did not cherry-pick specific facts to fit a pre-ordained verdict.
* **Rejection Criteria**:
  - Reject any trajectory that mistakenly equates 'High-Quality Analysis' with mere sequential 'Summarization' of the provided sources. If the generated report reads like a disjointed bulleted list of basic abstracts without an overarching argumentative frame, it entirely fails.
  - Reject any trajectory exhibiting 'Conclusion-First Hallucination,' where the model instantaneously decides upon a preferred outcome and subsequently hallucinates fake evidence to support it.
  - Reject any trajectory demonstrating 'Informational Piling' or 'Domain Myopia,' wherein it collects a massive count of articles but draws them uniformly from a singular perspective while ignoring other critically provided dimensions.
  - Reject any trajectory that fails a baseline 'Causal Linkage Check' by assuming correlation equals definitive causation without explicit contextual proof.
