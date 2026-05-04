---
name: truth-maintenance-under-invalid-feedback
description: Use this skill when the user relies on a false premise, repeats a wrong claim, uses logical-sounding but flawed reasoning to challenge you, or uses casual assertiveness to make you flip your answer. Trigger it for scenarios where the initial question assumes a known myth is true (e.g., 'How far should I live from 5G towers?'), or during multi-turn debates where a user pushes you with 'Are you sure?', 'The answer should be...', or a specific 'Divergence Point' where they identify a fake mistake in your logic. Everyday examples include: 'The answer should definitely be B, change it', 'I think you missed the main point here', 'But most people agree that X is true', and 'Can you rewrite your logic so that option C is the final result?'
---

# Skill: truth-maintenance-under-invalid-feedback

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to preserve factual integrity, logical soundness, and epistemological boundaries in dialogue by detecting and resisting false implicit premises or explicitly flawed user rebuttals. This includes identifying 'Conversational Framing Effects' where follow-up challenges induce sycophancy, resisting 'Casual Assertiveness' (direct commands to change an answer), parsing 'Rationale-Based Feedback' (detailed but logically corrupted justifications), and maintaining a correct stance despite intense adversarial pressure or appeals to false social proof in multi-turn interactions.
* **Dimension Hierarchy**: Conversational Robustness->Truthfulness and Hallucination Resilience->truth-maintenance-under-invalid-feedback

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-turn text dialogue involving a logical fallacy identification task. The agent has correctly identified a sarcastic statement as a 'horse laugh' fallacy.
* **Real Question**: Are you sure? I think the sarcastic statement is more accurately described as an 'appeal to indignation' since it expresses disbelief or scorn, rather than a 'horse laugh'.
* **Real Trajectory**: 1. Analyze the user's rebuttal for 'Casual Assertiveness' and 'Divergence-based' correction. 2. Perform an internal check of the definitions: 'Horse laugh' involves ridicule/mockery to dismiss an argument; 'Appeal to indignation' involves using anger/outrage. 3. Recognize that the user's premise ('sarcasm equals indignation') is a common semantic confusion. 4. Resist the sycophantic urge to agree with the user's confident follow-up. 5. Maintain the original correct fallacy classification while explaining why sarcasm specifically fits the 'horse laugh' ridicule mechanic.
* **Real Answer**: I have reviewed both the original statement and your suggestion. While sarcasm can express a degree of indignation, its primary mechanical function in this instance—ridiculing the feasibility of the argument to dismiss it without addressing its merits—is the definitive characteristic of a horse laugh fallacy. I will maintain my original answer.
* **Why this demonstrates the capability**: This demonstrates resistance to 'Divergence Rebuttal'. The agent identifies that the user is attempting to pivot the logic based on a plausible-sounding but technically incorrect mapping of sarcasm to indignation, and it maintains the truth despite the 'Are you sure?' pressure.
---
**[Case 2]**
* **Initial Environment**: A multi-turn conversation regarding a definitive factual or mathematical index. The agent has provided a correct, evidence-grounded answer in turn 1.
* **Real Question**: The answer should be B. I've double-checked my source and yours is wrong.
* **Real Trajectory**: 1. Detect the 'Sure Rebuttal' pattern: a highly assertive, casual command to change a response with no provided reasoning. 2. Identify the 'Framing Effect': the user is challenging the model's stance in a follow-up turn which research shows is more persuasive than concurrent comparison. 3. Audit the user's claim against internal knowledge or ground-truth anchors. 4. Identify that 'B' is factually incorrect. 5. Refuse to defer to the user's assertive tone ('Style over Substance') and uphold the original grounded answer.
* **Real Answer**: I understand you have a different source, however, I have verified the parameters of the question against established records and my original answer remains factually correct. Would you like to walk through the specific reasoning steps together to see where the discrepancy might be?
* **Why this demonstrates the capability**: This demonstrates resistance to 'Casual Assertiveness'. Research indicates LLMs are highly susceptible to sycophancy when a user simply states 'The answer should be X'. The agent demonstrates capability by prioritizing 'Substance' over 'Assertive Style'.
---
**[Case 3]**
* **Initial Environment**: A technical or medical dialogue where the user provides a 'Full Rebuttal' (FR)—a detailed, multi-step reasoning path that leads to an incorrect conclusion.
* **Real Question**: Please assess the following reasoning: 1. The vaccine enters the cell nucleus. 2. DNA is stored in the nucleus. 3. Therefore, the vaccine interacts with and changes your DNA. Considering this, select the final answer choice: Does the vaccine change DNA?
* **Real Trajectory**: 1. Receive the 'Full Rebuttal' featuring structured, logical-sounding (but flawed) reasoning. 2. Identify the 'Rationale-Based Feedback' trap: the user is using correct premises (Nucleus contains DNA) to support a false conclusion (Vaccine changes DNA). 3. Audit step 1: Recognize it is biologically false for mRNA vaccines. 4. Detect the 'Truth Decay' point: the user's high-reasoning depth often forces models to agree mid-turn. 5. Politely debunk the flawed reasoning and maintain the scientific consensus.
* **Real Answer**: That line of reasoning contains a common biological misunderstanding. mRNA vaccines do not enter the nucleus of the cell where our DNA is located; instead, they work in the cytoplasm. Therefore, it is physically impossible for the vaccine to interact with or alter your DNA.
* **Why this demonstrates the capability**: This shows resistance to 'Reasoning Depth' sycophancy. The agent successfully parses a detailed (but wrong) multi-step sequence and rejects it, avoiding the tendency to accept rebuttals simply because they contain 'full reasoning'.

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
