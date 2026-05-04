---
name: combinatorial-search-optimization-planning
description: Use this when the user needs to solve complex logic puzzles, evaluate solvability, find the best route through millions of points, or optimize resource allocation in NP-hard problems with irregular structures. Trigger it for requests like 'solve this massive 10-million node route', 'find a Steiner tree for these points', 'solve this asymmetric delivery problem where road A-to-B is different than B-to-A', or 'solve a logic challenge designed to break simple guessing algorithms'.
---

# Skill: combinatorial-search-optimization-planning

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform systematic exploration, lookahead verification, and optimization over discrete, high-dimensional state spaces—spanning both Euclidean and non-Euclidean structures—to identify optimal configurations in NP-hard problems. This capability specifically addresses extreme-scale scenarios (up to 10M+ nodes) and structurally irregular problem distributions (e.g., asymmetric costs or SAT-induced graphs) that defeat simple local heuristics, requiring the agent to synthesize and evaluate sophisticated search algorithms like Variable Neighborhood Descent or Simulated Annealing.
* **Dimension Hierarchy**: Closed-World Symbolic Planning->Combinatorial and Algorithmic Search->combinatorial-search-optimization-planning

### Real Case
**[Case 1]**
* **Initial Environment**: A non-Euclidean graph environment representing a stacker-crane operation in a warehouse. The distance from Point A to Point B is not equal to Point B to Point A due to mechanical transit rules, and the triangle inequality is not guaranteed to hold.
* **Real Question**: Solve the Asymmetric Traveling Salesman Problem (ATSP) for the provided warehouse node matrix to minimize the total crane movement time, visiting 500 distinct storage bins exactly once.
* **Real Trajectory**: 1. [Structural Analysis]: Detects that the distance matrix is asymmetric and violates metric assumptions. 2. [Algorithm Selection]: Rejects standard Euclidean 2-OPT because cross-swapping edges may result in massive cost increases in a non-metric space. 3. [Iterated Search]: Implements a specialized Lin-Kernighan-Helsgaun (LKH) variant tailored for asymmetric paths. 4. [Optimization]: Performs 1,000 trials of local refinement, iteratively updating the best-known tour through sub-tour patch-ups until a global optimum is reached.
* **Real Answer**: A specific sequence of node indices representing the optimal asymmetric tour, with a total movement time of 1,245 seconds.
* **Why this demonstrates the capability**: This demonstrates combinatorial optimization in non-metric spaces. The agent must recognize that the 'asymmetric' nature of the environment limits the effectiveness of common local search tools. By selecting an algorithm that accounts for directed edge costs, the agent proves it can plan around the structural irregularity of real-world industrial constraints.
---
**[Case 2]**
* **Initial Environment**: A large-scale graph with 10,000 terminal nodes. The objective is to connect all these points into a single tree with the minimum total edge weight, allowing the use of additional intermediate (Steiner) points to create shortcuts.
* **Real Question**: Compute the Minimum Steiner Tree for the provided VPC hypercube graph, identifying the optimal Steiner points to connect all mandated terminals.
* **Real Trajectory**: 1. [Global Mapping]: Identifies that the problem is an NP-hard Steiner Tree Problem (STP) on a non-Euclidean hypercube graph. 2. [Heuristic Selection]: Recognizes that simple MST-based heuristics will fail on the complex hypercube structure. 3. [Iterative Search]: Employs a hybrid Neural-Symbolic approach, using a GNN to predict potential Steiner points and then applying the Takahashi–Matsuyama algorithm to construct the tree. 4. [Refinement]: Performs a local 3-opt refinement to swap Steiner connections until the primal gap is minimized.
* **Real Answer**: A list of edges and coordinates for the Steiner points that form the most cost-effective spanning tree.
* **Why this demonstrates the capability**: The Steiner Tree Problem is a classic CO challenge where the agent must reason about adding *new* points to the state space to optimize the global goal. Handling hypercube graphs requires the agent to look past local proximity and understand non-Euclidean global connectivity, moving from simple spanning to complex structural optimization.
---
**[Case 3]**
* **Initial Environment**: A massive-scale graph environment containing 8,000,000 nodes derived from a SAT-reduction challenge. The goal is to find the largest possible set of nodes where no two nodes share an edge.
* **Real Question**: Find the Maximum Independent Set (MIS) for the provided 8M-node SAT-induced graph.
* **Real Trajectory**: 1. [Scale Reduction]: Identifies that the 8M node size will cause memory overflow for standard neural solvers. 2. [Kernelization]: Applies a Tomita-style kernelization to prune the graph, isolating the 'hard core' of the problem. 3. [Parallel Search]: Distributes the candidate search space across multiple local search explorers. 4. [Verification]: Iteratively checks each candidate node for conflicts against the current set and updates the best-found size until the time limit is reached.
* **Real Answer**: A set of node indices representing the maximum independent set found within the computational budget.
* **Why this demonstrates the capability**: This case tests extreme-scale combinatorial search. The agent must balance the 'curse of scale' (8 million nodes) with the 'structural difficulty' (SAT-reduction logic) by implementing a reduction strategy before attempting the final optimization.

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
