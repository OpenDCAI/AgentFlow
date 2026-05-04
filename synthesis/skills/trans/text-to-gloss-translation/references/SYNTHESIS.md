# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate 'Gloss-Targeted' translation prompts with explicit linguistic constraints. Synthesize the request using clear layman terms like 'convert to sign language labels' or 'write the gloss,' but follow it with a strict professional mandate to 'use only infinitive verbs and omit articles.' This forces the agent to demonstrate the specialized reductionist logic of T2G. For example: 'Translate this sentence into Bangla Sign Language labels (gloss). Rule: Use infinitives and remove words like "is", "the", or "to".'
  - Deploy 'Morphologically Rich' source sentences to test lemmatization robustness. Synthesize input sentences containing complex tenses, such as 'I had been singing' or 'they will have worked,' to force the agent into a deep lemmatization recovery. The gold answer must show the agent successfully mapping these back to 'I SING' or 'THEY WORK.' This evaluates the agent's ability to maintain semantic intent while purging the spoken-language-only tense markers.
  - Incorporate 'Topic-First' reordering tasks within the synthesis prompt. Design questions that provide a standard SVO sentence and command the agent to 'put the main object or location first' as per sign-language syntax. This tests the agent's ability to manipulate word order for visual-spatial efficiency. For instance: 'Convert to gloss and place the location at the start: "The teacher is in the classroom."'
  - Utilize 'High-Noise' functional environments containing multiple prepositions and articles. Synthesize sentences like 'A bird is sitting on a branch of a very tall tree' to test the agent's purge limits. The gold answer should reflect a highly compact label sequence like 'BIRD TALL TREE BRANCH SIT.' This strictly evaluates the difference between a fluent spoken translation and a concept-aligned sign gloss.
  - Serialize a 'Source-to-Label' reasoning path in the JSON trajectory. The synthesis rule mandates that the agent explicitly records: 1) Identification of inflected verbs, 2) Mapping to infinitives, and 3) Omission of functional particles. This provides the audit trail required and proves the agent is not just doing random word-dropping. Step 1: 'Identified inflected verb "গাইতে"'; Step 2: 'Recovered infinitive "গাওয়া"'; Step 3: 'Removed particle "তে" to satisfy gloss constraints.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
