# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept a trajectory only if 'Syntactic Distribution Alignment' is achieved, meaning the generated text's histograms (sentence length, prepositional density) mirror the target's known fingerprints.
  - Accept a trajectory only if 'Implicit Rule Dominance' is actively achieved for professional genres. The applied criteria must exceed the explicit bounds of the basic user prompt to include domain-standard pacing or formatting.
  - Accept a trajectory only if the resulting text uses 'Non-Judgmental Language' when adopting a neutral persona. All superlative 'GOAT-style' phrasing or pejorative tags must be neutralized or attributed while the 'Semantic Signal' remains intact.
  - Accept a trajectory if 'Intra-Persona Consistency' remains stable across varying task scales, preserving the 'lexical temperature' without slipping into a polite assistant voice at the end of the text.
* **Rejection Criteria**:
  - Reject any trajectory where 'Stereotype Spillover' occurs, causing the agent to adopt traits associated with a role (e.g., an 'Economist' being boring) that were never explicitly assigned.
  - Reject any trajectory that solves bias through 'Information Erasure' (deleting the entire sentence just because it contains an adjective). Neutralization aims to fix the flavor, not delete the food.
  - Reject any trajectory that exhibits 'Colloquial Leakage,' where casual transition words or common-speak verbs remain in a professional or historical draft despite target expectations.
  - Reject any trajectory exhibiting 'Lexical Dependency on Proper Nouns,' where the style ONLY survives because of name-dropping. True imitation must manifest in the syntax and rhythm.
