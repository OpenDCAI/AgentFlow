---
name: execution-feedback-driven-iterative-refinement
description: Use this when the user wants to automate technical or tool-use workflows that require running code or invoking APIs, analyzing error logs or feedback, and fixing the logic step-by-step. Trigger it for requests like 'debug this API call using feedback', 'iteratively refine this script based on scores', 'solve this task and correct any errors found in the tool response', or 'improve the tool plan based on execution failures.' It is particularly useful for System 2 reasoning where trial-and-error is mandatory for success.
---

# Skill: execution-feedback-driven-iterative-refinement

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to plan, generate, and execute an action sequence within a closed-loop environment, subsequently performing a dynamic 'Error -> Reflection -> Correction' cycle based on execution feedback (such as compiler errors, API failure logs, or numeric optimization scores). This capability encompasses meta-verification of reasoning trajectories to ensure step-wise accuracy and the adaptive discovery of hidden environment parameters through interactive tool probing.
* **Dimension Hierarchy**: Open-World Real-World Planning -> Technical Research and Optimization -> execution-feedback-driven-iterative-refinement

### Real Case
**[Case 1]**
* **Initial Environment**: A user order-retrieval system with two APIs: one for listing order history (get_user_orders) and another for fetching details (get_order_details). The documentation is incomplete, missing the specific user-identification parameter for the history list and utilizing an outdated parameter name for the details tool.
* **Real Question**: Can you fetch the details of my recent orders? I need to know the products, status, and delivery date.
* **Real Trajectory**: 1. [Tool Planning] Attempt to fetch history using `get_user_orders()`. 2. [Observation] Receive error: 'Input parameters missing; provide user ID'. 3. [Reflection] Identify the missing constraint and decide to provide `user_id`. 4. [Tool Invocation] Execute `get_user_orders(user_id='123')`. 5. [Observation] Success, found Order #456. 6. [Tool Invoation] Execute `get_order_details(is_id='456')` based on documentation. 7. [Observation] Error: 'Invalid parameter is_id'. 8. [Reflection] Hypothesize the parameter name evolved and try `order_id` as an integer. 9. [Tool Invocation] Execute `get_order_details(order_id=456)`. 10. [Observation] Success, retrieved status 'Shipped'.
* **Real Answer**: Your recent order (ID: 456) for the Apple iPhone 12 is currently 'Shipped'.
* **Why this demonstrates the capability**: This case demonstrates iterative refinement because the agent encountered multiple execution failures (missing parameters and outdated naming) and used each specific error message as a 'learning signal' to adjust its tool invocation strategy. It proves the agent can navigate production environments with imperfect documentation by applying a deliberate reflection loop rather than simply giving up.
---
**[Case 2]**
* **Initial Environment**: A weather forecasting tool `get_weather_forecast` that requires a specific date format. The user provided the date in a natural language format ('Christmas Day') which is not recognized by the backend server.
* **Real Question**: What is the weather forecast for London on Christmas Day 2024?
* **Real Trajectory**: 1. [Thought] I will query the weather for London on December 25, 2024. 2. [Action] `get_weather_forecast(city='London', date='December 25, 2024')`. 3. [Observation] 'Invalid date format. Use YYYY-MM-DD format'. 4. [Reflection] The tool feedback explicitly specifies the YYYY-MM-DD pattern. I must convert 'Christmas Day' to '2024-12-25'. 5. [Action] `get_weather_forecast(city='London', date='2024-12-25')`. 6. [Observation] Success: 'Light Snow, 2°C'.
* **Real Answer**: On Christmas Day 2024, London will experience light snow with a temperature of 2°C.
* **Why this demonstrates the capability**: This demonstrates execution-feedback-driven refinement by showing an 'Error -> Reflection -> Correction' paradigm. The agent recognizes its initial invocation failed due to a format constraint provided in the feedback and re-invokes the tool with corrected parameters to achieve the goal.

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
