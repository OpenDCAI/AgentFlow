---
name: repository-level-intent-and-architectural-reasoning
description: Trigger this skill when the user wants to understand the architecture, intent, or technical details hidden within a complex codebase or its associated documentation. Use it for requests like 'explain how the payment flow works', 'find where the research paper's logic is implemented', 'summarize the RL hyperparameters in the LaTeX docs', 'tell me why this class was designed this way', or 'find the data flow for the login module across the whole repo'. It is specifically meant for multi-hop reasoning over code, PDFs, TeX files, and READMEs to bridge the gap between high-level documentation and final implementation.
---

# Skill: repository-level-intent-and-architectural-reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform multi-hop reasoning over heterogeneous repository assets—including source code, configuration manifests, and technical documentation (e.g., LaTeX sources, PDFs)—to answer complex questions regarding system architecture, design rationales, cross-file dependencies, and implementation fidelity relative to research specifications. This involves synthesizing signals from distinct module boundaries, identifying contradictions between documentation and code, and tracing information/control flows through diverse software and document hierarchies.
* **Dimension Hierarchy**: Repository Maintenance and Repair->Repository Understanding and Analysis->repository-level-intent-and-architectural-reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A large-scale repository focused on SQL linting logic. The environment includes a plugin architecture directory and a core rule-loading engine.
* **Real Question**: How is the plugin system for custom rules implemented in this repository, and what are the key components involved in discovering them?
* **Real Trajectory**: The agent starts by searching for keywords like 'plugin' and 'hook' within the core engine. It identifies a 'PluginSpec' class that defines abstract methods for rules and configuration. It then traces the call graph to a 'get_plugin_manager' function that uses a third-party library for hook management. Finally, it identifies a discovery function that iterates through distribution entry points to register external rules with the 'sqlfluff' group.
* **Real Answer**: The plugin system is implemented using the 'pluggy' library, organized around three components: 1) A 'PluginSpec' class defining hooks like 'get_rules()', 2) A 'PluginManager' that loads models and manages configurations, and 3) An entry-point registration system in 'setup.py' that allows the system to discover external rules without modifying core code.
* **Why this demonstrates the capability**: This case requires multi-hop reasoning because the answer is not in a single file. The agent must connect the abstract hook specification in one module to the runtime registration logic in another and the third-party orchestration library used to bind them.
---
**[Case 2]**
* **Initial Environment**: A web framework repository containing a large test suite for GIS (Geographic Information System) utilities and database backend wrappers.
* **Real Question**: What specific verifications does the 'test_time_field' method perform to ensure OGR time fields are correctly mapped under different GDAL version constraints?
* **Real Trajectory**: The agent locates the 'test_time_field' function in the GIS test directory. It reads the implementation and identifies conditional blocks checking the GDAL version. It observes that for versions prior to 3.4, the test expects different mapping behavior for SQLite. It also notes checks for MariaDB-specific time field quirks and identifies calls to 'get_ogr_db_string' for connection validation.
* **Real Answer**: The method performs: 1) Mapping verification of OGR time fields to native DateTimeField types, 2) Version-specific branching for GDAL < 3.4 on SQLite backends, 3) Backend-specific bug checks for MariaDB, and 4) Database driver presence validation, ensuring compatibility across heterogeneous GIS environments.
* **Why this demonstrates the capability**: Success depends on understanding locational and factual knowledge across the test logic and the environment's metadata. The agent must interpret how logic branches based on external library versions (GDAL) and backend types, demonstrating deep architectural grounding.
---
**[Case 3]**
* **Initial Environment**: A repository contains several academic LaTeX source files, Reinforcement Learning (RL) papers in PDF format, and a corresponding implementation codebase.
* **Real Question**: Find the specific hyperparameters used for the PPO agent in the 'Multi-Agent Navigation' experiment described in the LaTeX documentation and verify if those match the values in the current config file.
* **Real Trajectory**: Traverse the 'docs/papers' folder to locate the .tex file corresponding to the 'Multi-Agent' study. Search for 'PPO' or 'hyperparameters' within the LaTeX source to identify the target values (e.g., learning_rate=3e-4). Navigate to the repository's 'configs/ppo_base.yaml' and perform a line-by-line audit. Identify that the code erroneously uses a learning rate of 5e-4, creating a discrepancy between the research specs and implementation.
* **Real Answer**: The LaTeX documentation specifies a learning rate of 3e-4 for the PPO agent, but the repository config file currently implements 5e-4.
* **Why this demonstrates the capability**: This case demonstrates the synthesis of information from unstructured documentation (LaTeX) and structured code (YAML). It tests the agent's ability to perform multimodal analysis across non-code assets within a repo to validate implementation fidelity.

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
