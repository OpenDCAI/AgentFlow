---
name: autonomous-web-data-collection-engineering
description: Use this skill when the user wants to autonomously gather datasets from open web sources by writing and executing scrapers or API harvesters. It is triggered by natural language requests such as 'collect all papers from this year's top AI conference', 'give me a CSV of NBA player stats for 2023', 'download daily stock prices for S&P 500 companies', or 'create a dataset of children's book abstracts from the web'. Use this when the agent needs to plan a data acquisition strategy, identify stable web anchors or API endpoints, and generate executable Python scripts to build a curated dataset from scratch.
---

# Skill: autonomous-web-data-collection-engineering

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to autonomously architect and implement end-to-end data acquisition pipelines from open web sources by translating high-level instructions into executable collection scripts. This involves performing multi-modal environmental research to arbitrate between REST API ingestion and HTML scraping, identifying stable CSS/XPath selectors or endpoint parameters, generating robust error-handling logic for live web volatility, and performing programmatic validation to ensure the collected dataset meets the specified volume, uniqueness, and attribute-fidelity constraints.
* **Dimension Hierarchy**: Data and ML Workflow Engineering->Enterprise Data Workflow Coding->autonomous-web-data-collection-engineering

### Real Case
**[Case 1]**
* **Initial Environment**: A software workspace equipped with a browser tool and a Python runtime. The target is an academic conference website containing archival paper lists and metadata blocks.
* **Real Question**: Collect all papers accepted in NeurIPS 2017 including their titles, author lists, abstracts, and permanent PDF links.
* **Real Trajectory**: Establish a research plan to locate the 2017 accepted paper list. Navigate to the conference proceedings portal and identify the HTML tag structure for paper entries. Draft a development blueprint mapping the title and abstract tags to a structured dictionary. Write a Python script using a networking library to iterate through all identified links, extract the specified attributes, and save the result into a JSON file. Validate the output by checking for empty entries and verifying the count against the expected conference total.
* **Real Answer**: A JSON file containing 679 paper objects, each with a title, author list, abstract, and paper link, faithfully extracted from the conference site.
* **Why this demonstrates the capability**: This case demonstrates the ability to transform a high-level domain request into a physical data artifact. The agent must bridge the gap between unstructured HTML and a structured schema, managing multi-page navigation and content extraction while ensuring the final script is executable and functionally complete.
---
**[Case 2]**
* **Initial Environment**: A server environment with access to financial market data portals and standard data manipulation libraries. The goal is to obtain historical trading data.
* **Real Question**: Collect daily stock information for AAPL between January 1st, 2023, and December 31st, 2023, including Open, High, Low, Close, and Volume.
* **Real Trajectory**: Search for financial data providers that offer historical price APIs or downloadable CSV portals. Identify a stable service endpoint and retrieve the required query parameters for temporal filtering. Implement a Python harvester that handles the request-response loop and sanitizes the numerical values. Execute the harvester to gather the 365-day range, ensuring that corporate actions like stock splits are accounted for in the adjusted volume. Export the final result to a CSV format.
* **Real Answer**: A cleaned CSV file containing the OHLCV data for AAPL for every trading day in 2023.
* **Why this demonstrates the capability**: The task requires selecting the most efficient modality (API vs. scraping) for financial data. It tests the degree of scientific precision required to handle time-series data, ensuring the agent can correctly parameterize queries and validate the temporal continuity of the resulting dataset.
---
**[Case 3]**
* **Initial Environment**: A development container targeting professional sports league repositories. The environment provides access to official league stats websites and documentation.
* **Real Question**: Collect all regular season statistics for the Los Angeles Lakers for the 2023-2024 season, ensuring every player's points, assists, and rebounds are captured.
* **Real Trajectory**: Navigate to the official league statistics page and locate the team roster for the specified season. Inspect the backend network requests to see if the data is available via a hidden REST API or must be parsed from table elements. Define a schema for the team stats and write an extraction script that iterates through the player profiles. Execute the script while handling potential anti-bot headers and rate limits. Cross-validate the generated data with the season summary to ensure no players were missed.
* **Real Answer**: A comprehensive player-level dataset for the LA Lakers 2023-24 season, verified for completeness and accuracy against the source site.
* **Why this demonstrates the capability**: This demonstrates 'Autonomous Engineering' by requiring the agent to navigate a dense, potentially dynamic sports portal. The agent must maintain state across player folders and the main team roster, ensuring robust data mapping even when player profiles use inconsistent layout patterns.

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
