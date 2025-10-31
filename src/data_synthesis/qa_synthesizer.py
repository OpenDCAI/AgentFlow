"""
QA Synthesizer

Responsible for synthesizing Q&A pairs based on trajectories
"""

import openai
import json
import os
from typing import Optional
from datetime import datetime

from models import Trajectory, SynthesizedQA
from synthesis_config import SynthesisConfig


class GenericQASynthesizer:
    """
    Generic QA synthesizer that generates Q&A pairs based on configuration and examples
    """
    
    def __init__(self, config: SynthesisConfig):
        """Initialize QA synthesizer"""
        self.config = config
        
        self.client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", ""))
        )
    
    def synthesize_qa(self, trajectory: Trajectory, qa_index: int = 0) -> Optional[SynthesizedQA]:
        """Synthesize Q&A pair based on trajectory"""
        print(f"\n🔧 Synthesizing QA pair - Trajectory: {trajectory.trajectory_id}")
        
        # Build trajectory description
        traj_description = self._format_trajectory(trajectory)
        
        # Generate Q&A pair
        prompt = self._build_qa_synthesis_prompt(trajectory, traj_description)
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # 生成QA的唯一标识：source_id + trajectory编号 + qa编号
            qa_id = f"{trajectory.trajectory_id}_qa_{qa_index}"
            
            qa = SynthesizedQA(
                question=result.get("question", ""),
                answer=result.get("answer", ""),
                trajectory_id=trajectory.trajectory_id,
                source_id=trajectory.source_id,
                qa_id=qa_id,
                reasoning_steps=result.get("reasoning_steps", []),
                metadata={
                    "seed_data": trajectory.seed_data,
                    "seed_description": self.config.seed_description,
                    "trajectory_depth": trajectory.total_depth,
                    "synthesis_date": datetime.now().isoformat(),
                    "environment_mode": self.config.environment_mode
                }
            )
            
            print(f"  ✓ Successfully synthesized QA pair")
            print(f"    QA ID: {qa_id}")
            print(f"    Question: {qa.question[:100]}...")
            print(f"    Answer: {qa.answer[:100]}...")
            
            return qa
            
        except Exception as e:
            print(f"  ✗ Synthesis failed: {str(e)}")
            return None
    
    def _build_qa_synthesis_prompt(self, trajectory: Trajectory, traj_description: str) -> str:
        """Build QA synthesis prompt (dynamically generated based on configuration)"""
        
        # Generic prompt template
        prompt = f"""You are a data synthesis expert. Based on the following Agent's exploration trajectory, synthesize a high-quality Q&A pair.

【Starting Point Information】
Content: {trajectory.seed_data}"""
        
        if self.config.seed_description:
            prompt += f"\nDescription: {self.config.seed_description}"
        
        prompt += f"""

【Complete Exploration Trajectory】
{traj_description}

"""
        
        # Add synthesis tips
        if self.config.synthesis_tips:
            prompt += f"""Data Synthesis Guidance:\n{self.config.synthesis_tips}\n\n"""
        
        # Add QA examples
        if self.config.qa_examples:
            prompt += """Refer to the style and quality of the following examples:\n\n"""
            for i, example in enumerate(self.config.qa_examples, 1):
                prompt += f"""Example {i}:
Question: {example.get('question', '')}
Answer: {example.get('answer', '')}
"""
                if 'reasoning' in example:
                    prompt += f"Reasoning Process: {example['reasoning']}\n"
                prompt += "\n"
        
        prompt += f"""
Please synthesize a Q&A pair based on the trajectory:

## Question Requirements:
- Refer to the style and complexity of examples
- Requires multi-step reasoning to reach the answer
- Question should be clear but require exploration
- Question should naturally arise from the exploration process

## Answer Requirements:
- Concise and clear
- Based on real information from the trajectory
- Answer should naturally derive from the exploration trajectory

## Reasoning Steps Requirements:
- Clearly show the reasoning process from question to answer
- Each step should explain the tool used and information obtained

Return in JSON format:
{{
    "question": "question text",
    "answer": "answer content",
    "reasoning_steps": [
        {{
            "step": 1,
            "description": "step description",
            "intent": "step intent",
            "action": "tool used",
            "observation": "summary of observed information"
        }},
        ...
    ]
}}
"""
        
        return prompt
    
    def _format_trajectory(self, trajectory: Trajectory) -> str:
        """Format trajectory into readable text"""
        formatted = ""
        
        for i, node in enumerate(trajectory.nodes, 1):
            formatted += f"\nStep {i}:\n"
            formatted += f"  Intent: {node.intent}\n"
            
            if node.action:
                formatted += f"  Action: {node.action.get('tool_name', 'unknown')}\n"
                formatted += f"  Parameters: {json.dumps(node.action.get('parameters', {}), ensure_ascii=False)}\n"
            
            obs_preview = node.observation[:500] + "..." if len(node.observation) > 500 else node.observation
            formatted += f"  Observation: {obs_preview}\n"
        
        return formatted

