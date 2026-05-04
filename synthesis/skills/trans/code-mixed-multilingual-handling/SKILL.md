---
name: code-mixed-multilingual-handling
description: Use this skill when translating content that mixes two or more languages (like Hinglish, Spanglish, or Manglish) into a single language, or vice versa. It is especially important for handling casual dialogues where people switch languages mid-sentence, such as in chat transcripts or social media. Trigger this for requests like 'translate this mixed English-Mandarin chat,' 'put this Hinglish text into pure English,' 'make sure you don't ignore the non-English words,' or 'test if the translator understands how bilingual speakers talk.'
---

# Skill: code-mixed-multilingual-handling

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to accurately translate and normalize code-switched (CS) discourse—where speakers alternate between a matrix language and an embedded language—without suffering from Code-Switching Loss (CSL). This includes resolving intra-sentential language shifts, maintaining Speaker Attribution (SMA) within dialogues, and preventing Meaning Shifts (MST) caused by the literal misinterpretation of the minority language components. It requires high-fidelity comprehension of linguistic alternation, burstiness, and span entropy to produce source-aligned translations that preserve the propositional intent across all mixed segments.
* **Dimension Hierarchy**: Contextual and Constraint-Aware Translation->Rule-Conditioned Translation->code-mixed-multilingual-handling

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent is provided with a Tamil-English (EN-TA) code-switched dialogue between two people discussing a health issue. The source uses phonetic Romanized Tamil mixed with English phrases.
* **Real Question**: Translate the following code-switched dialogue into pure English: 'Matthew: Enakku cold irukku. Unga elllaroda support um vennum. Athu romba painful. Lisa: Atha fight pannu. Orange juice kudi. Soup pannu. Matthew: Naa try panren. Lisa: Naa unna believe panran.'
* **Real Trajectory**: The agent identifies the matrix language shift between the Romanized Tamil and English. It recognizes 'Enakku' as 'I have', 'vennum' as 'need', and 'Atha' as 'it', ensuring no Tamil spans are ignored (avoiding CSL). It preserves the speaker roles for Matthew and Lisa (avoiding SMA) and renders the full dialogue into fluent English.
* **Real Answer**: Matthew: I have a cold. I need all of your support. It's very painful. Lisa: Fight it. Drink orange juice. Make soup. Matthew: I'll try. Lisa: I believe in you.
* **Why this demonstrates the capability**: This demonstrates the ability to avoid 'Code-Switching Loss' by processing the Tamil segments that carry the core meaning of the ailment and the specific advice given. Without this capability, a model might only translate the English words ('cold', 'support', 'painful'), leading to a fragmented and semantically hollow output.
---
**[Case 2]**
* **Initial Environment**: A translation agent processes a Mandarin-English (EN-ZH) dialogue regarding an airport pickup. The text alternates at the sentence level between English and Chinese characters.
* **Real Question**: Translate this Mandarin-English conversation into pure English: 'Anna：有人去机场接Mark吗？ Marcus：I could but when and where from? Anna：Sydney，星期四3点. Marcus：am 还是 pm？:D Leslie：haha, 幸运的是下午:D'
* **Real Trajectory**: The agent parses the Mandarin characters ('有人去机场接Mark吗' = 'is anyone going to the airport to pick up Mark') and links them to the English responses. It carefully tracks that Leslie is the one mentioning the '下午' (afternoon/pm) and not Anna, maintaining Speaker Misattribution resistance (SMA).
* **Real Answer**: Anna: Is anyone going to the airport to pick up Mark? Marcus: I could but when and where from? Anna: Sydney, Thursday at 3. Marcus: AM or PM? :D Leslie: Haha, fortunately it's in the afternoon :D
* **Why this demonstrates the capability**: This case tests resistance to 'Speaker Misattribution' (SMA) and 'Meaning Shift' (MST). In CS dialogues, agents often lose track of which speaker provided specific information in the non-English segments; here, the agent correctly attributes the timing confirmation to Leslie while accurately decoding the Mandarin temporal markers.

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
