# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Include explicit 'Variety Cues' in the synthesized prompts to test specialized register-triggering. Formulate instructions that specify the exact register name or social context (e.g., 'Translate this Mandarin into spoken Hong Kong Cantonese'). This ensures the data targets the agent's ability to activate high-fidelity re-mapping. For example: 'As an expert in Hong Kong Traditional Chinese, translate this formal report into colloquial Cantonese speech.'
  - Simulate 'Written-vs-Spoken' Stressors by pairing formal standard inputs with colloquial output mandates. Synthesize prompts where a formal, professionally drafted sentence must be delivered in a 'low-register' street dialect or vice-versa. This forces the agent to demonstrate 'Register Preservation' while simultaneously handling the source's technical jargon. An effective synthesis item would require translating a news headline into a casual social media comment in the target dialect.
  - Utilize 'Orthographical and Phonetic Noise' typical of informal digital communication in the source. Create source texts that use non-standardized spellings, social media shortcuts, or Romanized variants to see if the agent can normalize and translate them. This evaluates 'Robustness to Unstandardized Input,' a critical bottleneck in dialectal pairs. A successful synthesis item would require the agent to decode the phonetic intent before rendering the target standard output.
  - Mandate 'Contrastive directionality' to test asymmetric performance across diglossic pairs. Synthesize task sets where the same meaning is translated from Standard-to-Dialect and Dialect-to-Standard. This allows researchers to identify if the agent's generative capability in the spoken variety matches its comprehension capability. The gold answer for Mandarin-to-Cantonese must include specific colloquial particles that are absent in the Cantonese-to-Mandarin reverse task.
  - Incorporate 'NA' (Not Answerable) segments in cross-dialectal QnA tasks to test the cultural refusal boundary. Intentionally synthesize questions where the information is culturally impossible to map to the target register without a factual violation. The gold answer for these must be a polite refusal in the target dialect, noting the discrepancy. This prevents 'hallucinated grounding' where the model invents dialectal slang that does not exist for a specific standard concept.
  - Require Serialized 'Standard-to-Colloquial' reasoning steps in the JSON trajectory. The synthesis rule mandates that every sample logs: 1) Identification of standard word, 2) Selection of colloquial equivalent, and 3) Syntactic re-ordering. This provides a clear audit trail and proves the agent is acting on the internal diglossic map. Step 1: 'Identified Mandarin "我們"'; Step 2: 'Mapped to Cantonese "我哋"'; Step 3: 'Inserted aspectual particle "咗" to match the spoken rhythm.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
