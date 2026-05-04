---
name: exploration-guided-unfamiliar-app-adaptation
description: Use this skill when the user wants data where the agent must first learn an unfamiliar app's layout, handle GUI changes from version updates, or move tasks between mobile apps and websites using exploration. Trigger it for requests like 'the app updated and the button moved, can you find it?', 'make it figure out a new app by looking around first,' 'use this new store like you used the old one,' or 'go to the website and do what you did on the app.' This skill evaluates whether the agent can convert exploration evidence into app-specific navigation priors to overcome cross-version, cross-platform, or entirely new UI environments without relying on stale, memorized habits.
---

# Skill: exploration-guided-unfamiliar-app-adaptation

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to acquire actionable knowledge about an unfamiliar or evolving GUI environment through prior exploration (or cross-platform priors) and use that knowledge to solve downstream tasks. The agent must convert exploration evidence into app-specific navigation logic, generalizing functional intents across visual layout changes (Cross-Version updates), structural shifts (Mobile-to-Web Cross-Platform), and entirely new domain applications, rather than over-relying on generic cross-app assumptions or hard-coded coordinate memory.
* **Dimension Hierarchy**: GUI Perception and Environment Modeling->Environment Understanding->exploration-guided-unfamiliar-app-adaptation

### Real Case
**[Case 1]**
* **Initial Environment**: A messaging-and-payment super-app is open on its home screen. The agent has access to an exploration trace showing how wallet, payment, and subscription-management pages are organized, but the target feature is not exposed from the initial view and the app's information architecture does not mirror common Western payment apps.
* **Real Question**: Please cancel auto-payment service in WeChat.
* **Real Trajectory**: Consult the exploration trace, infer that the relevant path runs through wallet and payment management rather than a generic settings page, navigate to the auto-renewal area, identify the active service, and cancel it.
* **Real Answer**: The auto-payment service is canceled.
* **Why this demonstrates the capability**: The task is difficult precisely because prior experience with other payment apps suggests the wrong generic route. Success depends on mining the provided exploration evidence for developer-specific structure, then translating that evidence into a correct action sequence. This represents the core dynamic of exploration-guided adaptation within a single unfamiliar app.
---
**[Case 2]**
* **Initial Environment**: A shopping application is installed on an Android device. The application has recently undergone a major version update (from v12 to v13), shifting the 'Shopping Cart' from a bottom navigation tab to a top-right header icon and changing the primary 'Check Out' button color from orange to red.
* **Real Question**: I need to pay for the items I added to my cart earlier.
* **Real Trajectory**: Launch the updated application and scan the homepage for the bottom navigation bar. Observe that the 'Cart' tab is missing from the footer, perform a holistic screen scan to identify newly rendered header elements, locate the shopping cart icon at the top-right, and click it to identify the red 'Check Out' button based on semantic label and position despite the visual change.
* **Real Answer**: The checkout page for the current cart is successfully reached.
* **Why this demonstrates the capability**: This extends adaptation to cross-version transferability. The agent must continuously explore and adapt to a specific structural change (repositioning of a primary navigation element) and a visual change (color shift). Success proves the agent relies on active semantic grounding and environment mapping rather than stale coordinate paths memorized from previous versions.
---
**[Case 3]**
* **Initial Environment**: The agent has successfully navigated a mobile shopping app to find a specific kitchen appliance. The user now opens a web browser on a desktop environment pointing to the same retailer's website, which uses a sidebar-centric layout instead of the mobile app's tab-based navigation.
* **Real Question**: Find the same stainless steel blender on the website that we just saw on the phone app.
* **Real Trajectory**: Switch to the Web browser and identify the desktop-specific layout primitives (e.g., top search bar and left-hand category sidebar). Recognize that the mobile 'Bottom Tab' functions are now mapped to the 'Top Nav' on the Web layout, locate the search bar, type 'stainless steel blender', and verify the product details on the rendered web page against the recalled mobile app characteristics.
* **Real Answer**: The product page for the blender is opened in the web browser.
* **Why this demonstrates the capability**: This illustrates cross-platform transferability as a form of environmental adaptation. The agent must resolve divergent interaction patterns between mobile (touch/tabs) and web (sidebar/hover/search) terminals to reach a known goal. It demonstrates the ability to map a functional intent across disparate OS environments by exploring the new structural hierarchy.

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
