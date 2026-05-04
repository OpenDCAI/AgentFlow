# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Create contextually ambiguous terms heavily dependent on juxtaposed design layouts. Integrate synthetic queries centered on words or raw numbers possessing divergent dictionary definitions until interpreted linearly against their local visual counterparts (e.g., currency icons next to digits versus physical sizing formats). Expose the capability to explicitly engage visual reasoning blocks.
  - Inject 'Phonological and Orthographical Noise' into paired source text descriptions. Synthesize inputs that contain common typing slips (e.g., 'snickers' for 'sneakers', 'shrit' for 'shirt') alongside an image that reveals the true object. Force the agent into a 'Visual-Correction' mode where the gold translation maps to the image's reality, not the prompt's spelling mistake.
  - Deploy digital colloquial boundaries stressing internet platform dynamics. Insert test sets framed inside visual media applications like messaging apps or social networks comprising overlapping UI widgets, memes, emojis, or fragmented syntax blocks. Ensure the request strictly requires extracting modern communication cadence through picture analysis.
  - Utilize damaged, fragmented historical visuals triggering architectural artifact logic. Force scenarios employing scans of ancient manuscripts, carved monument slabs, or low-quality paper records exposing missing sections or archaic shorthand abbreviations. Verify the extraction honors material limits and integrates era-appropriate terminology matching the source material architecture.
  - Establish rigid Tri-Stage Output formats governing the entire sequence loop. Configure instructions strictly commanding the generation of distinct <recognize>, then <think>, wrapping finally into <translate> structural steps. Enforce formatting boundaries allowing validation scripts to effectively grade the discrete translation mechanisms.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
