# RAG Knowledge-Base — Data Synthesis Instructions

## What kind of data are we making?

Training data for a RAG (retrieval-augmented generation) agent. The agent has one tool — rag_search, which retrieves the most relevant text chunks from a pre-built knowledge base (E5 embedding + Faiss index). Given a seed topic or entity, the agent should explore the knowledge base across multiple retrieval hops, gather evidence from different chunks, and produce hard multi-hop QA pairs that require chaining facts from several pieces of retrieved text.

## How should the agent explore?

Start from the seed entity or topic and search the knowledge base. But don't stop after one query — use what you find to formulate follow-up queries. If the first retrieval mentions a related person, search for that person. If a chunk references an event, search for more details about that event.

Build dependency chains: A → B → C → D, where each hop introduces a new fact from a different chunk. The goal is to create trajectories where the final answer requires combining evidence from at least 3 different retrieval results.

Keep in mind:
- Capture hard metadata: exact dates, version numbers, counts, IDs, proper nouns. Vague or general facts make bad QA.
- Don't repeat the same query. If a search wasn't helpful, reformulate with different keywords or approach from a different angle.
- Aim for depth, not breadth. Three focused, chained queries are better than ten shallow ones.

## How to pick the best trajectories?

Pick trajectories where the agent made meaningful progress through chained retrievals. The best trajectories show a clear reasoning path: initial query → discover related entity → search deeper → find connecting fact → synthesize. Drop trajectories that just repeated similar queries or only got shallow, overlapping results.

## What should the final QA look like?

Questions should require multi-hop reasoning — at least 3 hops of evidence chaining. Keep questions concise (2 sentences max). Answers should be specific, verifiable facts: a name, a date, a number, a location. Not a long explanation.

The answer must be grounded in what was actually retrieved during the trajectory. If the evidence doesn't support it, choose a different question.

Good patterns:
- "The person who invented X also contributed to Y. What year was Y first published?"
- "Company A acquired company B in 2015. Company B's founder later joined which organization?"

Bad patterns:
- Single-hop factoid questions ("What is X?")
- Questions answerable from general knowledge without any retrieval
- Vague or opinion-based questions

## Examples

**Q:** What year was the company founded that developed the framework used in the project?
**A:** 2004
