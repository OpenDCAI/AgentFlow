---
name: information-asymmetric-theory-of-mind-reasoning
description: Use this skill when analyzing multi-party interactions where characters possess conflicting knowledge, or when verifying a speaker's identity strictly based on what they know or how they interact. Trigger it for requests like 'what does she think happened?', 'does he understand why she's mad?', or 'which character from the book is most likely speaking this line?'. Everyday scenarios include characters missing facts by leaving a room, forming false beliefs about another's core intentions, or identifying a hidden persona based on pragmatic conversational clues and unique historical knowledge limitations.
---

# Skill: information-asymmetric-theory-of-mind-reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform robust Theory of Mind (ToM) reasoning across cognitive categories (beliefs, intentions, knowledge) driven by information asymmetry. This involves isolating an omniscient view from individual character perspectives, mapping explicit false beliefs based on unequal conversational access, and applying zero-shot role inference to mathematically deduce a hidden speaker's identity based exclusively on uniquely compartmentalized epistemic boundaries and pragmatic social dynamics.
* **Dimension Hierarchy**: Social and Persona Modeling->Mental-state Reasoning->information-asymmetric-theory-of-mind-reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A group chat where Linda and David discuss Linda’s new dog. Kailey physically departs to acquire coffee right as the specific breed is revealed, returning only as the group transitions to discussing dog training tricks.
* **Real Question**: What breed would Kailey think Linda’s dog is?
* **Real Trajectory**: 1. Execute access tracking spanning occurrences before, during, and after Kailey's absence. 2. Quarantine the variable detailing the precise dog breed exclusively within Linda and David's operational knowledge graph. 3. Establish a divergent omniscient perspective. 4. Construct a response strictly bound to Kailey's specific informational deficit, ignoring internal systemic factual truths available globally.
* **Real Answer**: Kailey does not possess the necessary context to know the specific breed of the dog.
* **Why this demonstrates the capability**: It strictly contrasts the AI's internal omniscient perception against a simulated constrained character state. Failing to compute information occlusion via distinct presence intervals directly induces associative knowledge hallucinations.
---
**[Case 2]**
* **Initial Environment**: A deeply rooted dialogue involving two associates: Liam (organized) and Ethan (struggling financially). An intense information asymmetry emerges as Ethan hides his massive financial deficit but avoids Liam.
* **Real Question**: How does Ethan think that Liam feels when Ethan finally admits he is drastically falling behind on his bills?
* **Real Trajectory**: 1. Extract Liam's true psychological architecture: highly supportive. 2. Investigate Ethan’s separate inferential process warped by active deception. 3. Pinpoint Ethan’s specific False Belief projecting overarching judgment. 4. Distinctly articulate the delta between Liam's reality and Ethan’s psychological assumption.
* **Real Answer**: Ethan incorrectly assumes Liam will harbor deep annoyance regarding his prolonged silence, whereas Liam actually feels profound concern and an earnest desire to assist without judgment.
* **Why this demonstrates the capability**: This illustrates second-order False Belief mapping utilizing personality traits under limited disclosure. The agent cleanly partitions actual first-order emotional states against distorted second-order prognostications driven directly by obscured information.
---
**[Case 3]**
* **Initial Environment**: A snippet from a 19th-century adventure novel setting involving a secretive moral dilemma. Character 1 is Huck Finn; Character 2's identity is hidden. The candidate pool includes Aunt Polly, Sid, and Tom Sawyer.
* **Real Question**: Character 1: [Thinking: I try to think of a way out of this mess.] Maybe we ought to leave town. Just light out. Character 2: [Thinking: torn between fear and accountability.] But what about Muff Potter? He didn’t do nothing, and he’s gonna hang if we don’t say something. Who is Character 2?
* **Real Trajectory**: 1. Evaluate environmental and dialogue limits establishing the concept 'Muff Potter's innocence' as an intensely constrained epistemic variable known only to a few individuals. 2. Parse pragmatic intent analyzing Character 2's internal monologue highlighting youthful moral rebellion. 3. Rule out Aunt Polly and Sid based directly on these informational and psychological boundaries. 4. Deduce Tom Sawyer as the speaker.
* **Real Answer**: The hidden speaker is Tom Sawyer.
* **Why this demonstrates the capability**: This case merges Theory of Mind with Persona Inference. The agent applies severe epistemic boundary maintenance to recognize that the concealed secret is known only to specific entities, subsequently utilizing internal psychological assumptions to definitively unmask the missing identity.

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
