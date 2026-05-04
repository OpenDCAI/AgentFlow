# Phase 1: Environment Exploration Guide
* **Exploration Strategy**:
  - Stream-Level Task Sequencing: Explore not isolated tasks but ordered task streams where later tasks share partial structural/procedural overlap with preceding ones.
  - Experience Abstraction Strategy: Abstract raw historical trajectories into transferable knowledge schemas detailing required precondition checks, logical subgoal order, and reusable action dynamics.
  - Non-Stationary Adaptation Stress-Testing: Present environments where previous tasks are periodically re-introduced after learning novel interactions to monitor for stability decay in baseline skills.
  - Retrieval-Trigger Identification: Record explicit structural patterns (e.g., 'satisfy obstacle precondition before transfer') within earlier solutions, encoding them as triggering cues to recall logic during related future observations.
  - Failure-Aware Memory Refinement: Distill both failed and successful historical paths into specific corrections (e.g., identifying why opening a door with full hands failed) to constructively alter future routing selections.
* **Target Trajectory Profile**:
  - At Least Two Linked Tasks: The profile strictly contains an earlier source task alongside a later target task possessing meaningful, reusable procedural transfer value.
  - Reusable Procedural Core: Retain trajectories illustrating that the earlier knowledge specifically guided subgoal order or object manipulation strategy, avoiding pure semantic vocabulary associations.
  - Visible Adaptation Opportunity: The later trajectory must highlight a specific breakpoint where retrieving prior lessons noticeably altered an action choice or accelerated physical completion limits.
  - Performance Retention Checks: Premium streams feature a later reversion evaluating the agent's baseline competence on the initial task to prove it bypassed catastrophic behavioral forgetting.
  - Performance-Sensitive Transfer: The later trajectory concretely avoids a previous historical mistake or minimizes step counts, proving memory actually altered operational yield.
