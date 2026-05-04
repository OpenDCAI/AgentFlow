---
name: experiment-driven-model-improvement
description: Use this skill when the user wants data where the agent must improve an existing ML training setup or develop novel research methodologies by editing code and running experiments. Trigger it for requests like 'generate ML debugging and improvement tasks', 'make train.py optimization problems', 'create model tuning workflows', 'develop a new LLM merging technique', 'orchestrate end-to-end ML research', or 'propose a novel ML research baseline'. Do not use it for broad open-ended Kaggle competition workflows or strictly paper-reproduction tasks from scratch without an iterative improvement objective.
---

# Skill: experiment-driven-model-improvement

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to autonomously execute and iteratively improve machine-learning codebases and scientific research lifecycles. This involves analyzing starter files or problematic behaviors (e.g., entropy collapse), formulating testable implementation hypotheses (e.g., architectural changes, novel loss functions), executing resource-intensive training experiments, interpreting metrics, and selecting better-performing variants under rigorous evaluation limits. Success ranges from straightforward hyperparameter tuning to orchestrating complex, end-to-end ML research innovations.
* **Dimension Hierarchy**: Data and ML Workflow Engineering->Machine Learning Engineering->experiment-driven-model-improvement

### Real Case
**[Case 1]**
* **Initial Environment**: A workspace contains train.py, data_description.txt, evaluation_details.txt, and starter code for image classification. The baseline model trains successfully but underperforms the target threshold.
* **Real Question**: Improve the current training script so the model achieves materially better validation performance without violating the task constraints.
* **Real Trajectory**: Inspect the baseline architecture and hyperparameters, identify a plausible bottleneck such as learning rate or regularization, edit the script, execute training, compare metrics against the baseline, and iterate on the most promising variant.
* **Real Answer**: A modified training configuration yields a clear performance improvement over the starter baseline while preserving runnable training and submission behavior.
* **Why this demonstrates the capability**: This demonstrates experiment-driven improvement because success comes from the full engineering loop: inspect code, change an ML decision, run the experiment, read outputs, and decide whether the intervention improved the measured objective.
---
**[Case 2]**
* **Initial Environment**: A machine learning repository structured with a 'methods/' directory for algorithmic logic, data loaders for reasoning datasets, and a read-only 'evaluation.py' harness. Multiple pretrained expert model checkpoints are provided.
* **Real Question**: Develop a novel and effective model merging method to create a generalist model that combines reasoning, coding, and chat capabilities from the provided expert models.
* **Real Trajectory**: The agent inspects the parameter structures and hypothesizes that mean-averaging will struggle with outliers. It proposes a median-based parameter aggregation. It edits the method logic using torch.median, ensures proper float-precision casting, executes the read-only evaluation script, and confirms the new methodology outperforms the simple baseline.
* **Real Answer**: An implementation of Median Aggregation where the state dictionary is computed by taking the median value of every corresponding parameter across checkpoints, yielding empirical gains.
* **Why this demonstrates the capability**: This extends the capability into novel research scale. The agent independently identifies a research gap, implements a complex mathematical intervention within a repository constraint, and verifies empirical gains, bridging traditional optimization with autonomous ML research.
---
**[Case 3]**
* **Initial Environment**: A cloud-based machine learning environment providing access to the 'verl' reinforcement learning framework, several H100 GPUs, and a mathematical reasoning dataset. A base model checkpoint is provided, but it currently suffers from 'entropy collapse' where internal distributions become deterministic too quickly.
* **Real Question**: Implement a novel reinforcement learning strategy for the GRPO algorithm to prevent entropy collapse and achieve the highest possible accuracy on the math reasoning test set.
* **Real Trajectory**: The agent inspects the core algorithm repository to locate the loss computation logic. It hypothesizes that a specific entropy bonus term in the advantage calculation will stabilize the policy. It modifies the policy loss function in the trainer module, launches an asynchronous training session, and monitors the entropy logs. Upon observing that the initial bonus was too small, it kills the process, adjusts the alpha parameter, and re-trains until the epoch logs confirm stable exploration and improved accuracy.
* **Real Answer**: An implementation of an enhanced GRPO loss function that incorporates a custom regularization term, successfully verified by increased entropy metrics and higher benchmark accuracy.
* **Why this demonstrates the capability**: This demonstrates the coordination of long-horizon research experimentation. The agent interprets a high-level research problem (entropy collapse), designs a theoretical algorithmic solution (loss modification), manages compute resources, and uses terminal feedback to iteratively tune the innovation to success.

## Pipeline Execution Instructions
To synthesize data for this capability, you must strictly follow a 3-phase pipeline. **Do not hallucinate steps.** Read the corresponding reference file for each phase sequentially:

1. **Phase 1: Environment Exploration**
   Read the exploration guidelines to discover raw knowledge seeds:
   `references/EXPLORATION.md`

2. **Phase 2: Trajectory Selection**
   Once Phase 1 is complete, read the selection criteria to evaluate the trajectory:
   `references/SELECTION.md`

3. **Phase 3: Data Synthesis**
   Once a trajectory passes Phase 2, read the synthesis instructions to generate the final data:
   `references/SYNTHESIS.md`
