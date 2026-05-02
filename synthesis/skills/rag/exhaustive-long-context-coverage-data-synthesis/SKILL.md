---
name: exhaustive-long-context-coverage-data-synthesis
description: Use this skill when the user wants questions that 'need reading everything', 'leave no file behind', 'spread the clues across many documents', or 'test whether the model skips a document'. Trigger it for large multi-document bundles where the answer depends on broad coverage instead of one easy snippet.
---

# Skill: Exhaustive Long-Context Coverage

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to preserve document-level coverage over very long multi-document contexts, so that no required document is silently ignored and no answer is produced from a shortcut subset. The core challenge is coverage discipline under extended contexts where evidence is dispersed and many documents are semantically similar.
* **Dimension Hierarchy**: Multi-Source Evidence Composition->Long-Context Coverage->Exhaustive Long-Context Coverage

### Real Case
**[Case 1]**
* **Initial Environment**: A long bounded bundle of company reports from the same domain. Each company’s non-current-assets figure is stored in its own document, and the answer requires scanning all candidate companies before comparing them.
* **Real Question**: Which company has the highest non-current assets?
* **Real Answer**: HARTE HANKS
* **Why this demonstrates the capability**: This case punishes the agent if it reads only a convenient subset of documents. The answer is only trustworthy after coverage across all comparison candidates. The capability is therefore exhaustive long-context accounting, not simple local retrieval.
---
**[Case 2]**
* **Initial Environment**: A long bounded multi-report context where each company’s accounts-payable figure appears in a separate document. The task is to group companies into high, medium, and low payable buckets.
* **Real Question**: Categorize the companies above by 'Accounts Payable' into the following groups: high payable (x>100,000), medium payable (1,000<x<100,000), and low payable (x<1,000).
* **Real Answer**: {"high payable": ["BIOETHICS"], "medium payable": ["CLEARONE"], "low payable": ["Dominari Holdings"]}
* **Why this demonstrates the capability**: The agent must maintain broad coverage over several documents and preserve one extracted fact per document before grouping. Skipping even one document corrupts the final clustering. This is exactly the coverage pressure that long-context QA is meant to surface.
---
**[Case 3]**
* **Initial Environment**: A long bundle of same-domain documents in which only one document contains the target fact and the others are semantically similar. The context length is large enough that naive scanning or shortcutting is risky.
* **Real Question**: What is the Basic Earnings Per Share for Dominari Holdings Inc.?
* **Real Answer**: $(0.91)
* **Why this demonstrates the capability**: Although only one document contains the answer, the surrounding documents create long-context pressure by sharing domain vocabulary and structure. The agent must localize the right document without losing coverage discipline over the broader bundle. This case captures the foundational localization aspect of long-context reasoning.

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
