---
name: integration-aware-information-extraction-and-database-population
description: Use this skill when the user wants to populate or enrich an existing relational database using information extracted from raw text documents. Trigger it for requests like 'extract information from these news reports into my SQL database', 'add new rows to the movies table based on this biography', 'fill in missing data in my table using the provided text', or 'create new columns from the attached articles'. This skill is specifically for tasks that require the agent to understand a database schema and ensure that data extracted from unstructured sources follows formatting, granularity, and integrity constraints.
---

# Skill: integration-aware-information-extraction-and-database-population

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to autonomously enrich relational databases by extracting structured information from unstructured text while maintaining strict adherence to the target schema, data granularity, and referential integrity. This involves identifying extraction targets through schema analysis, resolving semantic ambiguities by querying existing database samples, and orchestrating a multi-step pipeline of information extraction (e.g., entity recognition, attribute extraction) followed by data integration logic (e.g., normalization, entity linking, and primary/foreign key management).
* **Dimension Hierarchy**: Data and ML Workflow Engineering->Enterprise Data Workflow Coding->integration-aware-information-extraction-and-database-population

### Real Case
**[Case 1]**
* **Initial Environment**: A relational database contains three tables: 'Movie', 'Actor', and 'Character'. The 'Movie' table has columns for title, release date, and gross; the 'Actor' table tracks names and birthplaces; the 'Character' table links actors to movies via foreign keys ActorID and MovieID. A long text document providing a detailed production history of recent superhero films is provided.
* **Real Question**: Given the document about a new movie, update its information into the database across all relevant tables.
* **Real Trajectory**: 1. Inspect the database schema to identify required attributes for a new movie entry. 2. Extract the movie title, release date, budget, and gross from the text using attribute extraction. 3. Identify all mentioned actors and their roles, then check the 'Actor' table to see if they already exist. 4. For new actors, extract birthplace and birth date, then generate new ActorIDs. 5. Normalize extraction results (e.g., converting '$714 million' to an integer) and insert rows into the 'Movie' and 'Actor' tables. 6. Map characters to the newly created MovieID and ActorID, then insert linking rows into the 'Character' table.
* **Real Answer**: The database is updated with a new movie row, multiple new actor entries with specific biographical details, and several character-linking rows that respect foreign key constraints.
* **Why this demonstrates the capability**: This demonstrates the capability because it moves beyond simple extraction. The agent must handle dynamic schema adaptation across multiple tables, enforce foreign key integrity during integration, and normalize raw text strings into database-compatible formats.
---
**[Case 2]**
* **Initial Environment**: The environment includes an 'Earthquakes' table with columns: 'Year', 'Magnitude', 'Location', 'Deaths', and 'Injuries'. Some rows contain missing values (NULL) for the impact metrics. A collection of recent news reports on global seismology is available.
* **Real Question**: I am maintaining a database of the largest earthquakes. Given the latest document of the Peru earthquake, please update the numbers of deaths and injuries for the existing entry in the database.
* **Real Trajectory**: 1. Identify the 'Peru 2019' earthquake row in the existing table to determine the target for infilling. 2. Search the news text for numerical values describing casualties specifically linked to that event. 3. Extract '2' for deaths and '30' for injuries. 4. Verify that the extracted values correspond to the correct semantic granularity (e.g., ensuring local injuries are not confused with regional totals). 5. Update the existing row using a data infilling tool that binds the information to the specific record uniquely identified by its primary key.
* **Real Answer**: The existing 'Peru 2019' row in the Earthquakes table now correctly contains '2' in the Deaths column and '30' in the Injuries column.
* **Why this demonstrates the capability**: This illustrates 'Data Infilling' where the agent must perform entity linking to bind extracted facts to existing structured records. It requires precision in locating the correct row and ensuring the extracted numbers are semantically aligned with the target columns.

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
