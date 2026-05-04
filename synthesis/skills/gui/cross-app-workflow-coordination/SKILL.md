---
name: cross-app-workflow-coordination
description: Use this skill when the task involves moving data or state between different applications, or populating a form based on an external document. Trigger it for requests like 'remember the name from the previous screen,' 'help me apply for this job using my resume,' 'keep a note of that price for later,' or 'match the info from this file to the boxes in the app.' This skill is for GUI tasks requiring a chain of memory where information is extracted from one source (e.g., a PDF resume, a map result) and utilized in a distinct destination (e.g., a web application form, a messaging app).
---

# Skill: cross-app-workflow-coordination

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to decompose complex instructions into cross-application subtasks and execute them by explicitly managing short-term and long-term memory. The agent must perform action-result abstraction to track immediate navigation progress and information distillation to extract, store, and share task-critical variables—such as abstract entity details, unstructured resume metadata, or search results—across different application boundaries and heterogeneous input widgets (like date-pickers and dropdowns).
* **Dimension Hierarchy**: Goal-Directed GUI Workflow Execution->Verified Task Completion->cross-app-workflow-coordination

### Real Case
**[Case 1]**
* **Initial Environment**: A mobile device home screen with LinkedIn and Microsoft Word installed. The LinkedIn application is logged in but not currently running.
* **Real Question**: Use the LinkedIn app to find a mobile app developer job, and then record the company name using Microsoft Word.
* **Real Trajectory**: 1. Launch LinkedIn and process the search query item for 'mobile app developer'. 2. Identify the job listing for 'Apex Systems'. 3. Extract the company name 'Apex Systems' into long-term memory. 4. Press the Home button, launch Word, and create a new document. 5. Retrieve the company name from memory and type 'Apex Systems'.
* **Real Answer**: A Microsoft Word document contains the text 'Apex Systems'.
* **Why this demonstrates the capability**: Success requires the agent to not only navigate across apps but to selectively extract a specific textual variable and maintain its persistence during the transition between the browsing state and the writing state without losing the context.
---
**[Case 2]**
* **Initial Environment**: A mobile device with Waze Navigation and Uber installed. The device is currently on the home screen.
* **Real Question**: Locate a nearby gym using Waze Navigation and then book a ride through Uber to get there.
* **Real Trajectory**: 1. Open Waze Navigation and search for 'gym'. 2. Select a nearby result, 'Trojan Crossfit'. 3. Observe the details and store 'Trojan Crossfit' into memory. 4. Exit Waze and open the Uber app. 5. In the Uber destination field, recall the name 'Trojan Crossfit' and input it.
* **Real Answer**: An Uber ride is initiated with 'Trojan Crossfit' as the destination.
* **Why this demonstrates the capability**: This interaction involves a 'Chain-of-Memory' where the output of a navigation search must be converted into a structured knowledge seed for a ride-hailing application, bridging two disjointed application environments.
---
**[Case 3]**
* **Initial Environment**: A web browser is open on a 'Startup Funding Application' page. The user has provided an external plan document containing the company's founding date, business stage, and funding amount.
* **Real Question**: Please fill out the startup funding application using the details in my company profile.
* **Real Trajectory**: 1. Scan the company profile for 'Business Stage'. 2. Switch focus to the browser, locate the 'Business Stage' dropdown on the form, and expand it to select 'Seed'. 3. Locate the 'Funding Amount' field and retrieve '500000' from memory to type. 4. Switch to date selection for founding date. 5. Verify all entered data against the document memory and submit.
* **Real Answer**: The funding application is successfully submitted with all fields populated from the document.
* **Why this demonstrates the capability**: This demonstrates multimodal info-transfer across applications because the agent must align semantic concepts from a distinct source document with heterogeneous, complex GUI widgets (dropdowns, inputs) on a destination web form, actively maintaining the memory abstraction across the workflow.

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
