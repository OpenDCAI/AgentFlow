"""
Exploration Trajectory Summarizer

从探索轨迹中"总结"出有价值的任务和QA数据
与直接生成的区别：这里是从已有探索中"发现"和"提炼"任务
"""

import openai
import json
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

from models import Trajectory, SynthesizedTask, SynthesizedQA
from synthesis_config import SynthesisConfig


class ExplorationSummarizer:
    """
    探索轨迹总结器
    
    功能：
    1. 分析探索轨迹，识别有价值的操作序列
    2. 从探索中提炼出可执行的任务
    3. 为任务生成合适的evaluator
    4. 或者生成推理型的QA对
    """
    
    def __init__(self, config: SynthesisConfig):
        """初始化总结器"""
        self.config = config
        
        self.client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", ""))
        )
    
    def summarize_to_task(
        self, 
        trajectory: Trajectory,
        task_index: int = 0
    ) -> Optional[SynthesizedTask]:
        """
        从探索轨迹中总结出任务
        
        关键：不是基于轨迹"生成"任务，而是"发现"轨迹中隐含的任务
        
        Args:
            trajectory: 探索轨迹
            task_index: 任务索引
            
        Returns:
            总结出的任务
        """
        print(f"\n📝 总结探索轨迹为任务 - Trajectory: {trajectory.trajectory_id}")
        
        # 构建轨迹描述
        traj_description = self._format_exploration_trajectory(trajectory)
        
        # 生成总结prompt
        prompt = self._build_task_summarization_prompt(trajectory, traj_description)
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # 生成任务ID
            task_id = f"{trajectory.source_id}_task_{task_index}"
            
            # 创建任务
            task = SynthesizedTask(
                id=task_id,
                question=result.get("task_instruction", ""),
                config=result.get("config", []),
                evaluator=result.get("evaluator", {}),
                trajectory_id=trajectory.trajectory_id,
                source_id=trajectory.source_id,
                answer=result.get("expected_score", 1.0),
                metadata={
                    "exploration_seed": trajectory.seed_data,
                    "trajectory_depth": trajectory.total_depth,
                    "num_actions": len(trajectory.nodes) - 1,
                    "synthesis_date": datetime.now().isoformat(),
                    "synthesis_type": "exploration_summary"
                }
            )
            
            print(f"  ✓ 成功总结出任务")
            print(f"    Task ID: {task_id}")
            print(f"    任务指令: {task.question[:100]}...")
            print(f"    Evaluator类型: {task.evaluator.get('func', 'N/A')}")
            
            return task
            
        except Exception as e:
            print(f"  ✗ 任务总结失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def summarize_to_qa(
        self,
        trajectory: Trajectory,
        qa_index: int = 0
    ) -> Optional[SynthesizedQA]:
        """
        从探索轨迹中总结出QA对
        
        关键：从探索中发现有价值的问题和答案
        
        Args:
            trajectory: 探索轨迹
            qa_index: QA索引
            
        Returns:
            总结出的QA对
        """
        print(f"\n📝 总结探索轨迹为QA - Trajectory: {trajectory.trajectory_id}")
        
        # 构建轨迹描述
        traj_description = self._format_exploration_trajectory(trajectory)
        
        # 生成总结prompt
        prompt = self._build_qa_summarization_prompt(trajectory, traj_description)
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # 生成QA ID
            qa_id = f"{trajectory.trajectory_id}_qa_{qa_index}"
            
            qa = SynthesizedQA(
                question=result.get("question", ""),
                answer=result.get("answer", ""),
                trajectory_id=trajectory.trajectory_id,
                source_id=trajectory.source_id,
                qa_id=qa_id,
                reasoning_steps=result.get("reasoning_steps", []),
                metadata={
                    "exploration_seed": trajectory.seed_data,
                    "trajectory_depth": trajectory.total_depth,
                    "synthesis_date": datetime.now().isoformat(),
                    "synthesis_type": "exploration_summary"
                }
            )
            
            print(f"  ✓ 成功总结出QA对")
            print(f"    QA ID: {qa_id}")
            print(f"    问题: {qa.question[:100]}...")
            print(f"    答案: {qa.answer[:100]}...")
            
            return qa
            
        except Exception as e:
            print(f"  ✗ QA总结失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _build_task_summarization_prompt(
        self,
        trajectory: Trajectory,
        traj_description: str
    ) -> str:
        """构建任务总结prompt"""
        
        prompt = f"""You are a GUI task discovery expert. Analyze the following GUI exploration trajectory and DISCOVER a meaningful, executable task that was implicitly demonstrated.

【Exploration Direction】
{trajectory.seed_data}

【Complete Exploration Trajectory】
{traj_description}

【Your Task: DISCOVER and SUMMARIZE】
From this exploration trajectory, identify:
1. What meaningful task was accomplished or could be accomplished?
2. What would be a clear task instruction for this operation sequence?
3. How can we verify this task was completed correctly?

【Important Guidelines】
- The task should be DISCOVERED from the trajectory, not invented
- The task instruction should be natural and user-friendly
- The evaluator must be automatic and deterministic
- Focus on the VALUE and PURPOSE of the discovered operations

【Common Evaluator Types】

1. **Command Output Check** (for installations, file operations):
```json
{{
  "func": "check_include_exclude",
  "result": {{
    "type": "vm_command_line",
    "command": "which <program>" or "ls <path>"
  }},
  "expected": {{
    "type": "rule",
    "rules": {{
      "include": ["expected_text"],
      "exclude": ["error_text"]
    }}
  }}
}}
```

2. **File Content Check** (for file creation/editing):
```json
{{
  "func": "check_include_exclude",
  "result": {{
    "type": "vm_file_content",
    "path": "~/path/to/file"
  }},
  "expected": {{
    "type": "rule",
    "rules": {{
      "include": ["expected_content"],
      "exclude": []
    }}
  }}
}}
```

【Output Format】
Return JSON:
{{
  "task_instruction": "Clear, natural language instruction of what task to accomplish",
  "discovered_operations": ["list", "of", "key", "operations", "found"],
  "task_value": "Why this task is useful/meaningful",
  "config": [],
  "evaluator": {{
    "func": "evaluator_function",
    "result": {{...}},
    "expected": {{...}}
  }},
  "expected_score": 1.0
}}
"""
        
        # 添加示例
        if self.config.qa_examples:
            prompt += "\n【Reference Examples】\n"
            for i, example in enumerate(self.config.qa_examples[:2], 1):
                prompt += f"\nExample {i}:\n"
                prompt += f"Task: {example.get('question', '')}\n"
                if 'evaluator' in example:
                    prompt += f"Evaluator: {json.dumps(example['evaluator'], indent=2)}\n"
        
        return prompt
    
    def _build_qa_summarization_prompt(
        self,
        trajectory: Trajectory,
        traj_description: str
    ) -> str:
        """构建QA总结prompt"""
        
        prompt = f"""You are a GUI reasoning expert. Analyze the following GUI exploration trajectory and DISCOVER an interesting reasoning question that can be answered based on what was discovered.

【Exploration Direction】
{trajectory.seed_data}

【Complete Exploration Trajectory】
{traj_description}

【Your Task: DISCOVER and CREATE】
From this exploration trajectory, create:
1. An interesting question that requires understanding the discovered operations
2. A clear answer based on the trajectory
3. Reasoning steps showing how to derive the answer

【Question Types to Consider】
- "What operations are needed to accomplish X?"
- "How many steps does it take to reach Y?"
- "What feature was discovered in Z location?"
- "What is the relationship between A and B operations?"

【Important Guidelines】
- Question should be GROUNDED in the actual exploration
- Answer must be DERIVABLE from the trajectory
- Reasoning should show the logical steps
- Focus on INSIGHTS discovered during exploration

【Output Format】
Return JSON:
{{
  "question": "Clear, interesting question",
  "answer": "Concise answer",
  "reasoning_steps": [
    {{
      "step": 1,
      "description": "step description",
      "observation": "what was observed",
      "conclusion": "what this tells us"
    }},
    ...
  ],
  "discovered_insights": ["key", "insights", "from", "exploration"]
}}
"""
        
        # 添加QA示例
        if self.config.qa_examples:
            prompt += "\n【Reference QA Examples】\n"
            for i, example in enumerate(self.config.qa_examples[:2], 1):
                if 'evaluator' not in example:  # 只展示QA格式的示例
                    prompt += f"\nExample {i}:\n"
                    prompt += f"Q: {example.get('question', '')}\n"
                    prompt += f"A: {example.get('answer', '')}\n"
        
        return prompt
    
    def _format_exploration_trajectory(self, trajectory: Trajectory) -> str:
        """格式化探索轨迹"""
        formatted = ""
        
        for i, node in enumerate(trajectory.nodes, 1):
            formatted += f"\n=== 探索步骤 {i} (深度: {node.depth}) ===\n"
            formatted += f"意图: {node.intent}\n"
            
            if node.action:
                tool_name = node.action.get('tool_name', 'unknown')
                parameters = node.action.get('parameters', {})
                formatted += f"动作: {tool_name}\n"
                formatted += f"参数: {json.dumps(parameters, ensure_ascii=False)}\n"
            
            # 保留observation的关键信息
            obs_lines = node.observation.split('\n')
            key_obs = '\n'.join(obs_lines[:20])  # 前20行
            if len(obs_lines) > 20:
                key_obs += f"\n... (省略{len(obs_lines)-20}行)"
            
            formatted += f"观察:\n{key_obs}\n"
        
        return formatted

