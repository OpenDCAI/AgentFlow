---
name: stateful-multi-file-code-refactoring
description: Use this skill when the user wants to reorganize, clean up, or restructure code across multiple files without changing its functional behavior. Trigger it for requests like 'refactor this project', 'clean up the code structure', 'move these functions to a separate utility file', 'consolidate these classes', or 'change the naming convention throughout the whole repository'. It is specifically designed for complex, multi-step changes where the agent must track its own previous edits and handle temporary errors while moving logic between different files.
---

# Skill: stateful-multi-file-code-refactoring

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform large-scale code refactoring by maintaining a consistent mental model of the codebase's state across extended trajectories. This involves deep dependency exploration, compositional reasoning to execute inter-file changes, and the ability to navigate temporary 'broken' states during structural transitions while preserving implementation fidelity verified by structural AST constraints.
* **Dimension Hierarchy**: Repository Maintenance and Repair->Multi-File Architectural Refactoring->stateful-multi-file-code-refactoring

### Real Case
**[Case 1]**
* **Initial Environment**: A Python web framework repository (similar to Flask) containing multiple sub-modules for handling requests, responses, and helpers. The environment includes terminal access to search and edit the entire directory structure.
* **Real Question**: Rename the internal helper function 'send_from_directory' to 'send_from_directory_helper' in the core helpers file, and update all internal imports and usage in the app, blueprint, and testing modules to use the new name as an alias.
* **Real Trajectory**: The agent starts by searching for the definition of 'send_from_directory' in 'helpers.py'. It identifies all dependent files (app.py, blueprints.py, test_helpers.py) that import this function. It then renames the function in 'helpers.py', which temporarily breaks all dependent imports. The agent systematically navigates to each dependent file, updates the import statements to use 'send_from_directory_helper as send_from_directory' to preserve external API compatibility, and verifies each change with structural checks.
* **Real Answer**: The core function is renamed in the source, all internal cross-file dependencies are updated with the appropriate aliasing logic, and the structural integrity of the project's imports is restored.
* **Why this demonstrates the capability**: This case tests stateful multi-file reasoning because the agent must remember which files it 'broke' with the first edit and ensure the trajectory doesn't end before every dependent callsite is tracked and updated. It requires a clear understanding of the project's import graph and the ability to maintain the refactoring objective spite of intermediate local errors.
---
**[Case 2]**
* **Initial Environment**: A large web crawling framework repository (similar to Scrapy) with utility modules for data decompression and multiple spider implementations that call these utilities.
* **Real Question**: Encapsulate the raw parameters currently passed to the 'gunzip' function (data and max_size) into a new class called 'GunzipParams'. Update the 'gunzip' function signature and all references in the spider and middleware modules to instantiate and pass this new object.
* **Real Trajectory**: The agent identifies the 'gunzip' function in 'utils/gz.py' and its call-sites in 'spiders/sitemap.py' and 'downloadermiddlewares/httpcompression.py'. It defines the 'GunzipParams' class in 'gz.py' and modifies the 'gunzip' signature. It then modifies the 'SitemapSpider' and 'HttpCompressionMiddleware' to create instances of 'GunzipParams' before calling the function. Finally, it updates the unit tests to match the new object-oriented interface.
* **Real Answer**: A new parameter class is implemented, the utility function is adapted, and all architectural boundaries (spiders, middleware, tests) are refactored to use the new encapsulated data structure.
* **Why this demonstrates the capability**: This demonstrates compositional refactoring which is harder than isolated bug fixing. The agent must orchestrate a coordinated change across the data access layer (utils), the business logic layer (spiders), and the networking layer (middleware), tracking its progress across multiple files where a single missing update would invalidate the architectural change.

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
