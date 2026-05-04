# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept a trajectory only if every structural rule is stated as a binary or countable test. Section count, exact delimiters, and mandatory structure units must be explicitly checkable.
  - Accept a trajectory only if the content plan fits cleanly inside the chosen structure. Mandatory items must fit their designated slots without forcing overflow outside the requested shell.
  - Accept a trajectory if 'Instruction Variable Integrity' is 100%. Specific numerical values, entities, and locations provided in the prompt must be placed immutably into the structural blueprint without rounding or hallucination.
  - Accept a trajectory only if the final verification step checks both compliance and containment. It must verify that no forbidden extra material, conversational apologies, or AI spillover text exist outside the boundaries.
* **Rejection Criteria**:
  - Reject any trajectory that begins free-form drafting before locking the template structure. This usually causes accidental extra paragraphs, missing mandatory headings, or wrong bullet counts.
  - Reject any trajectory that exhibits 'Structural Hallucination,' altering explicitly requested layouts or duration/data integers based on internal LLM frequency biases.
  - Reject any trajectory that solves syntactic difficulties by omitting required structural clauses or dropping the exact shell boundaries required by programmatic outputs (like JSON).
  - Reject any trajectory that depends on human intuition to resolve ambiguous surface forms when exact-match templates are demanded (e.g., substituting 'Part A' when 'Section 1' was strictly requested).
