# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Verification of Ground-Truth Sequence Recovery: Accept only if the evaluator determines success via a measurable, factual metric change (latency drop, exact file verification, specific correct role handoff) rather than conversational vibes.
  - Identification of First-Error Step (t*) & Blame Transition: Accept PRM trajectories that explicitly map the temporal index (t*) where the agent first deviated, providing concrete 'Logical Error', 'Functional Error', or 'Critic Harm' rationales.
  - Detection of Action-Coordinate Alignment: For UI tasks, accept only if the evaluator tests 'Coordination Errors' where the executed tool or click coordinate mechanically misaligns with the visually intended element.
  - Strict Instruction Adherence: Accept only sequences where the final state is verified to be 100% consistent with all positive and negative constraints in the prompt, catching missing nuances (e.g., bolding instead of highlighting).
* **Rejection Criteria**:
  - Ambiguous Error Origin Attribution: Reject any evaluation that issues a systemic 'Task Failed' verdict without pinpointing the exact step, tool execution, or agent role responsible for initiating the failure.
  - Visual Understanding Blindness & Sycophancy: Categorically reject samples where the judge simply believes the agent's self-reported thought process ('I clicked the button, so it is registered') while ignoring missing visual or system log evidence.
  - Redundancy and Latency Neglect: Reject trajectories where an evaluation awards perfect marks to an agent that completed a 3-step task via a 20-step brute-force infinite loop without penalizing its process efficiency.
  - Inconsistent Consensus under Perturbation: Discard any sample where strict unanimous voting falters across different prompt perspectives (e.g., the safety perspective finds a deleted folder, but the general success perspective ignores it and gives 5/5).
