# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate n x n 'Language Mismatch' stressors across Prompt, Context, and Target. Synthesize prompts where the Instruction is English, the Context is a high-difficulty language (Japanese/Dutch), and the Target is another distinct language (e.g., Spanish). This forces the agent to demonstrate 'Instruction Disentanglement' and prevents the easy path of defaulting to the prompt's language. For example: 'Using this German case details, provide a summary in Japanese using the following JSON schema.'
  - Deploy Positional Perturbations by reordering the Instruction vs Context sections. Synthesize items where the 'Output Instructions' and 'JSON Schema' are placed BEFORE the context details, and others where they are placed AFTER. This tests the agent's robustness to 'Instruction Order', a critical finding where GPT OSS models showed 20% variance. The instruction should include a command like: 'Ensure you follow the formatting rules regardless of their position in this message.'
  - Embed formal IT technical entities ('IAM', 'Terraform', 'ECR') within the cross-lingual flow to test Domain Isomorphism. Design synthetic contexts involving complex enterprise failures (authentication, policy, connectivity) that must be preserved through the language shifts. This evaluates the 'domain-terminology-translation' overlap, ensuring that 'Multi-architecture images' remain technically accurate in Dutch or Portuguese. Use the IT issue seeds from the PROMPT-ROBUST-ENTERPRISE benchmark format.
  - Incorporate 'NA' (Not Answerable) segments in cross-lingual QnA tasks. Intentionally synthesize questions where the information is missing from the multilingual context documents to test the agent's refusal boundary across languages. The gold answer for these must be a polite refusal in the TARGET language, noting that the information is absent from the SOURCE context. This prevents 'hallucinated grounding' which is exacerbated when multiple languages are involved.
  - Strictly enforce the Tri-Language JSON Trajectory format documenting linguistic transitions. The synthesis rule mandates that the JSON trajectory must explicitly observe the language of each block. First, list Step 1: Detect Prompt Language; Step 2: Detect Context Language; Step 3: Resolve Target Language. This provides a clear audit trail proving the agent is not just guessing but actively managing the linguistic matrix.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
