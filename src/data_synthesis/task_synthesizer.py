"""
OSWorld Task Synthesizer

负责基于轨迹合成OSWorld格式的可执行任务（带evaluator）
与QA合成器不同，这里生成的是可以直接在OSWorld中执行和评估的任务
"""

import openai
import json
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

from models import Trajectory, SynthesizedTask
from synthesis_config import SynthesisConfig


class OSWorldTaskSynthesizer:
    """
    OSWorld任务合成器
    
    基于探索轨迹生成OSWorld格式的任务：
    - question: 任务指令（自然语言描述用户目标）
    - config: 初始化配置（环境准备步骤）
    - evaluator: 验证逻辑（如何判断任务完成）
    """
    
    def __init__(self, config: SynthesisConfig):
        """初始化任务合成器"""
        self.config = config
        
        self.client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", ""))
        )
    
    def synthesize_task(self, trajectory: Trajectory, task_index: int = 0) -> Optional[SynthesizedTask]:
        """
        基于轨迹合成OSWorld格式的任务
        
        Args:
            trajectory: 探索轨迹
            task_index: 任务索引
            
        Returns:
            合成的OSWorld任务
        """
        print(f"\n🔧 Synthesizing OSWorld Task - Trajectory: {trajectory.trajectory_id}")
        
        # 构建轨迹描述
        traj_description = self._format_trajectory(trajectory)
        
        # 生成任务
        prompt = self._build_task_synthesis_prompt(trajectory, traj_description)
        
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
            
            # 创建任务对象
            task = SynthesizedTask(
                id=task_id,
                question=result.get("question", ""),
                config=result.get("config", []),
                evaluator=result.get("evaluator", {}),
                trajectory_id=trajectory.trajectory_id,
                source_id=trajectory.source_id,
                answer=result.get("expected_score", 1.0),  # 预期评估得分
                metadata={
                    "seed_data": trajectory.seed_data,
                    "seed_description": self.config.seed_description,
                    "trajectory_depth": trajectory.total_depth,
                    "synthesis_date": datetime.now().isoformat(),
                    "environment_mode": self.config.environment_mode,
                    "num_actions": len(trajectory.nodes) - 1  # 排除root节点
                }
            )
            
            print(f"  ✓ Successfully synthesized OSWorld task")
            print(f"    Task ID: {task_id}")
            print(f"    Question: {task.question[:100]}...")
            print(f"    Evaluator Type: {task.evaluator.get('func', 'N/A')}")
            
            return task
            
        except Exception as e:
            print(f"  ✗ Task synthesis failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _build_task_synthesis_prompt(self, trajectory: Trajectory, traj_description: str) -> str:
        """构建任务合成prompt"""
        
        prompt = f"""You are an OSWorld task synthesis expert. Based on the GUI exploration trajectory, synthesize an executable task in OSWorld format.

【Starting Point】
Content: {trajectory.seed_data}"""
        
        if self.config.seed_description:
            prompt += f"\nDescription: {self.config.seed_description}"
        
        prompt += f"""

【Complete Exploration Trajectory】
{traj_description}

【OSWorld Task Format】
An OSWorld task consists of:
1. **question**: Natural language instruction (what the user wants to accomplish)
2. **config**: Initialization steps (prepare environment before task execution)
3. **evaluator**: Verification logic (how to check if task is completed)

【Task Synthesis Guidelines】
"""
        
        # 添加合成tips
        if self.config.synthesis_tips:
            prompt += f"{self.config.synthesis_tips}\n\n"
        
        # 添加示例
        if self.config.qa_examples:
            prompt += """【Reference Examples】\n"""
            for i, example in enumerate(self.config.qa_examples[:2], 1):
                prompt += f"""
Example {i}:
Question: {example.get('question', '')}
Evaluator: {json.dumps(example.get('evaluator', {}), indent=2) if 'evaluator' in example else 'N/A'}
"""
        
        prompt += """

【Synthesis Requirements】

1. **Question (Task Instruction)**
   - Clear, concise natural language instruction
   - Describe WHAT the user wants to achieve (not HOW to do it)
   - Should be achievable based on the trajectory
   - Examples:
     * "I want to install Spotify on my current system. Could you please help me?"
     * "Please create a new folder named 'Projects' on the Desktop"
     * "Open the text editor and save a file with the content 'Hello World'"

2. **Config (Initialization)**
   - Prepare environment before task execution
   - Usually empty [] for most tasks
   - Only include if specific setup is needed
   - Format: list of {"type": "execute", "parameters": {"command": [...]}}

3. **Evaluator (Verification Logic)**
   - Define HOW to verify task completion
   - Must be automatic and deterministic
   
   Common evaluator types:
   
   a) check_include_exclude (检查命令输出):
   {
     "func": "check_include_exclude",
     "result": {
       "type": "vm_command_line",
       "command": "which spotify"
     },
     "expected": {
       "type": "rule",
       "rules": {
         "include": ["spotify"],
         "exclude": ["not found"]
       }
     }
   }
   
   b) check_file_existence (检查文件存在):
   {
     "func": "check_include_exclude",
     "result": {
       "type": "vm_command_line", 
       "command": "ls ~/Desktop/Projects"
     },
     "expected": {
       "type": "rule",
       "rules": {
         "include": ["Projects"],
         "exclude": []
       }
     }
   }
   
   c) check_file_content (检查文件内容):
   {
     "func": "check_include_exclude",
     "result": {
       "type": "vm_file_content",
       "path": "/home/user/file.txt"
     },
     "expected": {
       "type": "rule",
       "rules": {
         "include": ["Hello World"],
         "exclude": []
       }
     }
   }

【Output Format】
Return JSON with the following structure:
{
  "question": "Natural language task instruction",
  "config": [],
  "evaluator": {
    "func": "evaluator_function_name",
    "result": {
      "type": "verification_type",
      ...
    },
    "expected": {
      "type": "rule",
      "rules": {
        "include": ["..."],
        "exclude": ["..."]
      }
    }
  },
  "expected_score": 1.0
}

Now synthesize an OSWorld task based on the trajectory above:
"""
        
        return prompt
    
    def _format_trajectory(self, trajectory: Trajectory) -> str:
        """格式化轨迹为可读文本"""
        formatted = ""
        
        for i, node in enumerate(trajectory.nodes, 1):
            formatted += f"\nStep {i}:\n"
            formatted += f"  Intent: {node.intent}\n"
            
            if node.action:
                tool_name = node.action.get('tool_name', 'unknown')
                parameters = node.action.get('parameters', {})
                formatted += f"  Action: {tool_name}\n"
                formatted += f"  Parameters: {json.dumps(parameters, ensure_ascii=False)}\n"
            
            # 截断observation以避免过长
            obs_preview = node.observation[:300] + "..." if len(node.observation) > 300 else node.observation
            formatted += f"  Observation: {obs_preview}\n"
        
        return formatted
    
    def _extract_verification_info(self, trajectory: Trajectory) -> Dict[str, Any]:
        """
        从轨迹中提取验证信息
        
        尝试自动推断：
        - 哪些文件被创建/修改
        - 哪些程序被安装
        - 哪些配置被更改
        """
        verification_hints = {
            "files_created": [],
            "programs_installed": [],
            "commands_executed": []
        }
        
        for node in trajectory.nodes:
            if not node.action:
                continue
                
            tool_name = node.action.get('tool_name', '')
            params = node.action.get('parameters', {})
            
            # 检测文件操作
            if tool_name == 'type' and 'text' in params:
                text = params['text']
                if '/' in text or '~' in text:
                    verification_hints["files_created"].append(text)
            
            # 检测程序安装（简单启发式）
            if 'observation' in node.__dict__:
                obs = node.observation.lower()
                if 'install' in obs or 'apt' in obs or 'download' in obs:
                    # 尝试提取程序名
                    pass
        
        return verification_hints

