---
name: paper-to-code-implementation-fidelity
description: Use this skill when the user wants to implement complex scientific algorithms or methodologies from research papers, LaTeX formulas, or technical documentation into a code repository. Trigger it for requests like 'implement the research method from this PDF', 'code the formula from Section 3', 'refine my AI model implementation using these expert reviewer notes', or 'fix the discrepancies between our math derivation and the current code'. It is specifically designed for high-precision implementations requiring deep grounding in research artifacts, domain-specific terminology, and iterative refinement of mathematical logic based on hierarchical expert feedback.
---

# Skill: paper-to-code-implementation-fidelity

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to transform scientific publication artifacts—including text, LaTeX mathematical formulations, architectural diagrams, and citation lineage—into functionally correct, high-fidelity code within complex repositories. This involves performing interactive refinement loops where initial implementations are compared against reference formulas, diagnosing semantic misalignments between theory and implementation, bridging implicit domain knowledge gaps (e.g., terminology or standard library conventions), and ensuring architectural integration without reinventing existing repository utilities. Success is determined by the implementation's adherence to scientific specifications and its ability to replicate reported numerical results or pass expert-level verification checks within iterative development workflows.
* **Dimension Hierarchy**: Research Reproduction Engineering->Paper-Grounded Implementation->paper-to-code-implementation-fidelity

### Real Case
**[Case 1]**
* **Initial Environment**: A research project focused on deep learning decoding strategies. The workplace contains a paper description defining the 'Min-p sampling' algorithm (calculating a context-dependent threshold p_scaled = p_base * p_max and filtering tokens) and a skeleton class inheriting from a standard logits processor.
* **Real Question**: Implement the `__call__` method for the `MinPSampler` class based on the provided Min-p sampling algorithm description, ensuring the `min_tokens_to_keep` safeguard is strictly enforced according to repository standards.
* **Real Trajectory**: The agent identifies the core formula in the LaTeX description and implements an initial version using `torch.softmax` and `torch.masked_fill`. After receiving feedback that the manual boolean indexing used for 'min_tokens_to_keep' can cause batch-level discrepancies and deviates from the project's preferred 'sort-gather-scatter' pattern, the agent revises the implementation. It implements `torch.argsort` on the scores, gathers the removal mask to align with sorted indices, resets the first 'min_tokens_to_keep' positions to 'False', and scatters the mask back to the original vocabulary order before applying the final filter mask.
* **Real Answer**: A functionally correct implementation of Min-p sampling that utilizes the robust sort-gather-scatter pattern for token retention, ensuring 100% alignment with the canonical research implementation.
* **Why this demonstrates the capability**: This case demonstrates the capability to translate complex LaTeX-based logic into precise tensor operations while resolving semantic misalignments (T2) and adhering to repository-specific architectural idioms (T4) through iterative refinement based on expert feedback.
---
**[Case 2]**
* **Initial Environment**: A cloud development environment contains a repository for LLM in-context word acquisition, the original scientific paper describing morphological word learning, and a set of word frequency data files. The goal is to investigate how existing English word meanings interfere with new word learning by creating custom dataset variants.
* **Real Question**: Modify the implementation to generate new dataset variants by replacing target words with existing words from frequency files (Noun/Verb/Adjective). Use spaCy with lemminflect to ensure replacements match the original morphology, and run 5-shot experiments across 'Top' and 'Bottom' frequency groups to save results in res_top.json and res_bottom.json.
* **Real Trajectory**: The agent audits the repository to identify the dataset generation module and the existing templates. It locates the frequency files in the sub-folders and implements a replacement logic using the lemminflect and spaCy libraries to preserve parts-of-speech and tense. It updates the evaluation loop to iterate through the specific frequency cohorts, triggers the model inference using the specified template, and records the results in the corresponding JSON files. Finally, it creates an execution script to automate the entire generation and inference pipeline.
* **Real Answer**: A set of implementation patches that generate morphological-aware dataset variants and an executable script that produces the requested accuracy result files matching paper-reported trends.
* **Why this demonstrates the capability**: This illustrates 'Hypothesis-Driven Research Extension' where the agent implements unmasked research ideas using external data files. It requires bridging the gap between abstract research instructions and concrete file-system dependencies while maintaining scientific implementation rigor.

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
