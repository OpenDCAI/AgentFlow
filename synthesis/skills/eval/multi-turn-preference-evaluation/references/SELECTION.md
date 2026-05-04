# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - At least two verifiable context turns: The sample must contain either two explicit user-assistant turns or a distinct user persona log coupled with a conversational turn.
  - Preference justification via cross-turn integration: The exploratory notes must document at least one concrete piece of evidence (a memory lapse or a contextual carryover) to justify the verdict.
  - Both candidates plausible on first-read: To ensure difficulty, both conversational candidate responses should look 'acceptable' if judged strictly without the earlier context.
  - Implicit need coverage for long-term cases: If using multi-session data, the item must contain at least two distinct implicit needs that a successful model should have inferred.
* **Rejection Criteria**:
  - Turn independence and isolated context: Reject multi-turn samples where the later turn can be accurately answered and evaluated without any knowledge of the prior turns.
  - Generic personalization hallucination: Reject evaluations that award points merely because a model said 'I remember you' or used a generic pleasantry, if it functionally ignored the substantive context.
  - Obvious winner from style alone: Reject pairs where one assistant completely breaks formatting, starts speaking gibberish, or acts identically terrible on turn one, trivializing the multi-turn comparison.
  - Log-Dialogue Contradiction: Reject samples (if testing long-term traits) where the generated persona profile introduces physically impossible conflicting user states across timelines.
