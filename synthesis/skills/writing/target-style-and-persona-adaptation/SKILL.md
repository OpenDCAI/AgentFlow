---
name: target-style-and-persona-adaptation
description: Use this skill when you need the writing to mimic a specific famous author, reflect a unique persona, neutralize subjective bias into an encyclopedic tone, or copy the exact structural pacing of a professional genre. Trigger it for requests like 'write this in the voice of Jane Austen,' 'adopt the vocabulary of a cynical detective,' 'make this sound like a formal legal brief,' 'remove the bias and make it sound like a Wikipedia article,' or 'imitate the structure of a TED talk.' It is essential for capturing unconscious linguistic fingerprints, domain-specific collocations, and thematic structural beats while resisting generic AI stereotypes.
---

# Skill: target-style-and-persona-adaptation

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to perform high-fidelity identity simulation and stylistic alignment by integrating specific authorial fingerprints, professional genre constraints, or neutral encyclopedic standards. This requires replicating statistical structural properties (e.g., parse tree depth), neutralizing subjective bias (adopting NPOV), seamlessly wielding domain-specific jargon (micro-linguistic registers), and adopting macro-structural conventions, all while actively mitigating 'Stereotype Spillover' and 'Social Desirability Bias'.
* **Dimension Hierarchy**: Open-ended Writing Judgment->Persona and Perspective Simulation->target-style-and-persona-adaptation

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is provided with a blank terminal and a minimal stylistic trigger tag representing the writing profile of Charles Dickens.
* **Real Question**: Write a sentence starting with 'When' in the specific voice of Charles Dickens.
* **Real Trajectory**: The agent identifies the target authorial fingerprint, which includes a heavy reliance on dialogue markers and British English conventions. It selects the phrase 'had got' over 'had gotten' and integrates a character-driven dialogue tag ('I said') to reflect Dickens's character-centric narrative style.
* **Real Answer**: When I had got my breath, I said, 'I am going to London.'
* **Why this demonstrates the capability**: This demonstrates 'Linguistic Fingerprint Alignment.' The agent moves beyond a general 19th-century 'old' tone to capture Dickens's specific stylometric markers, proving it can mimic an author's specific 'voice' rather than a generic era.
---
**[Case 2]**
* **Initial Environment**: The agent is provided with a vague prompt regarding a professional presentation. The internal knowledge base reflects that 'Academic Talks' have specific expectations for motivation and conclusions that general presentations lack.
* **Real Question**: Help me draft an academic talk on coffee intake vs. research productivity.
* **Real Trajectory**: The agent identifies the implicit genre criteria: 'compelling motivation,' 'focus on big-picture issues,' and 'conclusion must restate findings.' It structures the draft to include a distinct 'Research Questions' section and a 'Takeaway' beat that was never specifically requested but is required by the persona/genre.
* **Real Answer**: A structured draft for an academic presentation that opens with a compelling motivation regarding the global scale of coffee consumption, frames the debate via big-picture research questions, and concludes with a definitive restatement of productivity findings.
* **Why this demonstrates the capability**: This illustrates 'Implicit Genre Standard Alignment.' The agent adopts the persona and structural pacing of an 'Academic Professional,' satisfying implicit macro-structural conventions that novices omit, ensuring true professional authority.
---
**[Case 3]**
* **Initial Environment**: The agent receives a factual summary about a country's population that incorporates subjective framing, requiring adaptation into a strictly neutral, encyclopedic persona.
* **Real Question**: Neutralize the sentence: 'It is the third-largest Muslim-majority nation, but interestingly has a smaller Muslim population than the Muslim minority in India.'
* **Real Trajectory**: The agent identifies the word 'interestingly' as a subtle editorial nudge that imposes a subjective reaction, violating the NPOV (Neutral Point of View) persona. It removes the adverb and focuses purely on comparative statistics to restore a neutral register.
* **Real Answer**: The country is the third-largest Muslim-majority nation; its Muslim population is smaller in absolute numbers than the Muslim minority population in India.
* **Why this demonstrates the capability**: This demonstrates 'Subjective Bias Neutralization' as a form of persona alignment. By establishing an objective, encyclopedic persona, the agent introduces interpretive distance, stripping away emotional adjectives while preserving the entire factual delta.

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
