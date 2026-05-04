# Document Understanding — Data Synthesis Instructions

## What kind of data are we making?

Training data for a document QA agent that works with parsed PDF documents. The agent has two tools — doc_search (keyword search across headings, paragraphs, tables, and image captions) and doc_read (read specific sections using a visual language model that can process both text and images). We want hard, multi-hop, visual-grounded QA pairs that require evidence from multiple pages and involve charts, figures, or tables.

## How should the agent explore?

You'll get an XML outline of the document as your starting point. The seed_path is automatically provided from the seed — you don't need to specify it when calling tools.

Here's how to explore effectively:
- Use doc_search with specific keywords to find visual elements: try terms like "Figure", "Chart", "Table", "panel", "footnote", "legend".
- Use doc_read to extract detailed information from promising sections. Always set a clear goal for what you want to extract.
- Chain across pages: if you find a chart on one page, search for its discussion or data source on other pages. If a table references a footnote, find and read that footnote.
- Collect content-based clues — captions, axis labels, legend items, headers. These are what make questions answerable without referencing page numbers.
- Don't use page numbers, section IDs, or explicit figure/table numbers in your exploration notes. We need content-based references.
- Avoid broad document-level counting ("how many pages..."), word-frequency questions, or repeating the same search query.

## How to pick the best trajectories?

Prefer trajectories with strong evidence quality across multiple pages. The ideal trajectory touches at least 2 different pages, involves at least one visual element (chart, figure, or table), and has clear non-redundant evidence. Drop trajectories that just searched the same thing repeatedly or only read one section.

## What should the final QA look like?

Every QA must satisfy ALL of these constraints simultaneously:
- **Multi-page**: evidence from at least 2 different pages
- **Visual-grounded**: involves charts, figures, tables, or page layouts
- **Multi-hop**: at least 2 reasoning hops (e.g., cross-reference + computation, footnote + chart reading)

Questions should be concise (5 sentences max), and answers should be specific facts — names, dates, numbers. Not paragraphs.

Use content-based clues to identify evidence in the question. Say "the demographics table showing global workforce percentages" instead of "Table 3 on page 5".

Good patterns:
- Text claim + chart verification ("The report states X. According to the chart showing Y, is this consistent?")
- Table + chart consistency ("Compare the figures in the annual results table with the time-series chart...")
- Footnote-constrained mapping ("A footnote indicates one year's data was restated. In the corresponding chart...")
- Layout comparison ("On the page containing the multi-panel figure, how many tables are visible?")

Bad patterns:
- Single-hop lookups ("What does Figure 3 show?")
- Questions with explicit page/section/figure numbers
- Broad counting questions ("How many pages mention revenue?")
- Anything where you'd have to guess or hallucinate the answer

If the trajectory doesn't support all three constraints, pick a different question. Never fabricate evidence.

## Examples

**Q:** A demographics table gives the percentage of women in the global workforce as of December 31, 2020, and a separate board composition graphic gives the percentage of women on the board for the same date. What is the percentage-point difference between these two percentages?
**A:** 16.3 percentage points

**Q:** In the annual results table, a footnote indicates one year's figures were restated. In the time-series chart covering the same span, which year corresponds to the restated figures?
**A:** 2019

**Q:** Locate the page that contains the only multi-panel figure with panels labeled (a) and (b). On that page, how many distinct tables are visible, and on the immediately following page, how many distinct tables are visible? What is the difference?
**A:** 1
