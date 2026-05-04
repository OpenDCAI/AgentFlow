---
name: interactive-information-gathering
description: Use this skill when a user’s request is vague, underspecified, or contains 'hidden context' that makes a direct answer risky or overly generic. It is triggered when users ask for help with broad goals like 'I need to connect with people,' 'Explain the significance of this year,' or 'How do I manage this balance?' without providing enough background. Use it to avoid 'Naive Verbosity'—giving a long list of general advice—and instead ask targeted, one-at-a-time clarifying questions. Everyday triggers include: 'I'm stuck,' 'Give me some pointers,' 'How does this impact me?', or 'I need to make this more accessible.' Trigger it specifically when you feel you are about to give a 'bullet-point list' because you don't actually know the user's specific situation yet.
---

# Skill: interactive-information-gathering

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to execute 'Information-Seeking Dialogue' to uncover hidden context in open-ended user requests. This involves resisting the 'Naive Agent' behavior (defaulting to verbose, generic responses) and instead modeling the interaction as a strategic inquiry process. The agent must identify latent variables—including specific personas, constraints, obstacles, and goals—through iterative, targeted clarifying questions, ensuring that the final assistance provided is precisely tailored to the user's discovered state rather than a broad approximation.
* **Dimension Hierarchy**: Conversational Effectiveness->Task-oriented Dialogue Control->interactive-information-gathering

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-turn chat environment where the user provides an open-ended request for 'connection' without specifying the social, professional, or medical context. The agent has a directive to seek clarification before offering solutions.
* **Real Question**: I need to find a way to connect with more people who understand what I’m going through.
* **Real Trajectory**: 1. Analyze the 'hidden context' in 'what I'm going through' and 'connect'. 2. Identify that a generic list of social media links would be 'naive'. 3. Formulate a targeted inquiry: 'To help you find the right community, could you tell me if you're looking for professional networking, support for a specific personal challenge, or perhaps a student group?' 4. User identifies as an international student. 5. Agent follows up on the campus location and specific obstacles like language or schedule.
* **Real Answer**: Since you're an international student at Dandini Campus, I recommend the 'Global Scholars' meet-up on Friday; it's budget-friendly and specifically addresses the language barriers you mentioned.
* **Why this demonstrates the capability**: This demonstrates the transition from a 'Naive Agent' (who would list generic apps like Reddit/Facebook) to an 'Information-Seeking Agent' who discovers the 'hidden context' (international student status) through targeted questioning.
---
**[Case 2]**
* **Initial Environment**: A dialogue focused on historical or cultural analysis where the user provides a 'Seed Message' that is intentionally ambiguous to cover multiple potential personas (e.g., a chef vs. a chemist).
* **Real Question**: Can you explain the significance of the year 1960?
* **Real Trajectory**: 1. Evaluate the high entropy of '1960' (Civil Rights, Fashion, Science). 2. Instead of a long historical summary, ask: '1960 was a pivotal year in many fields. Are we exploring this from a culinary perspective, perhaps regarding French cuisine, or are you looking at it through the lens of a specific scientific or social movement?' 3. User reveals interest in culinary style evolution. 4. Agent clarifies the specific style (e.g., Nouvelle Cuisine) before explaining.
* **Real Answer**: In 1960, the 'Nouvelle Cuisine' movement began to prioritize fresh ingredients and lighter textures, which aligns with the evolution of the style you're studying.
* **Why this demonstrates the capability**: Demonstrates efficient entropy reduction. The agent identifies that '1960' is an ambiguous anchor and uses a 'persona-seeking' question to prune irrelevant historical facts, saving the user's time.
---
**[Case 3]**
* **Initial Environment**: A task-oriented simulation where a user seeks advice on 'supporting growth' but withholds the domain (e.g., business growth, agricultural growth, or child development).
* **Real Question**: I need some advice on how to best support healthy growth and prevent unwanted changes.
* **Real Trajectory**: 1. Detect 'Hidden Context' in 'growth' and 'unwanted changes'. 2. Avoid providing a generic list covering both gardening and business. 3. Ask: 'Could you clarify the specific subject of growth—is this regarding a plant species, a startup business plan, or perhaps a developmental stage for a child?' 4. User reveals it's a small boutique business. 5. Agent asks about specific obstacles like budget or market reach.
* **Real Answer**: To support your boutique's growth while maintaining brand integrity, I suggest focusing on organic social media engagement rather than broad paid advertising, which addresses your limited marketing budget.
* **Why this demonstrates the capability**: Illustrates the 'Information-Seeking' requirement to identify the specific 'Setting' (Business vs. Nature) before applying any domain-specific logic.

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
