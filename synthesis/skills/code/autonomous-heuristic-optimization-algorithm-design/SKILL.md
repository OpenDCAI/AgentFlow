---
name: autonomous-heuristic-optimization-algorithm-design
description: Use this skill when the user wants to generate or refine code for hard optimization problems where exact answers are impossible, like delivery routing, scheduling, or resource planning. Trigger it for requests like 'solve this routing puzzle', 'optimize my delivery paths', 'make a scheduler for factory orders', or 'help me get a higher score on this algorithmic challenge'. It is specifically meant for iterative refinement tasks where you must use test feedback to continuously improve a program's numerical score over a long period.
---

# Skill: autonomous-heuristic-optimization-algorithm-design

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to autonomously design, implement, and iteratively optimize heuristic and meta-heuristic algorithms for NP-hard combinatorial optimization problems. This involves translating high-level mathematical objectives into executable code, utilizing long-horizon feedback loops from scorers and visualizers to refine strategies (e.g., Simulated Annealing, Beam Search, or local search neighborhoods), and managing the tradeoff between solution quality and execution time limits to maximize performance metrics.
* **Dimension Hierarchy**: Competitive Algorithm Engineering->Heuristic and Meta-Heuristic Optimization->autonomous-heuristic-optimization-algorithm-design

### Real Case
**[Case 1]**
* **Initial Environment**: A software workspace contains a dataset of 1000 food delivery requests, each defined by a restaurant (pickup) and a customer (delivery) coordinate on a 2D grid. The environment includes a scorer that calculates travel time based on Manhattan distance.
* **Real Question**: Develop a program that selects exactly 50 requests from the 1000 provided and outputs a depot-to-depot tour that minimizes total travel time, ensuring every pickup occurs before its corresponding delivery.
* **Real Trajectory**: Establish a baseline by selecting 50 random requests and sorting them using a simple greedy nearest-neighbor approach. Observe the initial score and identify that the route is messy with many crossing paths. Implement a Simulated Annealing algorithm that uses 'request-swapping' and '2-opt path reversals' as neighborhood moves. Execute the SA loop multiple times, monitoring the score progression from 50,000 to under 15,000, and finalize the implementation by tuning the temperature to fit within the 2-second CPU limit.
* **Real Answer**: A robust optimization script employing Simulated Annealing with optimized 2-opt moves that returns a valid sequence of 50 pickups and deliveries with a competitive total distance.
* **Why this demonstrates the capability**: This case demonstrates the skill because the agent must move beyond getting a 'working' solution to achieving a 'high-scoring' one. It requires the iterative use of meta-heuristics (SA) and neighborhood design to solve a complex routing problem where the true optimum is unknown.
---
**[Case 2]**
* **Initial Environment**: A repository contains a logic network represented as a set of points and requirements for geometric partitioning. A scorer is provided to calculate the reward based on the number of points captured minus the cost of the boundary rectangles.
* **Real Question**: Implement an algorithm to partition the boolean network using rectangles to maximize the total point-capture reward while adhering to the specified rectangle count limits.
* **Real Trajectory**: Analyze the point density map to identify high-reward clusters. Implement a greedy seeding approach where each point cluster gets a starting rectangle. Refine this by implementing a recursive coordinate bisection method to better align boundaries. After observing poor results on outlier points, implement a local search that attempts to merge and shrink rectangles to reduce the 'boundary cost' penalty. Use the resulting scores to choose the best-performing merge strategy.
* **Real Answer**: An efficient geometric optimizer utilizing recursive bisection and refined local search to produce a high-reward point-capture layout.
* **Why this demonstrates the capability**: The agent must handle symbolic-geometric reasoning and use score feedback to choose between different refinement strategies (bisection vs local search), mirroring professional algorithm engineering workflows.
---
**[Case 3]**
* **Initial Environment**: A hardware scheduling environment includes a Control Data Flow Graph (CDFG) and a mapping of resource types (adders, multipliers) with fixed counts. A judge script evaluates the total clock cycles required for execution.
* **Real Question**: Optimize the operation schedule for the CDFG to minimize execution latency while strictly respecting all data dependencies and the hardware resource caps.
* **Real Trajectory**: Parse the CDFG to build a dependency DAG and implement a basic list-scheduling heuristic using 'As Late As Possible' (ALAP) priorities. Identify that multiplier contention is the primary bottleneck after checking the resource utilization logs. Refine the priority function to weight operations by their resource-type scarcity and re-run the solver. Observe a 15% cycle count reduction and finalize the schedule.
* **Real Answer**: A hardware-accurate scheduler that allocates operations to cycles, minimizing latency within strict resource limits.
* **Why this demonstrates the capability**: Success requires the agent to interpret resource-constraint logs and iteratively improve its heuristic priority function to achieve lower latency, demonstrating the objective-driven nature of the skill.

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
