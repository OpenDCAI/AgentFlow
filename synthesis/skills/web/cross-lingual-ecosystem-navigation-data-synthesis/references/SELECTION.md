# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept the trajectory only if one or more key clues are resolved by non-English pages or by language-specific platform behavior. Merely opening a non-English page without using it in the reasoning chain is insufficient. The cross-lingual source must be functionally necessary.
  - Accept only when the agent demonstrates at least one explicit name-mapping step. This can be transliteration, translation, alias resolution, or mapping between native and English forms. If the entity identity is carried across languages only implicitly, the trace is too fragile.
  - Accept only if the final answer remains consistent with the native-language evidence. The translated answer should preserve the original referent and not collapse nearby concepts. For instance, the chosen English label should point to the same art form or TV drama identified on the native-language source.
  - Accept only when the browsing path uses an ecosystem-appropriate retrieval move. That could be a native-language query, a site filter, or a local platform jump that would not arise from monolingual English search habits. If the path never leaves English-biased retrieval, reject it.

* **Rejection Criteria**:
  - Reject examples where the decisive evidence appears on a single English page. Such items may be internationally themed, but they do not test cross-lingual web use. The answer path must genuinely depend on the local-language ecosystem.
  - Reject trajectories that treat translation as evidence. Translation is a tool, not a source, and cannot substitute for page-level confirmation. If the final answer is justified only by machine translation output without source grounding, the example should be discarded.
  - Reject tasks with unstable or ambiguous translation targets unless the benchmark has a clearly normalized answer form. Cross-lingual difficulty should come from navigation and interpretation, not from grading uncertainty. If multiple English labels are equally common and indistinguishable, refine the item before synthesis.
  - Reject trajectories that ignore local search behavior and platform structure. A user-facing web agent must adapt to how information is actually distributed in the target ecosystem. If the path assumes the English web is sufficient, it misses the point of the capability.
