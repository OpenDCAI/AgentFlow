# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept the trajectory only if at least one step would be ambiguous or wrong without screenshot-level grounding. This criterion ensures the multimodal channel is functionally necessary. If a text-only agent could execute the same path with no loss, reject the example.
  - Accept only when the trajectory explicitly references both page structure and visible state. The agent should use structural identifiers such as refs, fields, or HTML roles together with visual cues such as order, visibility, or current screen context. One modality alone is insufficient for this capability.
  - Accept only if the task includes an interface change after an action. This guards against shallow one-screen tasks that do not stress multimodal tracking. A modal opening, panel switch, forwarded email view, or results page update all satisfy the requirement.
  - Accept only if success can be judged from the resulting UI state or a directly associated system outcome. The benchmark should not rely on hidden backend state that the agent cannot perceive. For example, a forwarded message view or clicked result state is preferable to an invisible server-side flag.

* **Rejection Criteria**:
  - Reject examples where all necessary cues are available in clean text and static order. Such tasks do not actually require multimodal grounding. A screenshot should be necessary for at least one decision.
  - Reject trajectories that confuse DOM order with user-visible order when the task is framed from a user’s perspective. If the seventh result in the DOM is not the seventh visible result, the example is malformed for grounding. The synthesized task must follow the interface the user sees.
  - Reject tasks whose success depends on inaccessible or unstated UI assumptions. The agent should be able to infer the correct action from available screenshot and structure evidence. If the intended answer requires human common sense about a hidden style rule, it is out of scope.
  - Reject examples that are really OCR or static image questions disguised as web tasks. A valid web-grounding item still needs actionable page structure and interactive state. If no browser interaction is needed, the capability target is wrong.
