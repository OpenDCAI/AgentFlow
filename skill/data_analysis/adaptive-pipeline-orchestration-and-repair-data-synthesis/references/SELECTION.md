# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept only if the task meaningfully benefits from staged execution and revision. Some problems are too simple to require orchestration, and those should not be forced into this skill. The trace should make multi-step control flow genuinely valuable.
  - Accept only if the trajectory records why the pipeline was revised. The reason may be a runtime error, a scope mismatch, or an intermediate result that violated expectations, but it must be visible. This is crucial for later synthesis of repair-oriented data.
  - Accept only if the workflow remains within a disposable analysis environment. Planning, code execution, and repair should all happen inside a notebook, Python sandbox, or equivalent analysis toolchain. The skill should not drift into general software engineering or product debugging.
  - Accept only if the final plan is materially better than the initial one. A strong example teaches that adaptation improved retrieval, preprocessing, modeling, or formatting in a visible way. If revision changes nothing important, the case is weak.
* **Rejection Criteria**:
  - Reject trajectories that succeed in one shot with no meaningful control-flow choice. If the task never requires planning or repair, it should be routed to a narrower analytical capability. This skill is specifically about adaptive workflow management.
  - Reject cases where the repair step is purely syntactic. Fixing a missing parenthesis may happen in practice, but it does not teach analytical orchestration. The revision should address pipeline logic, evidence alignment, or execution strategy.
  - Reject examples that depend on broad software-development context outside the data-analysis sandbox. General codebase refactoring, package maintenance, or system-level debugging violate the Data Analysis Agent boundary. The workflow should stay tied to deriving insight from a dataset.
  - Reject traces with uncontrolled tool chatter and no convergent structure. Adaptive pipelines should still look purposeful and inspectable. If the agent keeps opening files and rerunning code without a clear evolving plan, the case is too noisy.
