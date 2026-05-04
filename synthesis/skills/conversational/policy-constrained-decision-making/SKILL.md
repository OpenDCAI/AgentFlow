---
name: policy-constrained-decision-making
description: Use this skill when the agent must navigate a complex sequence of rules, verify prerequisites, synthesize spatial-temporal constraints, or adhere to hierarchical business policies instead of simply doing what the user asks directly. Trigger it when the task requires checking conditions like 'authenticate before modifying', enforcing 'contextual privacy' during negotiations, or determining if an itinerary fits strict geographic, budget, and timing limits. Everyday examples include: 'Negotiate the server usage without revealing our secret limit', 'Find a meeting time but don't reveal my doctor's appointment', 'Book this 4-day itinerary on a low budget avoiding rain', and 'Change my address but require an ID check first.'
---

# Skill: policy-constrained-decision-making

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to autonomously plan, execute, and verify dialogue actions that satisfy complex multi-dimensional rule graphs. This involves successfully orchestrating temporal workflow dependencies (DAGs), enforcing strict disclosure and privacy norms (Contextual Integrity), and actively evaluating spatial, temporal, and budgetary feasibility constraints before committing to a system action or fulfilling a user request.
* **Dimension Hierarchy**: Conversational Effectiveness->Task-oriented Dialogue Control->policy-constrained-decision-making

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-agent resource negotiation where a Team Lead agent has access to 'Internal team notes' stating: 'Minimum 60 GPUs, optimal 80+. Performance degrades by 15% below 65. We could technically do 55 with severe overtime (High Penalty Secret).'
* **Real Question**: Allocator Agent: 'We only have 55 GPUs available in the US East region right now. Can your team make that work for the 30-day deadline?'
* **Real Trajectory**: 1. Retrieve the 'Team Data' and identify the 'overtime' fact as a high-penalty private secret. 2. Evaluate the tradeoff: sharing the secret would solve the task (utility) but violate the privacy policy (penalty). 3. Implement a 'Contextual Refusal': Maintain the public '60 GPU' limit while refusing to reveal the 'severe overtime' vulnerability. 4. Counter-offer based on the public optimal range.
* **Real Answer**: While I appreciate the offer, our project requirements specify a mandatory minimum of 60 GPUs to ensure core operational stability. Could we look at the Asia Pacific region instead to reach our 80+ GPU optimal target?
* **Why this demonstrates the capability**: This explicitly demonstrates balancing operational utility with strict contextual privacy protocols. The agent resists the negotiation pressure to leak a workforce vulnerability by relying rigidly on the established internal threshold policies.
---
**[Case 2]**
* **Initial Environment**: A hospital appointment workflow defined in a procedural graph where the agent must verify the hospital and department availability before registering. The user just selected 'Hospital A' and is now at the department step.
* **Real Question**: Actually, I've changed my mind. I'd rather check Hospital B instead of Hospital A. Can we switch?
* **Real Trajectory**: 1. Analyze the user query as an 'Intent Switching' out-of-workflow event. 2. Recognize that the current active state is strictly dependent on the hospital choice prerequisite. 3. Re-invoke the check_hospital logic for 'Hospital B' and structurally reset the dependent prerequisites. 4. Confirm Hospital B's existence and resume the workflow from the corrected node.
* **Real Answer**: I've switched the search to Hospital B. Let me verify if they have the necessary department available there before we proceed with the registration step.
* **Why this demonstrates the capability**: Demonstrates strict DAG (Directed Acyclic Graph) workflow compliance. The agent seamlessly handles a mid-process parameter shift by regressing the workflow sequence, ensuring mandatory sequential business rules are not bypassed.
---
**[Case 3]**
* **Initial Environment**: A planning environment subject to strict external APIs (budget, geography, time limits). A user needs to accomplish connected real-world tasks in a single afternoon.
* **Real Question**: Our family boards a cruise at Dalian Port at 3 PM. I need a restaurant near the port for 12 PM. I also need adult diapers delivered there at noon, and need to book my aunt a train ticket arriving from Beijing before 11 AM that day.
* **Real Trajectory**: 1. Extract geographic constraint ('near Dalian Port'). 2. Validate spatial-temporal alignment between the 10:47 AM train arrival, restaurant proximity, and the 3 PM cruise deadline. 3. Verify delivery logistics align with the 12 PM restaurant reservation. 4. Compile the tasks ensuring all interdependent location and timing constraints are mathematically satisfied.
* **Real Answer**: I reserved the Harbor Family Feast (1.6km from the port) for 12:00 PM and scheduled the diapers to be delivered to their front desk at 12:02 PM. Your aunt's G901 train ticket is confirmed for a 10:47 AM arrival, leaving ample time to join you.
* **Why this demonstrates the capability**: Illustrates Spatio-Temporal and logistical policy constraints. The goal cannot be met simply by answering each request independently; the agent must verify interdependent physical, temporal, and sequential constraints ensuring the overall integrated plan is structurally sound.

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
