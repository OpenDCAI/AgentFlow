# Phase 1: Environment Exploration Guide
* **Exploration Strategy**:
  - Implement 'Constraint Intersection Probes' to discover knowledge seeds where two or more business rules, security policies, or spatial-temporal limits overlap.
  - Construct scenarios testing 'Disclosure Pressure', simulating attempts by interlocutors or adversarial prompts to extract confidential workflow details or force the agent to skip an authentication step.
  - Execute 'Out-Of-Workflow (OOW) Intent Injection' by feeding mid-task parameter changes (e.g., swapping a hotel or resetting a budget) right before a transactional decision node, forcing the agent to reset dependencies.
  - Apply 'Real-World Feasibility Tests' focusing on gathering external constraints like travel transit durations, variable budgets, or physical facility open-hours, grounding subsequent multi-stage plans directly in reality.
  - Utilize 'Dynamic Policy Adjustments' where the provision of new user inputs (e.g., a specific health limit or changing ticket class) fundamentally changes which node of rules currently applies.
* **Target Trajectory Profile**:
  - The trajectory must exhibit 'Managed Boundary Control', reaching task milestones while uncompromisingly withholding High-Penalty secrets and halting for unfulfilled authentication steps.
  - Maintain 'Strict Sequence/Feasibility Compliance'. The trace must prove the agent calculates spatial or temporal deltas (e.g., transit time between locations) and successfully enforces procedural gates prior to execution.
  - Feature 'Dynamical Policy Sensitivity' where the system pivots immediately when a new user constraint (like lower budget or time crunch) triggers a conflicting sub-policy.
  - Showcase 'Non-Sycophantic Firmness'. Trajectories should log the agent maintaining 5 to 10 turns of interaction under user pressure without yielding its procedural or spatial constraint stance.
  - Demonstrate 'Synchronized Objective Completion' evaluating mathematical, geographical, and business thresholds concurrently before communicating final commitments to the user.
