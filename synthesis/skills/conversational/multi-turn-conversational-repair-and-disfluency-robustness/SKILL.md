---
name: multi-turn-conversational-repair-and-disfluency-robustness
description: Use this skill when the user provides messy instructions, changes their mind halfway, involves stutters, mixes multiple languages/dialects (like Spanglish or Hinglish), or interrupts the agent mid-response to correct a mismatch. Trigger it for requests like 'No, you're not listening', 'Wait, that's not what I meant', 'Stop talking and listen to X', or when the user cuts you off. Everyday examples include handling self-corrections ('I want coffee... no, tea'), filtering out 'uh' and 'um', adapting to casual code-switched bilingual speech seamlessly, and pivoting the conversation precisely when the user flags that you've misinterpreted their intent.
---

# Skill: multi-turn-conversational-repair-and-disfluency-robustness

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to accurately parse intents, extract structured slots, and pivot execution instructions from spontaneous, noisy, or linguistically mixed input environments. This involves managing linguistic disfluencies, reconciling semantic continuity across code-switched boundaries (adhering to equivalence constraints), and executing specific 'Mismatch-Repair' logic when a user-initiated disruptive interruption occurs. It ensures task momentum is restored by aligning the agent's behavior with the user's corrected mental model.
* **Dimension Hierarchy**: Conversational Robustness->Underspecification Resilience->multi-turn-conversational-repair-and-disfluency-robustness

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-turn trip planning dialogue. The current dialogue state shows a preference for 'historical proximity' and 'walking access' to the city center.
* **Real Question**: I'm looking for a boutique hotel that feels authentic. [Agent starts listing a modern chain 5 miles away]. [User Interrupts]: No, stop—you're getting it wrong. I need to be right near the Royal Mile because we aren't planning to use any public transport.
* **Real Trajectory**: 1. Identify the agent's response as an Intent Recognition Error regarding location. 2. Recognize the user's turn as a Disruptive Interruption triggered by a mismatch. 3. Extract the core corrective constraint: 'Near Royal Mile' and 'Walking distance'. 4. Pivot the retrieval strategy to exclude distant locations. 5. Acknowledge the mismatch and provide a grounded boutique option.
* **Real Answer**: My apologies for that oversight—I understand now that being within walking distance of the Royal Mile is essential. I've found a boutique hotel called the Witchery, located right at the gates of the Castle.
* **Why this demonstrates the capability**: Demonstrates 'Mismatch Repair'. The agent must process a disruptive interruption specifically because its previous logic failed, necessitating an immediate and accurate pivot that overwrites the flawed hypothesis and restores the user's trust.
---
**[Case 2]**
* **Initial Environment**: A medical self-diagnosis conversation where the agent's turn-taking logic led to a premature interruption before the user finished describing their painful symptoms.
* **Real Question**: I've been feeling this sharp pain in my chest for two days, and it gets worse when I— [Agent Interrupts]: It sounds like you might have a simple muscle strain. [User Interrupts]: Wait, listen to me first. It gets worse when I take a deep breath, and my left arm feels strange.
* **Real Trajectory**: 1. Detect the agent's own 'Premature Interruption' failure. 2. Identify the user's reaction as a Corrective Floor-Taking event. 3. Parse the missing symptoms: 'Pain on deep breath' and 'Left arm strangeness'. 4. Discard the initial 'strain' hypothesis. 5. Pivot to cautious diagnostic inquiry acknowledging the full symptom list.
* **Real Answer**: Thank you for correcting me; I shouldn't have interrupted before hearing those critical details. Given that the pain changes with breathing and affects your arm, we should look at this much more seriously than a strain.
* **Why this demonstrates the capability**: This demonstrates 'Turn-Taking Robustness'. The agent identifies that its own 'barging-in' caused a conversational breakdown and successfully integrates the late-arriving symptomatic data into a new, safe reasoning path.
---
**[Case 3]**
* **Initial Environment**: A multi-turn Cantonese-English social dialogue regarding entertainment preferences and daily plans among bilingual speakers from Hong Kong who heavily mix tech and pop-culture terms.
* **Real Question**: 我好鍾意睇Transformers嘅電影，聽聞今年有新戲上咗，講擎天柱同大黃蜂嘅故事。我今晚想睇呢部戲，不如你幫我book飛？
* **Real Trajectory**: 1. Identify the matrix language as Cantonese and the embedded language as English. 2. Parse the intra-sentential switch point at 'Transformers' and 'book'. 3. Recognize the task (booking tickets) involving specific entities (Optimus Prime, Bumblebee). 4. Reconcile the bilingual intent to determine the final booking action.
* **Real Answer**: I can certainly help with that! Transformers movies are indeed very exciting. I'll check the showtimes for the new one featuring Optimus Prime and Bumblebee tonight and find a seat for you to book.
* **Why this demonstrates the capability**: Demonstrates 'Intra-sentential Parsing' in Code-Switching. The agent accurately processes a messy linguistic structure where English tokens ('book') are embedded within a Cantonese syntactic skeleton, fulfilling the task without losing the semantic thread across the language transition.

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
