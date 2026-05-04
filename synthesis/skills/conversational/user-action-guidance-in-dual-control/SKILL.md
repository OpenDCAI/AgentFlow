---
name: user-action-guidance-in-dual-control
description: Use this skill when the world can only be changed by both the agent and the user together, so the agent has to guide the user instead of acting alone. Trigger it in support or troubleshooting settings where the user must do something on their side while the assistant does something on its side. Everyday examples include: 'toggle a device setting while I check the account', 'follow these steps on your phone and tell me what changed', 'I can reset the service but you need to reconnect', and 'I need you to do one action before I can finish the fix.'
---

# Skill: user-action-guidance-in-dual-control

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to solve tasks in a shared environment where both the assistant and the user can act, requiring the assistant to decide what it should do itself, what the user should do, and how to coordinate both action streams clearly.
* **Dimension Hierarchy**: Conversational Effectiveness->Task-oriented Dialogue Control->user-action-guidance-in-dual-control

### Real Case
**[Case 1]**
* **Initial Environment**: A telecom support assistant can inspect network state through its own tools, while the user simulator can also perform device-side actions such as toggling airplane mode. The world state is shared, but each side sees and controls different parts of it.
* **Real Question**: My mobile data is extremely slow. I want to fix it and get excellent internet speed on my phone.
* **Real Trajectory**: 1. Inspect account and network-side state through agent tools. 2. Infer whether the next best move is agent-side or user-side. 3. Tell the user exactly which device action to perform and in what order, while avoiding impossible or redundant instructions. 4. Re-check the shared state after the user’s action and continue until the issue is resolved or escalated.
* **Real Answer**: A coordinated troubleshooting dialogue that combines agent-side checks with precise user-side instructions such as device-state resets only when warranted by the shared state.
* **Why this demonstrates the capability**: The assistant cannot solve the problem by tool use alone because the user has agency over part of the environment. Success depends on decomposing responsibility correctly and communicating the user’s role clearly enough that the shared world transitions in the intended direction.

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
