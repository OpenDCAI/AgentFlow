---
name: information-gain-maximizing-sequential-inquiry
description: Use this when the user needs to reach a target outcome by asking the most efficient sequence of questions to narrow down a large set of possibilities. Trigger it for requests like 'find the right item using the fewest questions', 'create a help desk flow that identifies the problem fast', 'give me a search plan that eliminates wrong options systematically', or 'design a guide that gets to the answer without redundant steps'.
---

# Skill: information-gain-maximizing-sequential-inquiry

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to plan an optimal sequence of discriminative inquiries or probe actions by evaluating the information gain of potential attributes, specifically designed to reduce state uncertainty—modeled as entropy over a candidate set—reaching a terminal goal state in the minimum number of interaction turns.
* **Dimension Hierarchy**: Open-World Real-World Planning->Information-Grounded Plan Construction->information-gain-maximizing-sequential-inquiry

### Real Case
**[Case 1]**
* **Initial Environment**: A product catalog containing 5,000 lipsticks with varying attributes for color, brand, finish type, and price range. The agent has a customer preference profile: Wanted(Color: Dynamite Red), Unwanted(Brand: Gocheaper), Optional(Price).
* **Real Question**: Help me find a lipstick that meets my preferences by asking only the most relevant questions to narrow it down quickly.
* **Real Trajectory**: 1. [Information Gain Calculation]: Analyzes the catalog and determines that 'Color' has the highest entropy split. 2. [Inquiry]: Asks for color preference. 3. [Feedback]: Receives 'Dynamite Red', reducing candidates from 5,000 to 120. 4. [Re-evaluation]: Determines 'Brand' is the next most discriminative attribute. 5. [Inquiry]: Asks if any brands should be avoided. 6. [Feedback]: Receives 'Avoid Gocheaper', reducing candidates to 15. 7. [Terminal Action]: Recommends the top-rated product from the remaining set.
* **Real Answer**: Maybelline New York Color Sensational Red (Dynamite Red).
* **Why this demonstrates the capability**: The agent acts as a strategic planner using decision-tree logic to order inquiries. Instead of asking about 'Price' (which was optional) or 'Special Features' (low information gain), it prioritizes attributes that mathematically maximize the split of the search space, ensuring the shortest trajectory to discovery.
---
**[Case 2]**
* **Initial Environment**: A technical support knowledge base for a 'Computer Won't Boot' scenario. Possible faults include Power Supply, RAM failure, Motherboard failure, or Display issues. The agent must troubleshoot a user's machine.
* **Real Question**: Guide the user through a troubleshooting plan to identify why their computer won't start in the fewest steps possible.
* **Real Trajectory**: 1. [Thought]: Identify 'Power Status' as the most discriminative initial probe. 2. [Inquiry]: 'Are there any lights or fan noises when you press the power button?' 3. [Observation]: 'No lights, no sound.' (Eliminates RAM and Display immediately). 4. [Thought]: Next highest gain is Power Socket check vs. PSU internal check. 5. [Inquiry]: 'Is the power cable plugged directly into the wall or a strip?' 6. [Terminal Action]: Identify Power Supply failure based on subsequent cable verification.
* **Real Answer**: Plan: Check lights/fans -> Check wall socket connectivity -> Diagnose PSU failure.
* **Why this demonstrates the capability**: The agent creates a decision-tree-based plan where each diagnostic step is chosen specifically to eliminate the largest possible subset of potential faults. It bypasses low-gain questions (like 'What OS are you using?') when a high-gain question (Power status) can prune half the fault tree in one turn.

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
