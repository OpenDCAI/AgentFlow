---
name: cross-lingual-instruction-consistency
description: Use this skill when the user provides translation tasks where the instruction, the source text, and the target output involve different languages (n x n configurations). Trigger it for layman requests like 'English prompt for Spanish text to Japanese,' 'mismatched languages between the ask and the content,' or 'test if the translator gets confused when the command is in English but the text is in German and the answer should be in Dutch.'
---

# Skill: cross-lingual-instruction-consistency

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to maintain task-alignment and meaning-preserving transfer when the meta-instruction (prompt), source context, and target output belong to different linguistic domains (n x n language permutations). This involves correctly disentangling the 'instruction language' from the 'context language' to ensure that the agent follows the requested target language constraint without succumbing to source-language leakage or prompt-language default bias.
* **Dimension Hierarchy**: Robustness to Imperfect or Misleading Instructions->Instruction Disentanglement->cross-lingual-instruction-consistency

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent is provided with an English meta-instruction (prompt) and a contextual input regarding an IT 'Terraform state lock' issue that has been translated into German. The user-defined goal is to receive the result in Dutch (NL).
* **Real Question**: You are given the following case that needs to be summarized. Be sure to include the sections Main Problem, Key Events, and Final Resolution. Output in the following JSON format in Dutch: 'Terraform apply schlägt fehl, da die Statussperre nicht freigegeben wurde...'
* **Real Trajectory**: The agent identifies the English prompt as the controlling 'instruction'. It recognizes the German 'Source' material and suppresses the urge to output in English or German. It maps the German segments to Dutch equivalents, ensuring 'Main Problem' becomes 'Hoofdprobleem' and 'Key Events' becomes 'Belangrijkste gebeurtenissen', while correctly decoding the IT jargon 'force-unlock'.
* **Real Answer**: { "Hoofdprobleem": "Terraform apply mislukt door ontbrekende ontgrendeling van de state lock.", "Belangrijkste gebeurtenissen": ["Deployments geblokkeerd door proces lock", "Root cause: zwevende lock na onderbroken proces"], "Final Resolution": "'terraform force-unlock' gebruikt om de lock handmatig vrij te geven." }
* **Why this demonstrates the capability**: This case demonstrates the n x n cross-lingual consistency required in enterprise workflows. The agent must manage three distinct language states (EN, DE, NL) simultaneously. Failure would manifest as 'language leakage' where the agent accidentally responds in the same language as the context (German) or the instruction (English), precisely the robustness drop highlighted in contemporary enterprise benchmarks.
---
**[Case 2]**
* **Initial Environment**: A translation agent processes a chat transcript translated into Japanese concerning an AWS ECR image scan failure. The instruction is in English, and the requested output is Brazilian Portuguese (PT-BR).
* **Real Question**: Summarize the following chat transcript. Include sections for Main Problem and Final Resolution. Translate the content into Brazilian Portuguese: '[11:36] Sameer Patel: こんにちは、ECRリポジトリに新しいイメージをプッシュしましたが、スキャンステータスが更新されません。'
* **Real Trajectory**: The agent parses the Japanese input, identifying the 'User' and 'Agent' roles. It decodes the technical failure (scanOnPush not updating) and the resolution (lifecycle policy adjustment). It then reconstructs these findings into Brazilian Portuguese, ignoring the English metadata and Japanese source tokens in the final string.
* **Real Answer**: { "Problema Principal": "O status do escaneamento de imagem do ECR não atualiza após o push.", "Resolução Final": "Ajuste na política de ciclo de vida para permitir a conclusão do escaneamento." }
* **Why this demonstrates the capability**: The benchmark identifies Japanese as one of the most difficult 'mismatched' languages for LLMs. This case tests if the agent can extract dense technical entities from a high-resource Asian language and transition them into a Romance language target without the English prompt causing structural or linguistic interference, validating the model's resistance to 'Cross-Lingual' perturbation.

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
