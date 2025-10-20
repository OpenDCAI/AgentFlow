"""
QA合成器

负责基于trajectory合成问答对
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
    通用QA合成器，基于配置和示例生成问答对
    """
    
    def __init__(self, config: SynthesisConfig):
        """初始化QA合成器"""
        self.config = config
        
        self.client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", ""))
        )
    
    def synthesize_qa(self, trajectory: Trajectory) -> Optional[SynthesizedQA]:
        """基于trajectory合成问答对"""
        print(f"\n🔧 合成QA对 - Trajectory: {trajectory.trajectory_id}")
        
        # 构建trajectory描述
        traj_description = self._format_trajectory(trajectory)
        
        # 生成问答对
        prompt = self._build_qa_synthesis_prompt(trajectory, traj_description)
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            qa = SynthesizedQA(
                question=result.get("question", ""),
                answer=result.get("answer", ""),
                trajectory_id=trajectory.trajectory_id,
                reasoning_steps=result.get("reasoning_steps", []),
                metadata={
                    "seed_data": trajectory.seed_data,
                    "seed_description": self.config.seed_description,
                    "trajectory_depth": trajectory.total_depth,
                    "synthesis_date": datetime.now().isoformat(),
                    "environment_mode": self.config.environment_mode
                }
            )
            
            print(f"  ✓ 成功合成QA对")
            print(f"    问题: {qa.question[:100]}...")
            print(f"    答案: {qa.answer[:100]}...")
            
            return qa
            
        except Exception as e:
            print(f"  ✗ 合成失败: {str(e)}")
            return None
    
    def _build_qa_synthesis_prompt(self, trajectory: Trajectory, traj_description: str) -> str:
        """构建QA合成的prompt（基于配置动态生成）"""
        
        # 通用prompt模板
        prompt = f"""你是一个数据合成专家。基于以下Agent的探索轨迹，合成一个高质量的问答对。

【起点信息】
内容: {trajectory.seed_data}"""
        
        if self.config.seed_description:
            prompt += f"\n说明: {self.config.seed_description}"
        
        prompt += f"""

【完整探索轨迹】
{traj_description}

"""
        
        # 添加synthesis tips
        if self.config.synthesis_tips:
            prompt += f"""数据合成指导:\n{self.config.synthesis_tips}\n\n"""
        
        # 添加QA示例
        if self.config.qa_examples:
            prompt += """参考以下示例的风格和质量:\n\n"""
            for i, example in enumerate(self.config.qa_examples, 1):
                prompt += f"""示例 {i}:
问题: {example.get('question', '')}
答案: {example.get('answer', '')}
"""
                if 'reasoning' in example:
                    prompt += f"推理过程: {example['reasoning']}\n"
                prompt += "\n"
        
        prompt += f"""
请基于轨迹合成一个问答对:

## 问题要求:
- 参考示例的风格和复杂度
- 需要多步推理才能得到答案
- 问题应该清晰但需要探索
- 问题应该自然地从探索过程中产生

## 答案要求:
- 简洁明确
- 基于轨迹中的真实信息
- 答案应该从探索轨迹中自然得出

## 推理步骤要求:
- 清晰展示从问题到答案的推理过程
- 每步说明使用的工具和得到的信息

返回JSON格式:
{{
    "question": "问题文本",
    "answer": "答案内容",
    "reasoning_steps": [
        {{
            "step": 1,
            "description": "步骤描述",
            "intent": "步骤意图",
            "action": "使用的工具",
            "observation": "观察到的信息摘要"
        }},
        ...
    ]
}}
"""
        
        return prompt
    
    def _format_trajectory(self, trajectory: Trajectory) -> str:
        """格式化trajectory为可读文本"""
        formatted = ""
        
        for i, node in enumerate(trajectory.nodes, 1):
            formatted += f"\n步骤 {i}:\n"
            formatted += f"  意图: {node.intent}\n"
            
            if node.action:
                formatted += f"  动作: {node.action.get('tool_name', 'unknown')}\n"
                formatted += f"  参数: {json.dumps(node.action.get('parameters', {}), ensure_ascii=False)}\n"
            
            obs_preview = node.observation[:500] + "..." if len(node.observation) > 500 else node.observation
            formatted += f"  观察: {obs_preview}\n"
        
        return formatted

