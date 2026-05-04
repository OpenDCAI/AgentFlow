---
name: disruption-aware-reactive-replanning
description: Use this skill when the user wants to test how an agent handles unexpected changes, environmental disruptions, or live telemetry pushes in the middle of a task. Trigger it for natural language requests like 'what if the road is closed?', 'make sure you see the latest live changes,' 'deal with a flight delay,' 'don't use old data if an event is pushed,' or 'fix the schedule if a machine breaks.' Example triggers: 'add a surprise delay to the task,' 'keep your context fresh with live updates mid-task,' and 'make the agent pivot when the environment pushes an alert.'
---

# Skill: disruption-aware-reactive-replanning

## 1. Capability Definition & Real Case
* **Professional Definition**: Disruption-aware reactive replanning (encompassing event-driven context synchronization) is the orchestration capability to dynamically modify an active execution trace in response to exogenous environmental shifts, pushed telemetry streams, or resource unavailability that occurs after a plan has been initiated. Instead of relying solely on periodic static polling, the orchestrator incorporates live asynchronous events (e.g., a machine failure, a topological blockage, or a critical payload update) to immediately invalidate outdated assumptions in its dependency graph (DAG). The agent then performs a surgical state-update or re-routes the workflow to restore progress while preserving the unaffected portions of its global strategy.
* **Dimension Hierarchy**: Trustworthy Execution->Verification and Resilience->disruption-aware-reactive-replanning

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-vehicle urban transport environment is active with three vehicles and five passengers. The system has already matched passengers to vehicles and established pick-up routes. A road-closure map service is available as a background monitor pushing live events.
* **Real Question**: A major bridge on the route to the airport has just been closed for emergency repairs. Update the ride-sharing schedule for all affected vehicles to ensure no passenger misses their flight, prioritizing the earliest departures.
* **Real Trajectory**: The orchestrator receives the disruption alert mid-task and queries current GPS coordinates. Identifying that Vehicle 1 is 5 minutes from the bridge, it halts the 'Navigate' action, updates the DAG with a new 20-minute detour, and offloads Passenger 3 to Vehicle 2 (which is unaffected) to prevent cascading delays.
* **Real Answer**: Ride-share schedule updated: Vehicle 1 rerouted via detour; Passenger 3 transferred to Vehicle 2 to preserve deadline.
* **Why this demonstrates the capability**: Demonstrates reactive replanning because the disruption happened mid-execution, invalidating a previously optimized route. The agent performed state-aware filtering to selectively re-balance load rather than restarting from scratch.
---
**[Case 2]**
* **Initial Environment**: A production environment (Job-Shop) contains 3 machines and 3 active jobs. Job 1 is currently 50% complete on Machine A. Machines provide real-time status telemetry push-alerts.
* **Real Question**: Machine A has experienced a mechanical failure and will be offline for the next 2 hours. Reschedule the remaining operations to minimize the final completion time (makespan), ensuring no job steps are skipped.
* **Real Trajectory**: The agent observes the pushed 'Machine Breakdown' event at time T=4. It marks Machine A as blocked, identifies that Job 1 Step 2 can be moved to Machine B, and performs a 'Swap-and-Insert' operation in the workflow DAG to maintain overall operational precedence.
* **Real Answer**: Schedule revised: Job 1 Step 2 shifted to Machine B, resuming operations immediately to minimize makespan impact.
* **Why this demonstrates the capability**: Highlights the resilience aspect of workflow orchestration. The unexpected event forces a cascading logic change requiring alternatives to be evaluated dynamically to avert total systemic stall.
---
**[Case 3]**
* **Initial Environment**: A large-scale cloud resource management environment where 'Resource Watchers' push immediate asynchronous changes (deltas) into the agent's vector index rather than relying on hourly polling.
* **Real Question**: What is the current headroom for the guaranteed-throughput slice? If it's below 10Mbps, increase it immediately.
* **Real Trajectory**: While processing, the system detects a resource fluctuation via the Push Path, updating 'headroom' to 8Mbps. The orchestrator receives this up-to-the-second snapshot, recognizing the shortage mid-task. It executes a 'Resource Update' tool to modify the blueprint to 15Mbps, parsing the success based on the new watcher state.
* **Real Answer**: The live headroom alert showed 8Mbps due to a recent spike. I have increased throughput to 15Mbps to restore the safety threshold.
* **Why this demonstrates the capability**: This illustrates the event-driven synchronization dimension of replanning. The orchestrator reacted strictly to a live push-update mid-session, surgically updating its execution trajectory. Failing to react to the disruption would have resulted in using stale polling data.

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
