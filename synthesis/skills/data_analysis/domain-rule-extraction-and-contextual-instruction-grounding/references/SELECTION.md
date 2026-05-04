# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept only if a documented text rule fundamentally forces a change in the analytical outcome. The trajectory must confirm standard operations without the instruction would fail or evaluate incorrectly.
  - Accept only if the identified context is successfully mapped to reproducible operational logic. This translates to SQL JOIN keys, boolean thresholds, or explicitly injected API parameters derived solely from domain files.
  - Accept only if the definition source resides purely in the provided environment context rather than generic LLM pretraining memory.
  - Accept only if a human expert would definitively derive the identical deterministic logic boundaries from the literal text provided. Reject ambiguous subjective rules.
* **Rejection Criteria**:
  - Reject cases where mapping is redundant or already baked structurally into the target table logic (e.g., if the raw column already spells out the final rule outcome transparently).
  - Reject trajectories that quote contextual instruction files but omit converting the wisdom into explicit DataFrame syntax adjustments.
  - Reject instances where rules are un-actionable, overly broad philosophical guidelines incapable of deterministic code translation.
  - Reject instances focusing purely on joining two disparate rigid tabular schemas together without requiring the intermediary translation of textual business logic.
