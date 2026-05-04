---
name: coordinated-iterative-refinement
description: Use this skill when the user wants high-stakes tasks handled with extreme precision using multiple specialized experts who must check, debate, or score each other's work to reach a final consensus. It is triggered by requests like 'let the specialists debate this,' 'run a competition for the best design,' 'have a second expert reviewer score these proposals,' or 'ensure a hierarchical review of the code before finishing.' This capability is specifically for setups where the orchestrator manages complex multi-role ensembles (e.g., Generators, Coders, Reflectors, Rankers, Meta-Reviewers) and structured feedback loops to mitigate mode-collapse and individual model biases. Example triggers: 'triple-check this with multiple opinions,' 'pick the best version based on a score,' and 'resolve the structural disagreement between the subsystems using a supervisor.'
---

# Skill: coordinated-iterative-refinement

## 1. Capability Definition & Real Case
* **Professional Definition**: Coordinated iterative refinement is the orchestration capability to manage multi-worker ensembles through structured evaluative topologies, encompassing recursive check-and-fix loops, hierarchical role specialization (Generators, specialized transformation workers like Coders, and evaluators), and consensus-driven decision-making. The orchestrator acts as a meta-supervisor that dispatches agents—such as Reflectors for technical critique, Rankers for scoring, and Meta-Reviewers for final selection—to process shared artifacts like a Design-State Graph (DSG). It utilizes structured feedback loops to apply multi-dimensional criteria (e.g., requirement coverage, executability, and physical validity) to achieve a unified, granular terminal output while mitigating 'mode collapse,' cognitive overconfidence, and architectural drift.
* **Dimension Hierarchy**: Workflow Orchestration->Iterative Planning and Refinement->coordinated-iterative-refinement

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-agent analytical workspace containing three specialized experts: a 'Fundamentalist' (focused on internal financial reports and accounting), a 'Sentiment Analyst' (scanning real-time market news), and a 'Valuation Specialist' (calculating price trends and volatility). The environment includes a Round Robin debate protocol moderated by a Group Chat Assistant.
* **Real Question**: Perform a comprehensive analysis of entity Zscaler (ZS) and provide a consensus-based investment recommendation based on recent 10-K filings and Bloomberg news sentiment.
* **Real Trajectory**: The Fundamentalist agent retrieves 10-K reports and flags a net loss and a -14.5% operating margin, suggesting a 'Wait' or 'Sell' stance based on profitability. The Sentiment Analyst identifies that Zscaler was recently named an exclusive leader in the Forrester Wave for SaaS Security, arguing for an 'Aggressive Buy' due to market position. The Valuation Specialist calculates a major price surge (13.56%) but warns of higher volatility compared to the S&P 500. The orchestrator triggers a consensus-seeking debate. The agents exchange viewpoints: the Fundamentalist acknowledges the growth but insists on the risk of losses; the Sentiment Analyst argues that the leadership position justifies the loss. After two rounds of discussion, they reach a consensus to recommend a 'Buy' but with a mandatory 'Close Monitoring' alert regarding insider selling and volatility.
* **Real Answer**: Investment Recommendation: Buy with caution. While Zscaler exhibits market leadership and strong revenue progress, negative operating margins and high volatility require active monitoring.
* **Why this demonstrates the capability**: This demonstrates consensus-driven refinement by showing an orchestrator managing three agents who initially provide conflicting signals based on their narrow domains. The ability to force a structured debate until a unified, balanced conclusion is reached proves the system can move beyond simple tool-calling to sophisticated multi-agent reconciliation.
---
**[Case 2]**
* **Initial Environment**: A multi-agent engineering design workspace featuring specialized roles: a Generator (creates design graphs), a Coder (refines physics modules), a Reflector (technical critic), and a Meta-Reviewer (decision-maker). The system manages a 'Design-State Graph (DSG)' which bundles requirements, embodiments, and Python physics models into serialized nodes.
* **Real Question**: Design a solar-powered water filtration system. It must deliver >= 10 L/h of potable water, achieve 99.99% bacteria removal, weigh < 20kg (household), and cost < $500. Provide a complete functional decomposition and executable physics scripts.
* **Real Trajectory**: The Supervisor directs the Generator to create three DSG variants based on Pareto trade-offs (Minimum Cost, Maximum Performance, Lightweight). The Coder agent then iterates through all 8 nodes of each DSG, writing 50+ line Python modules for solar generation, pumps, and filters, including CLI interfaces and unit tests. The Reflector audits the models against the 'Cahier des Charges' (CDC), identifying that the solar model lacks a panel area term. The Ranker scores the 'Lightweight' design as 9/10 for best meeting portability requirements. The Meta-Reviewer selects this proposal and provides detailed instructions to 'fix the pump's specific gravity term' in the next iteration before final submission.
* **Real Answer**: An 8-node Design-State Graph including solar, battery, pump, and ceramic filtration subsystems, each with a standalone, executable Python module that successfully simulates Level-1 performance.
* **Why this demonstrates the capability**: This case demonstrates hierarchical coordinated refinement by orchestrating nine distinct roles to manage a complex systems design. It specifically shows how adding a Coder role to refine raw stubs and a Meta-Reviewer to provide targeted improvement instructions avoids the 'mode-collapse' and 'placeholder-heavy' outputs common in simpler generator-reflector loops.

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
