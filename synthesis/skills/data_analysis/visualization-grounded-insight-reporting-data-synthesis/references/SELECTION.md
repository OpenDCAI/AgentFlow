# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept only if presentation is a required part of success, not an optional afterthought. The task should specify or strongly imply that the agent must generate a figure, report, or grounded summary. Otherwise the example belongs under a computation-only capability.
  - Accept only if the narrative claims can be checked against artifacts or metrics. There should be a clear path from computed result to reported insight. If the text could have been written without looking at the data, reject the trajectory.
  - Accept only if the chosen artifacts are feasible in a standard analysis sandbox. Generating a PDF figure, chart image, text file, or compact report is appropriate; building a polished production dashboard is not. This preserves alignment with the Data Analysis Agent setting.
  - Accept only if the output remains useful to a downstream reader. The report or bullet summary should communicate actual findings, not merely restate the task or the file names created. This ensures the skill teaches meaningful insight reporting.
* **Rejection Criteria**:
  - Reject cases where a chart is created but never used to support interpretation. Visualization without grounded insight is only half the capability. The example should teach the connection between evidence and explanation.
  - Reject trajectories whose summaries contain unsupported or numerically wrong claims. Even if the plot is correct, hallucinated bullet points undermine the reporting skill. Strong synthesis requires artifact-faithful narration.
  - Reject tasks where presentation is subjective and uncheckable. If the only rubric is whether the report sounds nice, the supervision becomes noisy. There must be some objective tie back to computed evidence or required artifact structure.
  - Reject examples whose main challenge is figure aesthetics rather than analytical communication. Styling matters, but the core skill here is grounded insight transfer from data to user-facing output. If the task mostly grades cosmetics, it is not a strong fit.
