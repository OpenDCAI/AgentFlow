---
name: multi-document integration
description: Trigger this skill when the answer is logically fragmented across physically non-contiguous spans or when a local entity (like a function or a paragraph) requires context from a larger structure (like a repository, class, or multi-volume report). It is used for natural language requests like 'connect the fragments from this long report', 'stitch together clues from the repository', 'summarize this function using the rest of the class for context', 'check if a second search is needed for the missing repository details', or 'compare files to find similarities'. This skill ensures the agent can proactively identify and retrieve 'anchor' documents—such as skeletons, table of contents, or related code chunks—to perform high-fidelity synthesis.
---

# Skill: multi-document integration

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform token-level extraction and relational assembly where required components are logically separated across multiple documents, distant structural segments, or hierarchical layers. This includes the identification of 'structural anchors' (e.g., class skeletons, interface definitions, or section indices) to bound search spaces, and proactive evidence-gap probing to identify when a target entity's immediate context is insufficient for grounded synthesis. The agent must synthesize information by integrating local details with broader architectural or topical frameworks retrieved from a bounded repository or knowledge pool.
* **Dimension Hierarchy**: Multi-Source Evidence Composition->Cross-Document Synthesis->multi-document integration

### Real Case
**[Case 1]**
* **Initial Environment**: A RAG context containing a 150-page SEC 10-K filing for a technology firm. 'Item 1' outlines international revenue growth; 'Item 1A' outlines regulatory hurdles in European markets.
* **Real Question**: Based on the 10-K, how do the specific European regulatory risks listed in Item 1A qualify the international revenue projections in Item 1?
* **Real Trajectory**: The agent fragments the intent, finding the '9% growth' projection in Item 1 and the 'GDPR penalty' in Item 1A. It integrates these distant, disjoint segments to formalize the dependency.
* **Real Answer**: The projected 9% international revenue growth outlined in Item 1 is qualified by the potential for high fines under GDPR in European markets.
* **Why this demonstrates the capability**: This illustrates the ability to resolve discontinuous reference spans anchored by a document's formal structure, bringing together facts across 40 pages to satisfy a qualified extraction request.
---
**[Case 2]**
* **Initial Environment**: A professional Python codebase for a complex project (e.g., ClassEval). The environment contains a specific method `get_order_status` within a 500-line class, but its summary requires understanding the class-level state and other method signatures.
* **Real Question**: Generate a concise 2-sentence summary of what the `get_order_status` method does in its class context.
* **Real Trajectory**: The agent retrieves the target method code but identifies it is 'context-poor' due to internal variable references. It then retrieves the 'Class Skeleton' (header and method signatures) to identify that the class manages an asynchronous database. It integrates the local method logic with the class-level 'asynchronous' state found in the skeleton.
* **Real Answer**: The `get_order_status` method queries the internal order registry to return the current lifecycle stage of a transaction. Because it operates within an asynchronous session manager, it ensures thread-safe access to the shared database state.
* **Why this demonstrates the capability**: This demonstrates 'Structural Skeleton Integration.' The agent avoids 'Omission Failure' by recognizing that the local snippet lacks sufficient context and proactively integrates a structural anchor (the class skeleton) to refine the synthesis.
---
**[Case 3]**
* **Initial Environment**: A large-scale repository (e.g., Apache Airflow) where a target function `execute` in a BashOperator file interacts with global constants and utility functions defined in three separate files.
* **Real Question**: Explain how the `execute` method in the BashOperator handles temporary directory cleanup.
* **Real Trajectory**: The agent extracts the `execute` code and notes it calls `TemporaryDirectory()`. It identifies that the cleanup behavior isn't in the local file, so it executes a RAG search across the repository. It retrieves 'Top-K' related chunks (chunk 5 from `utils.py` and chunk 12 from `constants.py`) and integrates these external fragments to explain the internal cleanup logic.
* **Real Answer**: The `execute` method utilizes the `TemporaryDirectory` utility to create a sandboxed execution environment. It relies on the global `CLEAN_UP_LEVEL` constant to determine if the folder is deleted immediately or persisted for debugging, as defined in the repository's core utility configurations.
* **Why this demonstrates the capability**: This demonstrates 'Repository-Level Gap Probing.' The agent identifies a functional dependency on external 'chunks' and iteratively gathers them to build a comprehensive, multi-file explanation that a single-document search would fail to ground.

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
