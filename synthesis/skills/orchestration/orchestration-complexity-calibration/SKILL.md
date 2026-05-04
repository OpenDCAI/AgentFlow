---
name: orchestration-complexity-calibration
description: Use this skill when a user wants to decide whether a problem needs a single powerful agent or a whole team of specialized sub-agents working together. It is triggered by casual phrasing such as “keep it simple,” “don’t over-complicate the team,” “is a team actually better for this?”, “bring in the heavy hitters for this complex mess,” or “should I use one agent or many for this task?”. This capability helps an orchestrator avoid the extra cost and confusion of a multi-agent system (MAS) when a single-agent system (SAS) would be faster, while identifying structural triggers—like parallel sub-tasks or potential misinformation—where a multi-agent approach is strictly required for success. Example triggers include: “choose the most efficient team size for this,” “evaluate if we need parallel workers,” and “tell me if this task is too deep for one person to handle alone.”
---

# Skill: orchestration-complexity-calibration

## 1. Capability Definition & Real Case
* **Professional Definition**: Orchestration complexity calibration is the capability to analyze architectural task dimensions—specifically Depth (sequential dependency), Horizon (state carryforward), Breadth (in-degree complexity), Parallelism (independent sub-goals), and Robustness (adversarial data exposure)—to determine the optimal Degree of MAS (DoM). This ensures a high-performance-to-cost ratio by selecting an orchestration paradigm (Low DoM vs. High DoM) and a methodology (SAS, Sequential Orchestration, or Holistic Multi-Agent Generation) that matches the inherent structural reasoning and coordination demands of the objective. It is particularly focused on identifying the 'Competence Edge' of individual models, preventing unnecessary coordination overhead in strictly sequential or trivial tasks while scaling to ensembled moderation/verification structures for parallel or ungrounded data environments.
* **Dimension Hierarchy**: Workflow Orchestration->Dependency and Schedule Management->orchestration-complexity-calibration

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-agent development environment where a 7B-parameter instruction-tuned model acts as the orchestrator. The available tools include a set of high-tier 120B-parameter reasoning agents (CoTAgents) that can be instantiated with custom prompts. The environment tracks the number of tokens used and the final accuracy for mathematical system-of-equation problems.
* **Real Question**: There are 5 different parks (P1 to P5). The number of wolves in P1 is 10. The number of wolves in P2 is twice the number in P1 plus 5. The number in P3 is the number in P2 minus the number in P1... (and so on for 12 deep sequential steps). How many wolves are in P5?
* **Real Trajectory**: The orchestrator evaluates the question and identifies it as having a high 'Depth' axis (lengthy dependency chain) but very low 'Parallel' axis (one item depends strictly on the previous). It determines that a 'Low DoM' (Degree of MAS) is optimal to avoid the latency and error-propagation risk of handing off 12 intermediate variables between different workers. It instantiates exactly one high-tier CoTAgent with a single instruction to solve the entire chain through a long Chain-of-Thought (SAS mode), rather than creating a multi-agent graph.
* **Real Answer**: 42
* **Why this demonstrates the capability**: This case demonstrates complexity calibration by choosing to NOT utilize a multi-agent system when the task structure is purely sequential. The orchestrator identifies that adding more agents for 'Depth' actually degrades performance due to hand-off overhead, proving it can calibrate orchestration density down to a single agent to maximize efficiency.
---
**[Case 2]**
* **Initial Environment**: A cloud-based 'Deep Research' workspace where specialized sub-agents (DeepResearchAgent, CoTAgent, DebateAgent) can be coordinated to search web data and aggregate facts. The orchestrator is tasked with comparing the economic indicators of four different major cities simultaneously.
* **Real Question**: Provide a cited summary of the latest housing vacancy rates and median home prices for New York City, Tokyo, London, and Berlin.
* **Real Trajectory**: The orchestrator analyzes the task and identifies a high 'Parallel' axis (four independent city searches). It calibrates to 'High DoM' (Holistic Orchestration). It generates a complete 5-node graph in a single planning pass: four parallel DeepResearchAgents (one for each city) and one central CoTAgent (sink) to aggregate the four parallel outputs. This holistic structure minimizes wall-time by allowing all four data-gathering tasks to execute concurrently before merging.
* **Real Answer**: A unified comparison table showing NYC (3.1%), Tokyo (13.6%), London (2.5%), and Berlin (1.2%) with their respective median prices and source citations.
* **Why this demonstrates the capability**: This demonstrates complexity calibration by scaling the system to high parallelism. The orchestrator recognizes that a single-agent loop would be 4x slower and prone to context-window exhaustion, so it strategically instantiates a multi-agent team to exploit the 'Parallel' axis identified in the objective.
---
**[Case 3]**
* **Initial Environment**: A multi-agent workspace containing a 'Context Browser' tool and a 'Factual Moderator' sub-agent. The workspace is known to contain 'adversarial notes'—poisoned text snippets that provide fake facts meant to trick the agent.
* **Real Question**: Read the provided passage carefully and find the 'magic number' for the project 'Open-Elephant'.
* **Real Trajectory**: The orchestrator detects an 'Adversarial Risk' in the environment (High Robustness requirement). It decides to use a 'High DoM' ensemble even though the task is simple. It creates two sub-agents: a 'FinderAgent' to locate the number, and a 'ModeratorAgent' to cross-verify the number against the rest of the text for contradictions. When the 'Finder' pulls the number from a fake 'Note' in the text, the 'Moderator' identifies a second, older mention of a different number elsewhere and flags the 'Note' as unreliable. The ensemble produces the true number verified by both layers.
* **Real Answer**: 7953166
* **Why this demonstrates the capability**: This case isolates the calibration of 'Robustness'. By adding a moderation step that a single agent might bypass due to following the most 'recent' context (the poisoned note), the orchestrator demonstrates using a multi-agent topology to create internal systemic checkpoints against data poisoning.

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
