# Phase 1: Environment Exploration Guide
* **Exploration Strategy**:
  - Implement Domain-Specific Syntax and API Topology Mapping. First, interrogate the environment for specific framework documentation (e.g., MOOSE Kernel definitions, Verilog timing constraints, game engine semantics) before drafting. Cross-reference naming conventions to prevent terminal mismatches.
  - Conduct a Structural Topology Audit mapping external dependencies to internal rules. For simulations, evaluate mesh dimensions or boundary names. For behavioral simulations, audit action logs versus rules to detect hidden constraints or chance node determinism.
  - Execute Hierarchical Task Decomposition using a planner. Break vague overarching goals into discrete elements (e.g., Mesh Loading -> Sub-module calculation -> Inter-module coupled Transfer) and construct a directed execution plan.
  - Perform an Environment-Driven Feedback Verification immediately upon initial code generation. Run 'dry-run' syntax tests entirely to capture domain-specific warnings (Compile errors, Convergence Faults) to proactively isolate configuration flaws early.
* **Target Trajectory Profile**:
  - Demonstrates an explicit 'Requirement-to-Description' internal alignment phase, transforming purely qualitative requests into exact quantitative data structures representing states, time-steps, or finite state machine transitions.
  - Maintains a 'Convergence and Logic Ledger', observing execution outputs from compilers/solvers (like tracking non-linear residual L2-norms, or CocoTB fail rates) and issuing surgical corrective edits targeting the fault.
  - Shows highly mature Context Window Stewardship, reading only relevant chunks of massive function documentation or avoiding dumping extensive multi-megabyte log files into thought reasoning, extracting precisely what is required.
  - Prioritizes 'Minimal State Representation' when building simulators or hardware flows, shedding irrelevant decorative variables to optimize computationally intensive searches or synthesis logic.
