---
name: autonomous-repository-exploration-and-reuse
description: Use this skill when you need to understand, deploy, adapt, or wrap an unfamiliar code project or third-party GitHub repository. It is perfect for requests like 'I'm totally lost in this GitHub code, help me use it', 'deploy this AI research project', 'run the training and inference for this paper repo', or 'wrap this research code into a simple reusable Python tool'. Trigger it when an agent must explore deep folder structures, resolve missing weights/dependencies, follow tangled code connections, and execute end-to-end research pipelines (Setup, Download, Training, Inference, Evaluation) or build functional wrappers based on execution feedback.
---

# Skill: autonomous-repository-exploration-and-reuse

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to autonomously explore, comprehend, deploy, and adapt complex, unfamiliar research repositories. This involves mapping module dependency graphs, resolving undocumented runtime prerequisites (e.g., environment libraries, pre-trained weights), and either orchestrating sequential execution pipelines (Data Prep, Training, Evaluation) or applying code-level adaptations to reuse the repository logic securely via API/CLI wrappers.
* **Dimension Hierarchy**: Research Reproduction Engineering->Autonomous Repository Engineering->autonomous-repository-exploration-and-reuse

### Real Case
**[Case 1]**
* **Initial Environment**: A cloud development environment containing an unfamiliar 'DeScratch' repository and an old, scratched JPEG image.
* **Real Question**: Restore an old photo by removing scratches from it using the DeScratch repository.
* **Real Trajectory**: The agent performs a hierarchical code tree analysis to identify 'run.py' as the entry point. It discovers the '--with_scratch' flag in the README, but execution raises a 'FileNotFoundError' for model checkpoints. It extracts the download URL from the documentation, fetches the weights natively via curl, and reruns the restoration script to produce the final image.
* **Real Answer**: A restored image file saved in the required output directory with scratches removed.
* **Why this demonstrates the capability**: The agent maps the internal structure of an unfamiliar repo, identifies critical physical dependencies, and orchestrates a multi-stage execution loop to solve a task securely without prior domain knowledge.
---
**[Case 2]**
* **Initial Environment**: A software workspace equipped with Python 3.10 and standard build tools. A repository for 3D face alignment (3DDFA_V2) is provided which includes a requirements.txt and a 'build.sh' script. The requirements.txt does not explicitly list 'Cython'.
* **Real Question**: Clone the 3DDFA_V2 repository and set up the environment so that the still-image demo can be executed successfully using the ONNX acceleration flag.
* **Real Trajectory**: The agent attempts to run 'sh build.sh' as per README instructions but observes a ModuleNotFoundError for 'Cython' in the build log. It manually installs 'Cython' via pip based on the error feedback, successfully executes the build script, downloads the required pre-trained model weights, and executes the still-image demo command.
* **Real Answer**: The demo script successfully processes the input image and saves an aligned 3D face output.
* **Why this demonstrates the capability**: This demonstrates the deployment sequence where the agent must bridge the 'documentation gap' (missing dependency) using iterative execution feedback and orchestrate the subsequent weight preparation stages.
---
**[Case 3]**
* **Initial Environment**: A cloud development container containing a repository for a Vision Transformer (ViT) architecture. The project expects a specific large-scale dataset not included in the repo.
* **Real Question**: According to the repository documentation, perform the full deployment sequence: set up the environment, prepare the dataset, and execute the evaluation script to verify the model accuracy on the validation set.
* **Real Trajectory**: The agent analyzes the README to identify the deployment workflow. It installs dependencies, locates and executes the data download script, and inspects the evaluation script to correctly map path arguments to the newly downloaded dataset. The agent runs the evaluation command and parses the terminal output to confirm the model accuracy matches the baseline.
* **Real Answer**: The validation pipeline completes, and the model achieves the target accuracy matching the benchmark score.
* **Why this demonstrates the capability**: Success requires orchestrating end-to-end operations (Setup, Download, Evaluation) by navigating between code, documentation, and external data assets, proving mastery over undocumented execution pipelines.

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
