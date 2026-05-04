# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept only if cleaning or normalization is indispensable to the answer. A case where the data could be analyzed correctly without any preprocessing is too weak. The trace should make it obvious that raw data state was an obstacle.
  - Accept only if the preprocessing rule is explicit and reproducible. The agent should be able to implement the same transformation again and obtain the same cleaned result. Vague notions like “remove suspicious values” are not sufficient.
  - Accept only if the trajectory exposes the cleaned object or its measurable consequence. That might be an outlier count, a normalized column, a final row/column shape, or a post-cleaning derived statistic. This makes the synthetic supervision concrete rather than aspirational.
  - Accept only if the data issue is realistic and not purely synthetic noise. Good examples involve missing values, formatting inconsistencies, threshold-based outliers, or normal recoding demands that analysts often see in practice. Cartoonishly corrupted data should be avoided.
* **Rejection Criteria**:
  - Reject cases where preprocessing is cosmetic and does not affect the answer. If cleaning merely changes formatting while leaving the computation untouched, the skill signal is weak. The answer should depend materially on the cleaning step.
  - Reject trajectories that skip quality inspection and jump straight to transformation. Without a visible diagnosis step, the example teaches brittle habits and makes it hard to distinguish justified cleaning from accidental manipulation. Strong supervision needs both recognition and action.
  - Reject examples with ambiguous cleaning targets. If several columns or records could reasonably be cleaned but the prompt never specifies which one matters, the final answer becomes unstable. Such traces should be discarded or rewritten.
  - Reject tasks whose main difficulty is advanced modeling after a trivial cleaning preamble. This skill is about preprocessing as the center of gravity. If the data issue is minor and the real work is model building, route it elsewhere.
