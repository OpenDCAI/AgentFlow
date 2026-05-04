---
name: live-web-multimodal-information-seeking
description: Use this skill when the user wants to extract specific factual data that is deeply embedded within complex websites or applications, requiring multi-step stateful interaction. Trigger it for requests like “find the HS code for this product,” “verify the business license on the official registry,” “lookup the hidden ECCN classification,” “check the merchant’s WHOIS details,” or “scan this site for any hidden gambling or phishing content.” This skill is for GUI tasks where the answer cannot be found in surface-level search snippets and requires navigating through dynamically loaded subpages, tabs, and interactive elements to retrieve high-stakes intelligence.
---

# Skill: live-web-multimodal-information-seeking

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to perform goal-directed navigation through live, stateful GUI environments to locate, access, and extract deeply embedded factual information from unstructured or semi-structured sources. Unlike static web scraping, this requires event-driven interaction with dynamic web content (e.g., interacting with DOM-indexed elements, navigating through tabbed interfaces, and bypassing intermediate procedural layers) to retrieve actionable intelligence such as compliance data, risk profiles, or technical specifications buried within professional e-commerce, legal, or logistics portals.
* **Dimension Hierarchy**: Goal-Directed GUI Workflow Execution->Live Information Interaction->live-web-multimodal-information-seeking

### Real Case
**[Case 1]**
* **Initial Environment**: A web browser is open at the Google Search home page. The project requires finding specialized export control data for an electronic component.
* **Real Question**: Search for the DigiKey page for part number HRP-100-12 and identify its Export Control Classification Number (ECCN).
* **Real Trajectory**: 1. In the search box, input 'DigiKey HRP-100-12' and press enter. 2. Click the first organic link to open the product detail page. 3. Scan the product specifications for 'Export' or 'Compliance' sections. 4. Locate the 'Environmental & Export Classifications' expandable table and click it to reveal hidden rows. 5. Identify the 'ECCN' field and extract the value 'EAR99'.
* **Real Answer**: The ECCN for part number HRP-100-12 is EAR99.
* **Why this demonstrates the capability**: This case requires moving beyond surface-level search results to interact with deeply embedded content. The agent must navigate to a specific distributor's product page and execute a state-changing interaction (expanding a hidden classification table) to extract a factual attribute that is not visible in the initial DOM rendering.
---
**[Case 2]**
* **Initial Environment**: A mobile browser is open. The user needs to verify the authenticity of a merchant site to ensure it is not participating in 'transaction laundry' (illicit content hidden on benign sites).
* **Real Question**: Check the 'FitnessGear' e-commerce site to see if it contains any unauthorized links to offshore gambling or adult services in its Terms of Use page.
* **Real Trajectory**: 1. Navigate to the FitnessGear URL. 2. Scroll to the footer and click the 'Terms of Use' link. 3. Use the 'extract structured data' tool to pull all external links mentioned in the legal disclaimer section. 4. Identify a mismatched external URL that redirects to an unlicensed gambling portal. 5. Terminate and report the illicit content finding.
* **Real Answer**: The 'FitnessGear' site contains an unauthorized redirect to an offshore gambling portal within its Terms of Use page.
* **Why this demonstrates the capability**: This demonstrates multimodal information seeking for risk auditing. The agent must perform a deep semantic audit of the site's content consistency, looking for visual and architectural 'mismatches' (e.g., gambling links on a supplement site) that indicate fraudulent behavior, which requires navigating into specific legal subpages.
---
**[Case 3]**
* **Initial Environment**: A logistics tracking portal is open. The user needs to verify a customs declaration audit status for a high-value shipment.
* **Real Question**: Check the clearance status for shipment ID ANT-1922 and extract the customs inspector's comments.
* **Real Trajectory**: 1. Input 'ANT-1922' into the tracking field and click search. 2. Locate the 'Clearance & Customs' tab and click to switch the view. 3. Navigate to the 'Audit Results' sub-link. 4. Scroll to find the 'Inspector Comments' text area and extract the factual string recording any anomalies.
* **Real Answer**: The customs clearance for ANT-1922 is 'Released' with inspector comments: 'All documentation consistent with invoice'.
* **Why this demonstrates the capability**: This interaction involves stateful navigation across a freight platform's dashboard. Success depends on navigating through a multi-layered hierarchy (Tracking -> Clearance Tab -> Audit Detail) to retrieve a terminal factual string that is only rendered after specific event-driven transitions.

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
