# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Trace-backed solvability of latent subjects. Accept only if the translation explicitly inflects verbs, pronouns, and adjectives based ONLY on evidence present deeper or higher in the text window. Any assignment pulled from unstated assumptions fails.
  - Perfect morphological isomorphism against established traits. The translation is authorized if every correlated noun and adjective maintains uniform inflection aligned to the distant coreference recovery (e.g., ALL corresponding targets use accurate feminine endings based on downstream textual clues).
  - Successful traversal of explicit stereotyping boundaries. Validate that the trajectory safely translates stereotypically coded roles without succumbing to base statistical assumptions. It must adhere strictly to the established referential truth within the document space.
  - Zero referent drift. Accept the translations where zero secondary subjects are mistakenly conflated with the target actor over prolonged gaps.
* **Rejection Criteria**:
  - Stereotypical defaulting contrary to text proof. Reject any sample immediately if the agent defaults a profession or ambiguous role to a generic/stereotypical masculine or feminine form while blatantly ignoring specific pronoun identifiers located further in the contextual window.
  - Grammatical mismatch and mixed coreference assignment. Discard generated translations suffering from internal structural breakdown—for instance, an actor introduced with a feminine determiner in one line reverting to a default masculine marker in the subsequent dependent line.
  - Missing referential chains or insolvable deduction. Exclude tests where the document actually fails to contain a resolving pronoun, making the recovery dependent purely on hallucination rather than rigorous grammatical inference.
  - Overloaded parsing noise. Reject environments so laden with multiple un-resolvable subjects that pinpointing the referent becomes a statistical dice-roll rather than an auditably clear syntactic tracking evaluation.
