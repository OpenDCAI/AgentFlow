---
name: cross-lingual ecosystem navigation
description: Use this skill when the agent needs to move beyond English-centric web pages to search, reason, or perform interactive tasks (like shopping or attribute selection) on non-English websites. Trigger it for requests like “find a product on a French site,” “use the Chinese version of this shop,” “buy a yellow coat from the local store,” or “check these details across different language portals.” It is designed for scenarios where the challenge is not just translation, but navigating UI elements, buttons, and menus that are labeled in a foreign language.
---

# Skill: cross-lingual ecosystem navigation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to retrieve knowledge and execute interactive workflows (Search, Click, Attribute Selection, Checkout) within foreign-language web ecosystems. This involves 'Cross-Lingual Alignment' to map multilingual instructions and UI labels to functional actions, ensuring operational efficiency and accuracy across high-, mid-, and low-resource language environments.
* **Dimension Hierarchy**: Open-Web Information Seeking->Evidence Reasoning->cross-lingual ecosystem navigation

### Real Case
**[Case 1]**
* **Initial Environment**: A multilingual e-commerce platform (e.g., WebShop) initialized with a German language interface where buttons are labeled 'Suche' and 'Kaufen'.
* **Real Question**: Search for a large yellow coat priced below 40 Euros and initiate the purchase.
* **Real Trajectory**: 1. [search] 'Gelber Mantel' -> 2. [click] Next Page (Nächste Seite) to find price-matching results -> 3. [click] Item ID 1 -> 4. [click] Attribute: 'Groß' (Large) -> 5. [click] Attribute: 'Gelb' (Yellow) -> 6. [click] Buy Now (Jetzt Kaufen).
* **Real Answer**: Successfully landed on the purchase confirmation page with the correct 'Yellow' and 'Large' filters applied.
* **Why this demonstrates the capability**: The agent must interpret German UI labels for 'Size', 'Color', and 'Buy' to execute a multi-step purchase flow. Success requires aligning the English instruction 'large yellow coat' with the German attributes 'Groß' and 'Gelb' while navigating correctly labeled buttons rather than English defaults.
---
**[Case 2]**
* **Initial Environment**: A Chinese-language interactive cultural portal with navigation menus organized by regional dynasties and artistic styles.
* **Real Question**: Which Yuan Dynasty art form was included in the intangible cultural heritage list between 2010 and 2015? Provide the name in Chinese.
* **Real Trajectory**: 1. Search for '元代 2010-2015 非物质文化遗产' using native script. 2. Identify the artistic category and filter by the region mentioned in the search snippets. 3. Navigate to the provincial heritage listing page. 4. Extract the exact art form name.
* **Real Answer**: 锦灰堆 (Heaps of Brocade and Ash)
* **Why this demonstrates the capability**: The agent bridges the English query to the Chinese cultural web, where identifying heritages requires navigating region-specific government listings and local encyclopedias that do not have English translations. It tests native-script retrieval and ecosystem-specific navigation.
---
**[Case 3]**
* **Initial Environment**: A Turkish news and entertainment portal containing fragmented information about various TV leads and their career histories.
* **Real Question**: On the CCTV Spring Festival Gala six years after the lead actress's husband's hometown was revealed, which male lead from the same show performed? First, identify the show.
* **Real Trajectory**: 1. Identify the actress and husband via social media snippets in Turkish. 2. Chain the 'Huzhou' hometown clue to a specific marriage year. 3. Calculate the Gala year and search Turkish entertainment archives for lead actor appearances. 4. Verify the performance on the Gala official site.
* **Real Answer**: Love of Parents
* **Why this demonstrates the capability**: The task requires chaining across fragmented Turkish web silos where cultural identifiers (Spring Festival Gala, specific actors) follow local naming conventions. The agent must resolve identity and timeline constraints across language-specific entertainment platforms.

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
