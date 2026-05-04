---
name: programmatic-macro-skill-composition
description: Use this when the user needs to solve a complex, multi-step task that involves repetitive sub-goals or can be simplified into a modular routine. Trigger it for requests like 'make a task where the agent learns a shortcut', 'give me plans for adding many different things to a list at once', 'create a problem that needs a repeatable program to solve several similar steps', or 'generate a plan that simplifies many clicks into one command like searching and then buying.'
---

# Skill: programmatic-macro-skill-composition

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to induce and apply programmatic macro-actions from successful trajectories to handle long-horizon agentic tasks more efficiently. This involves identifying repetitive or procedurally linked primitive actions (such as navigation, form-filling, and selection) and abstracting them into verifiable, composable Python-like functions that the planner can invoke as single units within a complex action program. By replacing long sequences of low-level steps with these high-level macro-calls, the agent reduces the planning horizon, minimizes potential cumulative errors, and ensures functional consistency across environments.
* **Dimension Hierarchy**: Open-World Real-World Planning -> Information-Grounded Plan Construction -> programmatic-macro-skill-composition

### Real Case
**[Case 1]**
* **Initial Environment**: A web agent is on the homepage of an e-commerce platform. It has access to primitive tools like 'click', 'fill', and 'scroll', and its goal is to manage address data for a user who has just relocated.
* **Real Question**: I recently moved. Can you change my billing address to '231 Willow Way, Suite 100, Chicago, IL, 60601'? Then, update my shipping address to: 987 Sycamore Circle, Philadelphia, PA, 19102.
* **Real Trajectory**: 1. {action: navigate_to_address_settings('billing'), observation: 'Address form visible'}; 2. {action: update_address_details('231 Willow Way', 'Suite 100', 'Chicago', 'IL', '60601'), observation: 'Billing address updated'}; 3. {action: navigate_to_address_settings('shipping'), observation: 'Address form visible'}; 4. {action: update_address_details('987 Sycamore Circle', '', 'Philadelphia', 'PA', '19102'), observation: 'Shipping address updated'}; 5. {action: send_msg_to_user('Both addresses updated successfully')}
* **Real Answer**: The agent successfully updates both billing and shipping records by invoking higher-level 'address update' macros that wrap approximately 12-15 primitive click and fill actions into distinct, verifiable blocks.
* **Why this demonstrates the capability**: This demonstrates programmatic macro composition because the agent uses high-level functions (navigate_to_settings, update_details) to solve a complex 25+ step sequence in only 5 macro-steps. It proves the agent can manage long-horizon constraints without roaming into redundant exploration, specifically by using a 'verified' routine that ensures the parameters (address strings) are correctly injected into a repeatable workflow.
---
**[Case 2]**
* **Initial Environment**: The agent is at a blank search page for an online catalog. It needs to find and organize multiple heterogeneous items for a shopping list.
* **Real Question**: Add a wireless headphone, a water bottle, a notebook, a ground coffee, and a mug to my shopping cart.
* **Real Trajectory**: 1. {action: search_and_add_to_cart('wireless headphone'), observation: 'Headphone in cart'}; 2. {action: search_and_add_to_cart('water bottle'), observation: 'Bottle in cart'}; 3. {action: search_and_add_to_cart('notebook'), observation: 'Notebook in cart'}; 4. {action: search_and_add_to_cart('ground coffee'), observation: 'Coffee in cart'}; 5. {action: search_and_add_to_cart('mug'), observation: 'Mug in cart'}
* **Real Answer**: All five items are correctly identified and added to the cart using a single repeatable programmatic skill that abstracts the entire search-and-select process.
* **Why this demonstrates the capability**: This demonstrates the efficacy of ASI in scaled-up web activities. Instead of regenerating the same 4-step primitive sequence (click box, type name, enter, click add) five times—which increases the chance of a hallucinated element or ID—the agent uses a single composable skill `search_and_add_to_cart`. This drastically improves the 'steps-to-success' ratio and simplifies the planning task to a simple iteration over the list of item names.

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
