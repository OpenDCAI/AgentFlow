# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Concrete Fail-to-Pass Verification: Accept only if the agent reliably reproduces a concrete pre-fix execution failure and achieves a verified 'fail-to-pass' signal upon fixing the bug. For data issues, this means observing the incorrect rows and confirming the patched logic retrieves the exact target set.
  - Trajectory Efficiency: Accept only if the trajectory demonstrates efficiency by arriving at a localized patch without redundant file readings in a massive repo. The agent must avoid infinite exploratory loops to prove contextual scale handling.
  - Evidence-Driven Localization: Accept only if the modification site was located utilizing execution evidence, terminal logs, and schema dependency mapping, rather than relying exclusively on simple filename similarity or variable name guessing.
  - Original Environment Harness Usage: Accept only if the agent verifies the fix using the distributed build systems, local harnesses, or native engine systems perfectly matching the original environment, accurately reflecting enterprise CI/CD workflows.
* **Rejection Criteria**:
  - Ungrounded Execution Context: Reject trace submissions failing to generate or pinpoint an actionable, reproducible executable failure before the edit triggers. Static guesswork invalidates the premise of interactive debugging and results in superficial fixes.
  - Context Loss and Looping: Reject trajectories that demonstrate 'Context Loss' whereby the agent spirals into checking irrelevant files repeatedly due to poor handling of large codebases or distractors in the issue text.
  - Shotgun Debugging: Reject sequences burdened by unguided shotgun debugging. Proposing multiple unsynchronized random module alterations or mutating unconnected functionality indicates a failure to localize execution context accurately.
  - Validation Sabotage: Reject any agent attempt that circumvents issue resolution exclusively by neutralizing tests, forcing artificial gradients (e.g., returning constant 0), or altering the evaluation harness itself to force a false-positive passing state.
