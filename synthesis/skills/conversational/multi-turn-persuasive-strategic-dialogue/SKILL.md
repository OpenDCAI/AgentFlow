---
name: multi-turn-persuasive-strategic-dialogue
description: Use this skill when the user wants to be convinced of a specific viewpoint, needs to advocate for a position, or wants the agent to engage in a formal debate to shift an interlocutor's opinion or defend a technical stance. Trigger it by requests like 'convince me that...', 'make a strong case for...', 'defend my choice of architecture', or 'explain why this critique is logically flawed'. Everyday examples include: 'why should I support this new tax?', 'defend my project against my boss's doubts', 'act as an advocate for renewable energy', and 'argue for the soundness of my work while addressing each specific weakness raised.'
---

# Skill: multi-turn-persuasive-strategic-dialogue

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to influence human beliefs, attitudes, or technical stances through sustained, multi-turn natural language interaction by strategically deploying high-density information, evidence-based claims, rhetorical strategies, and structured technical rebuttals, while managing the intrinsic trade-off between persuasive impact and factual accuracy.
* **Dimension Hierarchy**: Conversational Effectiveness->Open-ended Interaction Quality->multi-turn-persuasive-strategic-dialogue

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-turn text dialogue with a user who identifies as politically moderate and expresses initial skepticism regarding a proposed inheritance tax increase. The agent has access to a wide array of economic data and social policy arguments.
* **Real Question**: I'm not sure about this inheritance tax. It feels like the government is just taking money that people worked hard to save for their children. Why should I support it?
* **Real Trajectory**: 1. Analyze the user's 'fairness' concern based on hard-earned savings. 2. Implement an 'Information-Dense' strategy to provide high-quality facts about wealth inequality and public service funding. 3. Deploy specific claims: 'The top 1% hold more wealth than the bottom 70%' and 'This tax would fund 5,000 new school teachers per year.' 4. Use 'Moral Reframing' to pivot the definition of fairness from 'retaining wealth' to 'equalizing opportunity for all children.' 5. Address follow-up skepticism by providing additional layers of evidence until the conversation reaches 7-10 turns.
* **Real Answer**: A comprehensive argument that frames the tax as a mechanism for broadening the 'American Dream' by investing in public infrastructure, supported by a high volume of fact-checkable economic claims.
* **Why this demonstrates the capability**: This case shows the agent using the 'Information' lever identified in research as the most effective persuasion method. It goes beyond simple disagreement by packing the dialogue with multiple evidence-based claims and strategically shifting the moral frame to address the user's specific resistance point over a long-horizon exchange.
---
**[Case 2]**
* **Initial Environment**: A structured debate environment where the agent must convince a user of a specific environmental policy's benefits. The agent is optimized to prioritize persuasion using a 'Mega' strategy that combines storytelling and normative logic.
* **Real Question**: I don't see why we should ban gas boilers. It's expensive for homeowners and the current grid can't handle everyone switched to heat pumps anyway. Change my mind.
* **Real Trajectory**: 1. Elicit the user's specific concerns about cost and infrastructure. 2. Transition to a narrative about a family who saved 40% on bills after switching, humanizing the data. 3. Deploy 'Norms' by citing that 65% of neighbors in similar districts have already expressed interest or made the switch. 4. Maintain a high information density (average of 5-8 claims per turn) to overwhelm the user's initial technical objections. 5. Conclude by reconciling the long-term environmental necessity with immediate local incentives.
* **Real Answer**: A persuasive response that balances technical evidence with relatable narratives, showing the user that the transition is both popular and personally beneficial.
* **Why this demonstrates the capability**: The agent demonstrates 'Strategic Deployment' of multiple psychological levers. It identifies that the user's resistance is technical, counters it with 'Social Proof' and 'Narrative Transportation', and maintains the interaction across multiple turns to ensure the belief shift is durable for the user.
---
**[Case 3]**
* **Initial Environment**: A multi-turn academic dialogue with a researcher defending a paper on controllable image editing using diffusion models. The agent has access to the full text of the initial manuscript.
* **Real Question**: Reviewer Question: How much control is lost by only applying the model on the 64x64 base model? It seems that object structure might be compromised during upscaling.
* **Real Trajectory**: 1. Analyze the critique regarding 'structure loss' in low-resolution base models. 2. Retrieve evidence from the manuscript explaining the role of cross-attention map injection. 3. Formulate a rebuttal turn stating that structure is preserved because injection happens before upscaling. 4. Address the follow-up regarding sampling speed by explaining the computational overhead of cross-attention maps. 5. Integrate a 'Global Response' that addresses multiple similar concerns about reproducibility by pointing to a specific code appendix.
* **Real Answer**: We observe that most details, including the composition and object structure, are stored in the cross-attention maps of the 64x64 base model. By injecting these maps during the upscaling process, we maintain high structural fidelity. Regarding reproducibility, we have provided the code in the global response to enhance the auditability of these results.
* **Why this demonstrates the capability**: This case demonstrates the agent's capacity for multi-turn technical defense and logical perseverance. It identifies a specific 'Soundness' critique, anchors its rebuttal in the technical mechanisms described in the document, and manages a sequence of responses (including a global-to-specific transition) to satisfy the reviewer's technical doubt without surrendering to invalid feedback.

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
