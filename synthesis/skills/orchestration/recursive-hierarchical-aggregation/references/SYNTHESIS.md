# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate the overarching prompt as a 'High-Entropy Volume Challenge' that explicitly demands parsing massive scale, such as 'Analyze our entire 2024 global security posture utilizing these 5,000 incident reports' or 'Audit every single component on this dense blueprint'. Deliberately abstain from mentioning terms like 'chunking', 'summarize in pieces', or 'use sub-agents', mandating the orchestrator autonomously recognize the scale forcing a multi-agent tree architecture. This setup ensures simple flat-prompting fails dramatically while intelligent spatial or semantic partitioning thrives.
  - Incorporate a 'Resource Format Diversity Trap' ensuring the monolithic dataset natively spans heavily incongruent formats, such as combining raw string server logs, binary high-resolution images, and strict CSV financial reports. This explicitly forces the model to not only partition the sheer volume but intimately evaluate each chunk to dispatch a specifically tuned expert (e.g., text-reader vs. vision model) before any aggregation logic begins. This rigorously tests the 'Specialist Consultation' mapping integrated within the hierarchy.
  - Design a 'Needle-in-the-Haystack Global Metric' where fulfilling the high-level demand requires explicitly capturing and tallying a micro-metric perfectly scattered across all hidden sub-chunks. Phrase the request alongside constraints like 'Calculate the exact overall carbon reduction tonnage across all these facility readouts', compelling the orchestrator to purposefully extract precise integer values from every separate leaf summary to calculate the final synthesis total. This ensures the brutal reduction phase retains high-fidelity, grounded operational data rather than washing away nuances into broad storytelling.
  - Deploy robust 'Layman Compression Cues' leveraging non-technical directives like 'get a 10,000-foot view', 'boil this ocean of data down to one page', or 'don't let any detail fall through the cracks while giving me the tl;dr'. This tests the orchestrator's capability to successfully map an extremely casual executive request into a rigorous, technically sound recursive reduction tree. To elevate difficulty, supply a 'Global Index' artifact the orchestrator must consult to strictly enforce 100% data coverage during the parsing setup phase.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
