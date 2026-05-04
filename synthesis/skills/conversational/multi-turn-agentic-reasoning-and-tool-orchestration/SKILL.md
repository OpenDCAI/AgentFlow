---
name: multi-turn-agentic-reasoning-and-tool-orchestration
description: Use this skill when the agent must use external tools (APIs, searching, or MCP servers) to solve a task, particularly when the request requires multiple steps or a 'plan' to be successful. It is triggered by requests like 'get the news and then summarize it', 'check my order and then tell me if I can return it', 'book a flight and then find a hotel nearby', or 'solve this multi-part problem using your tools'. Everyday examples include: 'make a list of things to do and start with the first one', 'what are the steps to fix this account?', 'can you look up these three things for me?', and 'execute the plan we talked about.'
---

# Skill: multi-turn-agentic-reasoning-and-tool-orchestration

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to execute complex agentic workflows using a Multi-Step Planning and Reasoning (Pre-Act) architecture combined with Conversational ReAct (CRA). The agent generates a structured execution plan (Next Steps) and a summary of history (Previous Steps) before every tool call, allowing it to perform long-term planning, sequential decision-making, and incremental plan refinement based on real-world tool observations or failures.
* **Dimension Hierarchy**: Conversational Effectiveness->Task-oriented Dialogue Control->multi-turn-agentic-reasoning-and-tool-orchestration

### Real Case
**[Case 1]**
* **Initial Environment**: A conversational environment with a 'get_news_headlines' tool. The user asks for a simple sequential task: fetch news and provide a tidy list.
* **Real Question**: Can you tell me the latest news headlines for the United States?
* **Real Trajectory**: 1. [Thought]: Previous Steps: NA. Next Steps: 1. Invoke get_news_headlines(country='United States'). 2. Provide the final answer with headlines. 2. [Action]: get_news_headlines(country='United States'). 3. [Observation]: {'headlines': ['Policy update A', 'Weather event B', 'Market shift C']}. 4. [Thought]: Previous Steps: Invoked get_news_headlines for United States. Next Steps: 1. Provide the top headlines to the user. 5. [Action]: Final Answer ('Here are the headlines...').
* **Real Answer**: Here are the latest news headlines for the United States: 1. Policy update A, 2. Weather event B, 3. Market shift C.
* **Why this demonstrates the capability**: This case demonstrates 'Pre-Act' multi-step planning. Instead of just jumping to the first tool call, the agent explicitly maps out the entire sequence—fetching the news then explaining it—ensuring it remains aware of the end goal throughout the interaction.
---
**[Case 2]**
* **Initial Environment**: A multi-server environment managing a quarterly compliance update workflow involving document retrieval and content editing tools.
* **Real Question**: I need to understand the current policy structure, update all mentions of 'Q3 2024' to 'Q1 2025', and add footnotes to the end.
* **Real Trajectory**: 1. [Thought]: Previous Steps: NA. Next Steps: 1. Get document outline. 2. Perform search and replace. 3. Append footnotes. 2. [Action]: get_document_outline(). 3. [Observation]: Outline retrieved. 4. [Thought]: Previous Steps: Got outline. Next Steps: 1. Search and replace 'Q3 2024' with 'Q1 2025'. 2. Append footnotes. 5. [Action]: search_and_replace(...). 6. [Observation]: Replaced 14 instances. 7. [Thought]: Previous Steps: Got outline and updated dates. Next Steps: 1. Add footnotes to last 3 sections. 8. [Action]: add_footnote(...). 9. [Final Answer]: Task complete.
* **Real Answer**: I have updated your policy document by first analyzing the structure, replacing 14 date occurrences, and adding the required footnotes.
* **Why this demonstrates the capability**: Demonstrates complex multi-tool orchestration through incremental plan refinement. The agent tracks dependencies (knowing which sections to footnote requires the outline from step 1) and maintains the mission-critical sequence without losing context.
---
**[Case 3]**
* **Initial Environment**: An environment with 'Weather' and 'Travel' tools. The user asks for a 'Crypto' price, which is outside the available toolset capability.
* **Real Question**: What is the current price of Ethereum on the OKX exchange?
* **Real Trajectory**: 1. [Thought]: The user wants crypto market data. Next Steps: 1. Check available tools. 2. Realize no crypto tool exists. 3. Inform user of limitation. 2. [Action]: Final Answer (Refusal).
* **Real Answer**: I don't have access to tools that can check cryptocurrency prices like Ethereum at the moment.
* **Why this demonstrates the capability**: Demonstrates 'Irrelevance Mapping' and resilience to hallucination. By planning to check its toolset before acting, the agent avoids calling an unrelated tool (like weather) or making up a price, proving its reasoning is grounded in its actual capabilities.

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
