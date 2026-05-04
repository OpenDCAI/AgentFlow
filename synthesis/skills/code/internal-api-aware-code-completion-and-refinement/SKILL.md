---
name: internal-api-aware-code-completion-and-refinement
description: Use this skill when you need to finish writing a block of code that relies on functions or classes defined elsewhere in the same project rather than standard libraries. It should be triggered by layman requests such as 'finish this function using our internal helpers', 'complete this call but I don't remember the exact sub-module function', 'help me use our custom API to register this dataset', or 'fix my code where I'm guessing the name of our team's functions'. Do not use it for general Python library completion; use it for project-specific internal logic that isn't found in online docs.
---

# Skill: internal-api-aware-code-completion-and-refinement

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform high-fidelity code completion and refinement by inferring and retrieving project-specific internal API information, including signatures and functional semantics, without relying on existing import statements. This involves a multi-stage process of generating an initial code draft, extracting candidate call patterns or functional intents from the draft, and querying a custom-built repository knowledge base to resolve hallucinations and satisfy implicit cross-file dependencies.
* **Dimension Hierarchy**: Repository Maintenance and Repair->Repository Understanding and Analysis->internal-api-aware-code-completion-and-refinement

### Real Case
**[Case 1]**
* **Initial Environment**: A large-scale software repository focused on image processing and dataset registration. The current file `register_cityscapes.py` contains a logic block for registering semantic segmentation metadata but is missing the final internal function call to load the data.
* **Real Question**: Complete the following code block to register the cityscapes semantic segmentation task: `DatasetCatalog.register(sem_key, lambda x=image_dir, y=gt_dir: [code to complete])`.
* **Real Trajectory**: The agent performs a repository audit and generates an initial draft, which incorrectly assumes the internal function is named `load_cityscapes_sem_seg`. Using this identifier as a seed, the agent queries the internal API knowledge base and discovers a functionally similar, actual function called `load_cityscapes_semantic` in `datasets/cityscapes.py`. The agent then verifies the parameters of the real function and updates the code to use the correct name and argument structure.
* **Real Answer**: y=gt_dir: load_cityscapes_semantic(x, y)
* **Why this demonstrates the capability**: This demonstrates the capability because the agent had to resolve a hallucinated API name by inferring the intent from a code draft and looking up the correct project-specific internal API, which was not documented in standard libraries.
---
**[Case 2]**
* **Initial Environment**: A deep learning framework repository used for model training and deployment. The developer is editing the `DefaultTrainer` class in `trainers/base.py` and needs to initialize the logger writers using project-specific utilities.
* **Real Question**: Initialize the `self.log_writers` variable within the `__init__` function of the `DefaultTrainer` class using the appropriate project-defined utility.
* **Real Trajectory**: The agent creates a draft which incorrectly uses a generic `getattr` pattern to find common writers. Realizing this pattern is likely a placeholder, the agent summarizes the intent as 'obtaining log writers from project settings' and searches the functional semantic index. It identifies the internal API `get_log_writers` in the project's utility module, which perfectly matches the required behavior. The agent then implements the call while passing the existing `self.opts` and `self.save_location` variables.
* **Real Answer**: self.log_writers = get_log_writers(self.opts, save_location=self.save_location)
* **Why this demonstrates the capability**: This illustrates the capability to move from a vague functional intent to a concrete internal API call by bypassing superficial code similarity and grounding the solution in the project's actual functional repertoire.

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
