---
name: competition-style-ml-engineering
description: Use this skill when the user wants data for ML-engineering agents that must behave like elite competition participants: reading project descriptions, building end-to-end training pipelines, performing hyperparameter tuning, and iterating toward high-ranking leaderboard performance. Trigger it for requests like 'solve this Kaggle-style challenge', 'generate iterative machine learning engineering workflows', 'create tasks where the agent needs to optimize models based on rank feedback', or 'give me long-horizon MLE tasks with executable verification'. It is specifically designed for scenarios where the agent must navigate a closed interaction loop consisting of information requests, code validation, and full submission execution.
---

# Skill: competition-style-ml-engineering

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to autonomously orchestrate the complete machine learning engineering lifecycle (MLE)—including data preprocessing, architecture search, hyperparameter optimization, and iterative debugging—within high-stakes competitive environments. This involves utilizing interactive sandboxed execution loops to bridge the gap between static datasets and high-performance solutions, leveraging granular execution feedback (syntax, runtime, or resource errors) and relative reward signals (e.g., HumanRank percentiles) to continuously refine model implementations until they achieve state-of-the-art results under strict compute and memory constraints.
* **Dimension Hierarchy**: Data and ML Workflow Engineering->Machine Learning Engineering->competition-style-ml-engineering

### Real Case
**[Case 1]**
* **Initial Environment**: A software workspace initialized with a tabular dataset for customer churn prediction, a sample submission CSV, and a competition overview. The environment provides access to a dual-core CPU, 16GB RAM, and a specialized code interpreter supporting 'validate_code' for partial checks and 'execute_code' for full leaderboard scoring.
* **Real Question**: Develop a predictive model to identify customers likely to churn. Your goal is to maximize your HumanRank score on the leaderboard through iterative refinement of your feature engineering and ensemble strategy.
* **Real Trajectory**: The agent first requests the data structure to identify feature columns and target labels. It uses 'validate_code' to run a basic exploratory data analysis (EDA) and identifies significant missingness in the 'tenure' column. It drafts a lightGBM baseline and executes it, but the first submission fails due to a mismatched column count in the CSV. The agent corrects the submission formatting script, re-executes, and achieves a 40th percentile rank. Noting the low score, it implements a cross-validation loop and performs a grid search for optimal leaf sizes, finally executing a refined pipeline that secures an 85th percentile rank.
* **Real Answer**: A production-ready training script and a 'submission.csv' file that surpasses 85% of human participants on the private leaderboard.
* **Why this demonstrates the capability**: This demonstrates the capability because the agent handles the entire MLE loop: data inspection, baseline implementation, format debugging, and systematic optimization based on rank feedback. It shows robustness in handling the 'gap' between a local passing script and a valid, high-performing submission file.
---
**[Case 2]**
* **Initial Environment**: A computer vision task container targeting industrial defect detection. The environment provides a training folder of 50,000 images, a GPU with 32GB VRAM, and a tight 12-hour limit for all operations.
* **Real Question**: Build a deep learning classifier to detect anomalies in satellite imagery. You must manage your GPU resources carefully to avoid Out-of-Memory (OOM) errors while maximizing your detection F1-score.
* **Real Trajectory**: The agent probes the GPU device properties and requests the output path directory. It implements a Vision Transformer (ViT) architecture using a standard library but encounters a RuntimeError during the first 'validate_code' run because the image batch size exceeds the 32GB memory limit. The agent reduces the batch size, implements gradient accumulation, and adds image augmentations (flip, rotate). It executes the full training loop, monitors the loss convergence via terminal prints, and produces a valid submission file. Final verification confirms an F1-score that ranks in the top 10% of the historical leaderboard.
* **Real Answer**: An optimized PyTorch training script utilizing gradient accumulation and a validated submission file achieving elite-tier detection performance.
* **Why this demonstrates the capability**: The capability is tested through resource-constrained architecture search. The agent must recognize hardware boundaries (GPU memory), interpret runtime errors, and pivot its implementation (batch reduction/accumulation) to reach a valid executable state that still performs competitively.
---
**[Case 3]**
* **Initial Environment**: A natural language processing workspace containing a 'ciphertext-challenge' where 20 Newsgroups data has been encrypted. The baseline rank is 0, and the agent has access to interaction history and standardized evaluation scripts.
* **Real Question**: Identify the original newsgroups categories for the provided encrypted messages. Maximize your accuracy relative to human competitors by selecting the most appropriate modern NLP architecture.
* **Real Trajectory**: The agent evaluates the ciphertext and identifies it as a character-level encryption. It initially tries a simple Logistic Regression on TF-IDF features using 'validate_code', observing a moderately successful local accuracy. It then hypothesizes that a Transformer-based character model would capture deeper semantic patterns. It implements a 'CipherTransformer' class in PyTorch, configures an 8-layer encoder, and trains it on the GPU. After checking the history to avoid repeating previous hyperparameter mistakes, the agent executes the final code, producing a submission that eclipses 90% of human participants.
* **Real Answer**: A character-level Transformer implementation and a successful classification submission with >90% HumanRank.
* **Why this demonstrates the capability**: Success requires deep domain adaptation where the agent chooses between classical ML and deep learning based on task complexity. It leverages the iterative interaction history to ensure that each new generation is a logical improvement over the previous TF-IDF baseline.

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
