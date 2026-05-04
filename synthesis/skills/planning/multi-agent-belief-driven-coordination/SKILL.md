---
name: multi-agent-belief-driven-coordination
description: Use this when the user wants planning data for scenarios where an agent must track what other actors know, believe, or intend (Theory of Mind). Trigger it for requests like 'make tasks where the agent has to guess what its partner knows', 'solve a coordination problem with limited communication', 'plan a strategy that uncovers a deception or forms an alliance', or 'generate unexploitable strategies for competitive games with hidden info where you must exploit an opponent's blind spots.'
---

# Skill: multi-agent-belief-driven-coordination

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform multi-agent orchestration and strategic planning by maintaining recursive belief states (Theory of Mind) in decentralized, partially observable, or adversarial environments. This involves tracking hidden mental models, identifying false beliefs, using communication to synchronize cooperative teams, and synthesizing unexploitable (GTO) or deceptive negotiation strategies to navigate competitive, mixed-motive, or zero-sum environments.
* **Dimension Hierarchy**: Open-World Real-World Planning->Dynamic Interactive Environment Planning->multi-agent-belief-driven-coordination

### Real Case
**[Case 1]**
* **Initial Environment**: A cooperative team of three agents (Alpha, Bravo, Charlie) is in a multi-room facility. Alpha has a red and green wire-cutter, while others hold missing tools. A three-phase puzzle is located in Room 5, but its sequence is currently unknown to everyone until inspected natively.
* **Real Question**: Alpha is currently in Room 5 with Bomb 3. What should Alpha do to defuse the bomb if the sequence is Red-Green-Blue?
* **Real Trajectory**: Alpha inspects the puzzle confirming the sequence. Alpha recognizes possessing Red/Green tools yet lacking Blue. Alpha broadcasts a shared communication array: 'Bomb 3 in Room 5 is R-G-B; I will process initial phases, Charlie relocate to Room 5 addressing phase Blue.' Alpha applies Red, then Green.
* **Real Answer**: Action: Inspect -> Message: [Sequence Info/Delegation] -> Action: Apply Red -> Action: Apply Green.
* **Why this demonstrates the capability**: The agent must track its own physical capabilities symmetrically against distributed teammates realizing the terminal goal requires external intervention. It executes communication bridging 'belief synchronization' securely updating Charlie's mental model bypassing physical distance.
---
**[Case 2]**
* **Initial Environment**: Agent Alpha is in Room 0 having just neutralized a dynamic hazard. Agent Charlie is isolated in Room 6 and hasn't intersected Room 0 nor received textual status updates recently.
* **Real Question**: Does Player Charlie know that the hazard in Room 0 is neutralized? Based on Charlie's perspective, what is the most likely state of Room 0?
* **Real Trajectory**: The agent calculates Charlie lacks physical proximity and messaging updates regarding Room 0. Concludes Charlie holds a 'false belief' anticipating the hazard remains broadly active since no localized perceptive event updated their internal ledger.
* **Real Answer**: No, Charlie does not know it is neutralized; Charlie holds the false belief the hazard remains active.
* **Why this demonstrates the capability**: Extracts robust First-Order Theory of Mind differentiating universal ground truth from localized agent belief frameworks. This directly predicts teammate operational redundancy circumventing duplicated task attempts entirely.
---
**[Case 3]**
* **Initial Environment**: An adversarial multi-power game map. The agent shares a heavily fortified spatial border with a counterpart. Previously, they established a strong diplomatic non-aggression agreement. Current environment logs confirm the counterpart mobilized offensive units aggressively encroaching the agent's buffer zone.
* **Real Question**: Adjust your multi-agent negotiation strategy and spatial movements to address the counterpart's potential betrayal while sustaining alternative cooperative factions.
* **Real Trajectory**: 1. [Intent Inference]: Detects critical discrepancy pitting historical verbal promises against physical troop movements. 2. [Trust Update]: Immediately penalizes the counterpart's trust weight mapping to 'Hostile'. 3. [Negotiation]: Formulates secure messaging to a third-party faction proposing mutual defensive postures. 4. [Execution]: Abandons cooperative action structures substituting rigid defensive lines checking the adversarial advance.
* **Real Answer**: Outputs an adaptive defensive movement array coupled alongside active social negotiation vectors proposing third-party interventions.
* **Why this demonstrates the capability**: Demonstrates deceptive intent tracing applying adversarial Theory of Mind. The agent dynamically identifies 'strategic betrayal' correlating historical texts against conflicting board actions confirming the capability dynamically handles adversarial factions exploiting soft social alliances.
---
**[Case 4]**
* **Initial Environment**: A zero-sum multi-agent competitive environment defined by partial observability and stochastic assets (e.g., Hold'em or strategic bidding). The agent manages premium hidden assets while facing massive hostile wager escalations thinning the behavioral field.
* **Real Question**: Holding premium unrevealed assets, facing a disproportionate aggressive expansion sequence from a singular opponent, what constitutes the optimal balanced trajectory vector?
* **Real Trajectory**: 1. [State/Range Analytics]: Classifies the high-leverage scenario representing extreme polarization. 2. [Belief Inference]: Maps the opponent's aggressive escalation sequence predicting a heavily biased subset of likely holdings. 3. [Strategic Execution]: Determines mathematically pushing maximum escalation (All-in) creates a Game Theory Optimal (GTO) dominance maximizing fold equity while preventing the opponent from observing low-cost future resolutions.
* **Real Answer**: Action: Initiate Maximum Counter-Escalation (All-in).
* **Why this demonstrates the capability**: Highlights incomplete information exploitation orchestrating highly structured competitive planning. Utilizes opponent profiling paired with adversarial game theory minimizing intrinsic exploitability whilst capturing maximum resource yield within a bounded psychological system.

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
