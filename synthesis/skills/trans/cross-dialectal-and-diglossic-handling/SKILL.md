---
name: cross-dialectal-and-diglossic-handling
description: Use this skill when the user wants to translate content that uses local dialects, regional slang, or non-standard language varieties (like Egyptian Arabic, Krama Javanese, or Hong Kong Cantonese) into a formal standard, or vice-versa. Trigger it for requests like 'translate this Mandarin into spoken Cantonese,' 'make it sound like how people talk in Hong Kong,' 'use the polite Krama version for this Javanese text,' or 'convert this colloquial Cantonese chat into standard written Chinese.'
---

# Skill: cross-dialectal-and-diglossic-handling

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to accurately translate between standardized language varieties (diglossia) and their regional or social registers—such as the high-level politeness systems found in Javanese (Krama/Ngoko) or the spoken-written divergence between Hong Kong Cantonese and Standard Mandarin. This involves resolving lexical, morphological, and syntactical variations while preserving semantic equivalence and socio-linguistic appropriateness, particularly in 'Written-to-Colloquial' transitions where word-for-word translation fails due to archaic grammar and unique regional vocabularies.
* **Dimension Hierarchy**: Specialized and Culturally Grounded Translation->Dialectal and Socio-Linguistic Translation->cross-dialectal-and-diglossic-handling

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is provided with an English narrative sentence about a historical battle. The target requirement is a 'Krama' Javanese version, which is the high-politeness register used for formal settings and social hierarchy.
* **Real Question**: Translate the following sentence into Krama (Formal) Javanese: 'After a battle against the Romans, Muawiyah and his soldiers were victorious.'
* **Real Trajectory**: The agent identifies the source as English and the target as the formal Krama register. It selects the specific polite lexical items such as 'Sasampunipun' instead of the casual 'Sawise' and 'prajuritipun' for soldiers. It ensures the verb 'kasil menang' aligns with the sophisticated tone required by the honorific system.
* **Real Answer**: Sasampunipun perang nglawan tiyang-tiyang Romawi, Muawiyah lan prajuritipun kasil menang.
* **Why this demonstrates the capability**: This demonstrates the ability to shift from a standard English concept to a specific social register. Success requires the agent to bypass the common casual Javanese (Ngoko) and select the 'Krama' variant, which is often less represented in training data and requires precise honorific mapping.
---
**[Case 2]**
* **Initial Environment**: A translation environment where a user provides a standard written Mandarin sentence using common vocabulary. The goal is to generate a spoken-style Cantonese equivalent suitable for Hong Kong colloquial use.
* **Real Question**: Please translate the following Mandarin into Cantonese colloquial language: 我們能有幾回機會像這樣一起旅行，所以我們一定要好好珍惜。
* **Real Trajectory**: The agent identifies the diglossic shift from the Mandarin written standard to the Cantonese spoken form. It maps the Mandarin plural pronoun '我們' to the Cantonese '我哋' and the adverbial '幾回' to the colloquial '幾何'. It restructures the middle clause '像這樣' into the Hong Kong idiomatic '好似噉' to achieve natural flow while preserving the final semantic intent regarding 'cherishing the trip.'
* **Real Answer**: 我哋有幾何機會好似噉一齊旅行，所以我哋一定要好好珍惜。
* **Why this demonstrates the capability**: This case highlights the 'Written-to-Colloquial' divergence in Hong Kong linguistics. A literal or word-for-word translation would maintain Mandarin-style terms that sound robotic or 'un-HK' when spoken; the agent's ability to pivot to specific colloquial particles and vocabulary demonstrates authentic diglossic resolution.
---
**[Case 3]**
* **Initial Environment**: The agent receives a colloquial Cantonese sentence from a chat transcript, complete with regional particles and non-standardized phrasing. The goal is to normalize this into standard written Mandarin for a general professional audience.
* **Real Question**: Please translate the following Cantonese into Mandarin colloquial language: 我哋嘅談判已經去到咗死衚衕，雙方都唔能夠妥協。
* **Real Trajectory**: The agent parses the Cantonese possessive marker '嘅' and the aspectual particle '咗'. It recognizes the colloquial negation '唔能夠' and converts the entire string into the matrix written standard. It substitutes '我哋嘅' with '我们的' and ensures the final Mandarin string uses standard grammatical structures while keeping the 'dead end' metaphor intact.
* **Real Answer**: 我们的谈判已经走到了死胡同，双方都无法妥协。
* **Why this demonstrates the capability**: This reflects the 'Colloquial-to-Standard' normalization process. Models often struggle with non-standardized Cantonese syntax; here, the agent correctly identifies regional markers and maps them to standard characters while maintaining the professional weight of the negotiation context.

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
