---
name: hierarchical and nested data structural reasoning
description: Use this skill when the data is stored in complex, multi-layered formats such as HDF5, NetCDF, AnnData (.h5ad), or highly nested MultiIndex tables. It is especially critical for 'MissionBio', 'ParseBio', or 'H5' file formats where columns are not immediately visible and must be discovered through attribute navigation. Trigger it for requests like 'find the metric hiding in the metadata layers,' 'navigate the tiered attributes of this scientific file,' or 'extract values from a container with linked observation and variable tables.' Plain-language examples: 'Look inside the different parts of this h5ad file,' 'figure out which layer of the data tree has the counts,' or 'check the metadata properties before you read the main table.'
---

# Skill: hierarchical and nested data structural reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability involves the navigation and semantic grounding of datasets with deep hierarchical architectures and relational-component linkages, including scientific multi-component containers (e.g., AnnData, HDF5, NetCDF) and nested tabular structures (e.g., Pandas MultiIndex). It requires the agent to perform absolute path resolution, recursive attribute traversal, and cross-component alignment—where the agent must map linguistic entities to specific partitions, metadata attributes (e.g., scale factors/units), or linked observation-variable tables within a unified storage object.
* **Dimension Hierarchy**: Data Grounding->Data Retrieval & Semantic Grounding->hierarchical and nested data structural reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A scientific multi-component container file (AnnData .h5ad) is provided in the sandbox. The data is partitioned into high-dimensional matrix observations (`.X`), observation metadata (`.obs`), and variable metadata (`.var`).
* **Real Question**: For the 'ParseBio' platform data subset, what is the mean total count of transcripts per cell in the 'Monocyte' population?
* **Real Trajectory**: The agent loads the .h5ad file using the anndata library and identifies that the target labels 'ParseBio' and 'Monocyte' reside in the `.obs` dataframe, not the main matrix. It executes code to generate a boolean mask by filtering `.obs['platform'] == 'ParseBio'` and `.obs['cell_type'] == 'Monocyte'`. Using this mask, it subsets the primary measurement matrix `.X`, sums the transcript counts along the cell axis, and computes the final mean value.
* **Real Answer**: 1452.3
* **Why this demonstrates the capability**: This case demonstrates structural reasoning by requiring the agent to perform relational mapping between a metadata table (.obs) and a linked measurement matrix (.X). Instead of a simple query, the agent must treat the hierarchical object as a partitioned system where observations and measurements are stored in different internal attributes that must be logically combined.
---
**[Case 2]**
* **Initial Environment**: A scientific HDF5 dataset contains a hierarchical tree where datasets are nested under multiple levels of groups. For example, a root group contains 'measurements,' which contains 'sensor_01,' which finally holds a dataset named 'temperature_reading' with associated 'units' and 'scale_factor' attributes.
* **Real Question**: Extract the sensor 01 temperature reading and apply the scale factor mentioned in the file properties.
* **Real Trajectory**: Load the file using the h5py library and recursively list all group keys to understand the internal directory structure. Identify that the target data resides at the absolute path '/measurements/sensor_01/temperature_reading'. Retrieve the dataset and specifically check the '.attrs' dictionary for 'scale_factor'. Multiply the raw array by the attribute value to normalize the result before returning the final observation.
* **Real Answer**: Array of normalized temperature values [e.g., 298.15, 298.20...]
* **Why this demonstrates the capability**: The agent must navigate a physical folder-like hierarchy within a single file to find the correct data path. Success requires not just finding the data but also grounding the analytical operation in node-level metadata (the scale factor), which is characteristic of scientific data formats like HDF5.
---
**[Case 3]**
* **Initial Environment**: A CSV dataset representing national labor statistics is provided. The first header row contains broad sectors like 'Employed' and 'Unemployed', while the second header row defines sub-categories such as 'Agriculture', 'Non-agriculture', and 'Total'.
* **Real Question**: Match the year where the employment in agriculture was the highest and state its corresponding total employed population in that year.
* **Real Trajectory**: The agent identifies that the 'Agriculture' column is nested under the 'Employed' major category by inspecting the first two rows of the dataframe. It uses MultiIndex slicing to isolate the ('Employed', 'Agriculture') column and identifies the maximum value across all years. Once the year is identified, it retrieves the ('Employed', 'Total') value for that same index to satisfy the multi-step request.
* **Real Answer**: Year: 1955; Total Employed Population: 62,170
* **Why this demonstrates the capability**: It demonstrates structural navigation of MultiIndex (hierarchical) tables. The agent must resolve name collisions (like 'Total' appearing under different parents) by recognizing the parent-child relationship between header levels.

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
