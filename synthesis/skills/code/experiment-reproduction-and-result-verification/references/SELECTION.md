# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept only if the trajectory runs or directly validates the designated execution entrypoint in a fresh or clearly controlled environment. The agent must be checking reproduced outputs, not merely reading code and guessing what would happen. This is foundational for result verification.
  - Accept only if evidence is tied back to explicit requirements or success criteria. Logs, files, and tables should each be mapped to what they prove or fail to prove. Without this mapping, the task becomes generic experiment running instead of benchmarked verification.
  - Accept only if the trace distinguishes full matches from partial matches. Many research benchmarks intentionally decompose success into subrequirements. Preserving that decomposition is critical for producing useful synthetic data.
  - Accept only if the trajectory checks for missing, stale, or hard-coded outputs. Verification tasks are particularly vulnerable to false positives if the agent trusts existing artifacts blindly. A good trace either regenerates them or verifies their provenance carefully.
* **Rejection Criteria**:
  - Reject traces that never execute or otherwise validate the claimed reproduction pipeline. Reading a repository and asserting that it should work is not result verification. This capability depends on empirical evidence.
  - Reject trajectories that conflate script completion with scientific reproduction. A script can finish while producing wrong metrics, incomplete tables, or misconfigured runs. Such traces are too shallow for high-quality synthesis.
  - Reject traces that ignore the benchmark’s grading structure. If the source benchmark separates code-development, execution, and result requirements, the synthetic trace should not collapse them into one undifferentiated success label. Doing so removes important capability distinctions.
  - Reject traces that trust pre-existing output files without checking whether they were produced by the current run. Stale artifacts are a major source of false confidence in reproduction settings. Any such shortcut undermines the validity of the final example.
