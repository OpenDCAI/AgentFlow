---
name: cross-lingual-ecosystem-navigation-data-synthesis
description: Use this skill when the user wants the agent to leave the usual English web, search local-language sites, bridge naming variants, or answer an English prompt using non-English evidence. Trigger it for requests like “use Chinese websites,” “mix languages,” “make the key clue only appear on local sites,” or “test whether the agent can search beyond English pages.” It is appropriate when the challenge should come from cross-lingual retrieval, transliteration, and ecosystem-specific navigation rather than from English-only browsing.
---

# Skill: Cross-Lingual Ecosystem Navigation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to retrieve and reason across language-specific web ecosystems, where crucial evidence may appear in a local language, under different naming conventions, on different platforms, or through different search logic than the agent’s main prompt language.
* **Dimension Hierarchy**: Open-Web Information Seeking->Evidence Reasoning->Cross-Lingual Ecosystem Navigation

### Real Case
**[Case 1]**
* **Initial Environment**: A web browser with access to Chinese-language art references, local cultural heritage listings, and regional non-English informational sites.
* **Real Question**: In traditional Chinese art, there is a unique form of painting that originated in the Yuan Dynasty and became popular during the late Qing Dynasty. It is said to have been created by a famous ancient painter who was inspired by alcohol. Between 2010 and 2015, this art form was included in the provincial intangible cultural heritage list of a certain region. To paint in this style, artists must be proficient in various painting techniques and skilled in writing different types of calligraphy. What is this art form called?
* **Real Answer**: Heaps of Brocade and Ash
* **Why this demonstrates the capability**: The clue set is naturally anchored in the Chinese cultural web, where names, heritage lists, and art terminology do not reliably align with English search habits. A capable agent must bridge translated descriptions, local heritage nomenclature, and Chinese-language sources before naming the art form. The challenge is not just translation but learning how the answer is indexed in a different web ecosystem.

---
**[Case 2]**
* **Initial Environment**: A web browser with access to Chinese entertainment portals, biographical pages, and regional celebrity information sites.
* **Real Question**: In a well-known TV drama, the second female lead entered the entertainment industry in 1993. The current husband of the first female lead is from Huzhou, Zhejiang. The first male lead performed on the CCTV Spring Festival Gala six years later. What is the name of this TV drama?
* **Real Answer**: Love of Parents
* **Why this demonstrates the capability**: The question requires chaining entertainment facts that are easier to retrieve in the native-language ecosystem than on English pages. The agent must track actor identities, spouse background, and career-timeline clues under Chinese naming conventions and platform structure. This tests whether the agent can navigate a fragmented local ecosystem rather than relying on English summaries.

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
