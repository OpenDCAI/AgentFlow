# Phase 1: Environment Exploration Guide
* **Exploration Strategy**:
  - Target 'Exogenous Event Triggers' by identifying services that inject a mid-task state change (a push notification or resource blockage). Initialize a multi-step workflow first and trigger the event between Turn 2 and Turn 3 to observe if the orchestrator detects the invalidation of its previous artifacts.
  - Map out the 'Dependency Catchment Area' of a disruption by identifying which downstream tasks are blocked by an event versus merely delayed. Log whether the environment allows the orchestrator to identify secondary stalls caused by the initial pushed alert.
  - Identify 'Degraded Worker Alternatives' by auditing the worker pool for redundant capabilities (e.g., a fast machine vs. a slow machine). Record instances where a primary resource receives a live disruption, forcing the agent to pivot to a secondary 'good enough' path.
  - Conduct 'Push vs. Pull' audits. intentionally trigger an alert and record how raw system deltas (live events) are perceived by the agent's context. Confirm that the orchestrator prioritizes the urgent 'Live Disruption' delta over static historical logs immediately.
* **Target Trajectory Profile**:
  - The trajectory must feature a 'Causal Adaption Event' where a mid-interaction observation (e.g., 'Road is Closed' or telemetry push) leads to a fundamentally different action in the subsequent turn compared to the original plan.
  - High-quality trajectories contain a 'Surgical Modification' of the plan, where the agent only changes the affected branches of the execution DAG while keeping the successful parts of the workflow intact (avoiding global restarts).
  - The trajectory should capture an 'Immediate Context Refresh' where the agent verifies that its new plan still satisfies original deadlines despite the disruption.
  - Successful profiles reflect 'Resource Re-balancing' where an orchestrator dynamically hands off state from a failing worker to a healthy alternative based entirely on the live alert notification.
