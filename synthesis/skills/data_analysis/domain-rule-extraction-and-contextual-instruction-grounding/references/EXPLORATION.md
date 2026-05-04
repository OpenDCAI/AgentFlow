# Phase 1: Environment Exploration Guide
* **Exploration Strategy**:
  - Search for rule-bearing documents before executing primary computation. Domain-rule tasks habitually hide decisive logic in manuals, policy dictionaries, or compliance notes rather than in headers. E.g., 'target period' means nothing without a fiscal mapping manual.
  - Classify each rule as explicit, implicit, or composite. An explicit rule dictates a formula, an implicit rule requires translating a noun (like 'Tier-1 clients') to an array of SQL string IDs by checking context texts, and a composite rule links multiple bounding clauses.
  - Translate descriptive narrative logic into executable conditions as early as possible. Materialize 'Policy Exceptions' into formal pandas index exclusions. An edge case is recognizing a textual addendum physically overrides default tabular metrics.
  - Validate the scope of contextual mapping against data variance. A textual rule might assert mapping X to Y only for a subset of records, requiring boundary checking prior to globally broadcasting the dictionary override.
* **Target Trajectory Profile**:
  - A high-quality trajectory must include an explicit moment of policy mapping. The trace needs to transparently dictate where the agent consumed a rule, how it deciphered implied entities into explicit parameters (e.g. mapping Q4 to exact dates), and how this reshaped the pipeline.
  - The trajectory makes it irrefutable that standalone raw data was insufficient. Reviewers should seamlessly confirm that without textual guidance dictionaries, a vanilla statistical baseline would hallucinate or crash trying to resolve undefined terms.
  - The rule translation step remains highly scoped. If a manual rule only targets a merchant exclusion during tax-holidays, the trace ensures code logically isolates that scenario rather than applying a penalty randomly.
  - The execution concludes objectively. Regardless of abstract conversational inputs, the resulting payload is a strictly executable filter format preventing vague conversational drift.
