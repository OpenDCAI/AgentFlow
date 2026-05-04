# Web Deep Research — Data Synthesis Instructions

## What kind of data are we making?

We're building training data for a web research agent. The agent has two tools — web_search (batch keyword search) and web_visit (visit a URL and extract content toward a goal). Given a seed topic, it should explore the internet across multiple hops, gather evidence from different sources, and eventually produce a hard multi-hop QA pair that can't be answered without chaining facts from several pages.

## How should the agent explore?

Start from the seed topic and branch outward. Don't just search once and stop — dig deeper. If the first search gives you a person's name, search that person next; if a page mentions an organization, visit the org's page. Build dependency chains like A → B → C → D, where each hop adds a new piece of evidence.

A few things to keep in mind during exploration:
- Use web_visit at least once per trajectory — we need page-level evidence, not just search snippets.
- Capture hard metadata: exact dates, version numbers, numeric counts, IDs. Vague facts make bad QA.
- Don't loop on the same query. If a search didn't help, reformulate or move on.
- Aim for at least 3 hops of reasoning depth before stopping.

## How to pick the best trajectories?

After sampling multiple exploration paths, pick the ones that have the richest and most diverse evidence. Prefer trajectories where the agent actually visited pages and extracted non-trivial facts. Drop trajectories that are mostly redundant search results or shallow single-hop lookups.

## What should the final QA look like?

The question should require multi-hop reasoning — at least 3 hops. It should be concise (no more than 5 sentences), and the answer should be a specific fact: a name, a date, a number, a location. Not a paragraph.

Make sure the answer is actually grounded in the trajectory evidence. If the trajectory doesn't support it, pick a different question — never hallucinate an answer.

Good patterns:
- "Who founded the company that acquired X, and in what year was that company itself acquired by Y?"
- "The framework used in project A was developed by team B. What university did team B's lead graduate from?"

Bad patterns:
- Single-hop lookups ("What is X?")
- Questions answerable from search snippets alone without visiting any page
- Vague or opinion-based questions

## Examples

**Q:** The Python web framework Django was originally developed at a newspaper. What is the name of that newspaper, and in what year did it release Django as open source?
**A:** Lawrence Journal-World; 2005

**Q:** The creator of Linux also created a version control system. That system was originally built to manage the Linux kernel source code. How many days did it take him to build the first working version?
**A:** About 10 days
