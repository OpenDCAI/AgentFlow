# Document + Data Analysis (Mixed) — Data Synthesis Instructions

## What kind of data are we making?

Training data for a hybrid agent that can handle both document understanding and CSV data analysis. Depending on the seed, it might be working with a parsed PDF (using doc_search and doc_read) or with a directory of CSV files (using ds_inspect_data, ds_read_csv, and ds_run_python). We want QA pairs that are grounded in whichever modality the seed provides.

## How should the agent explore?

First, figure out what you're working with. The seed_path is automatically provided from the seed context.

**If it's a document:**
- Use doc_search with targeted keywords to find relevant sections, tables, figures.
- Use doc_read with a clear extraction goal to pull detailed information from sections.
- Chain across sections: if one section mentions a result, find the methodology section that explains it.
- Focus on content-based clues (captions, labels, headers), not page numbers or section IDs.

**If it's a data directory:**
- Start with ds_inspect_data to understand what CSVs exist and their schemas.
- Use ds_read_csv to preview the data, then ds_run_python for real computation.
- Don't stop at previewing — run actual joins, aggregations, and analyses on the full dataset.

In either case, chain your operations. One tool call should inform the next.

## How to pick the best trajectories?

For documents: pick trajectories with evidence from multiple sections and involving visual or tabular elements. For data: pick trajectories where the agent actually executed code and got concrete results. In both cases, drop trajectories that are repetitive or only scratched the surface.

## What should the final QA look like?

**For document seeds:**
- Questions should require multi-hop reasoning across different parts of the document.
- Answers should be specific facts grounded in extracted evidence.
- Use content-based references, not page numbers.

**For data seeds:**
- Questions should be computation-heavy: joins across multiple tables, statistical tests, ML tasks.
- Answers must come from full-dataset computation, not data previews.
- Format answers precisely: numbers rounded to 2 decimals, or key=value pairs.

Never mix modalities in a single QA — if the seed is a document, the QA should be about the document; if it's data, the QA should be about the data.

## Examples

**Document example:**
**Q:** The annual report's revenue breakdown table lists Region A's contribution. A separate growth chart shows year-over-year changes for the same region. In which year did Region A's growth rate first exceed the company average?
**A:** 2021

**Data example:**
**Q:** Join orders.csv with products.csv on product_id and compute the total revenue per product category. Which category has the highest total revenue? Reply as: category=<name>, revenue=<float>.
**A:** category=Electronics, revenue=15823.50
