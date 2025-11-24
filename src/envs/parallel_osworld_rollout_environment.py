# -*- coding: utf-8 -*-
"""
Parallel OSWorld Rollout Environment - 直接继承 Environment，内联 DesktopEnv 逻辑。

特性：
- 独立持有 PythonController/SetupController，不依赖 DesktopEnv 类。
- 从 VMPoolResourceManager 获取连接凭证 (Attach 模式)。
- 负责 Task 级别的 Setup 和 Teardown。
- [修改] 完整的 run_task 实现，支持多模态交互与轨迹记录。
"""

import os
import sys
import json
import base64
import logging
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, cast, Callable

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from envs.enviroment import Environment
from envs.data_models import Observation
from tools.tool import Tool
from utils.resource_manager import ResourceManager, NoResourceManager, VMPoolResourceManager
from utils.instance_tracker import get_instance_tracker

# 引入原 DesktopEnv 依赖的底层组件
from utils.desktop_env.controllers.python import PythonController
from utils.desktop_env.controllers.setup import SetupController, VMReadinessProbe
from utils.desktop_env.evaluators import metrics, getters

logger = logging.getLogger(__name__)

# 类型别名
Metric = Callable[[Any, Any], float]
Getter = Callable[[Any, Dict[str, Any]], Any]

def _fix_pyautogui_less_than_bug(command: str) -> str:
    """修复 PyAutoGUI '<' 字符输入的 Bug"""
    press_pattern = r'pyautogui\.press\(["\'](?:<|\\u003c)["\']\)'
    def replace_press_less_than(match):
        return 'pyautogui.hotkey("shift", ",")'
    command = re.sub(press_pattern, replace_press_less_than, command)
    
    typewrite_pattern = r'pyautogui\.typewrite\((["\'])(.*?)\1\)'
    def process_typewrite_match(match):
        quote_char = match.group(1)
        content = match.group(2)
        try:
            decoded_content = content.encode('utf-8').decode('unicode_escape')
            content = decoded_content
        except UnicodeDecodeError:
            pass
        if '<' not in content:
            return match.group(0)
        parts = content.split('<')
        result_parts = []
        for i, part in enumerate(parts):
            if i == 0:
                if part: result_parts.append(f"pyautogui.typewrite({quote_char}{part}{quote_char})")
            else:
                result_parts.append('pyautogui.hotkey("shift", ",")')
                if part: result_parts.append(f"pyautogui.typewrite({quote_char}{part}{quote_char})")
        return '; '.join(result_parts)
    
    command = re.sub(typewrite_pattern, process_typewrite_match, command)
    return command


class ParallelOSWorldRolloutEnvironment(Environment):
    """Parallel OSWorld Environment built directly on Environment base class."""
    
    # 声明此环境需要重型资源
    has_heavy_resource = True

    @classmethod
    def setup_global_resources(cls, config: Any) -> ResourceManager:
        """根据配置初始化全局资源管理器（VM 池）"""
        
        target_modes = ["osworld", "osworld_parallel"]
        current_mode = getattr(config, 'env_mode', None)
        
        if current_mode not in target_modes:
            logger.info(f"Mode '{current_mode}' is not a heavy resource mode, using NoResourceManager")
            return NoResourceManager()
        
        if not (hasattr(config, 'use_resource_pool') and config.use_resource_pool):
            logger.info("Resource pool disabled, using NoResourceManager")
            return NoResourceManager()
        
        logger.info("Initializing VM pool (Distributed Worker Architecture)...")
        env_kwargs = getattr(config, 'env_kwargs', {}) or {}
        pool_config = {
            "num_vms": getattr(config, 'num_vms', 3),
            "provider_name": env_kwargs.get("provider_name", "vmware"),
            "path_to_vm": env_kwargs.get("path_to_vm"),
            "snapshot_name": env_kwargs.get("snapshot_name", "init_state"),
            "action_space": env_kwargs.get("action_space", "computer_13"),
            "screen_size": (
                env_kwargs.get("screen_width", 1920),
                env_kwargs.get("screen_height", 1080),
            ),
            "headless": env_kwargs.get("headless", False),
            "require_a11y_tree": env_kwargs.get("require_a11y_tree", True),
            "require_terminal": env_kwargs.get("require_terminal", False),
            "os_type": env_kwargs.get("os_type", "Ubuntu"),
            "client_password": env_kwargs.get("client_password", "password"),
        }
        resource_manager = VMPoolResourceManager(pool_config=pool_config)
        resource_manager.initialize()
        return resource_manager

    def __init__(
        self,
        resource_manager: Optional[ResourceManager] = None,
        parallel_degree: int = 1,
        model_name: str = "gpt-4.1-2025-04-14",
        openai_api_key: Optional[str] = None,
        openai_api_url: Optional[str] = None,
        enable_terminal_bench: bool = False,
        **osworld_kwargs,
    ):
        self._pending_osworld_kwargs = dict(osworld_kwargs)
        
        # 控制器相关
        self.controller: Optional[PythonController] = None
        self.setup_controller: Optional[SetupController] = None
        self._allocated_resource_id: Optional[str] = None

        # 评测相关
        self.metric: Optional[Union[Metric, List[Metric]]] = None
        self.result_getter: Optional[Union[Getter, List[Getter]]] = None
        self.expected_getter: Optional[Union[Getter, List[Getter]]] = None
        self.metric_options: Optional[Union[Dict, List[Dict]]] = None
        self.evaluator_config: Dict = {}
        self.metric_conj: str = "and"

        # 缓存配置
        self._action_history: List[Any] = []
        self._step_no: int = 0
        self._current_trajectory: List[Dict[str, Any]] = []
        self._current_task_id: Optional[str] = None
        self._current_instruction: str = ""
        
        # Task 级别配置缓存
        self._task_use_proxy: Optional[bool] = None

        super().__init__(
            model_name=model_name,
            openai_api_key=openai_api_key,
            openai_api_url=openai_api_url,
            enable_terminal_bench=enable_terminal_bench,
            defer_init=True,
            resource_manager=resource_manager,
            parallel_degree=parallel_degree,
        )

        self._tools_registered = False

    # ---------------------------------------------------------------------
    # Environment overrides
    # ---------------------------------------------------------------------
    @property
    def mode(self) -> str:
        return "osworld"

    def get_action_space(self) -> str:
        return self.config.get("osworld", {}).get("action_space", "computer_13")

    def _replace_prompt_placeholders(self, prompt: str) -> str:
        prompt = super()._replace_prompt_placeholders(prompt)
        if "{CLIENT_PASSWORD}" in prompt:
            client_password = self.config.get("osworld", {}).get("client_password", "password")
            prompt = prompt.replace("{CLIENT_PASSWORD}", client_password)
        return prompt

    def _initialize_config(self):
        pending = getattr(self, "_pending_osworld_kwargs", {})
        osworld_defaults = {
            "path_to_vm": pending.get("path_to_vm"),
            "provider_name": pending.get("provider_name", "vmware"),
            "action_space": pending.get("action_space", "computer_13"),
            "observation_type": pending.get("observation_type", "screenshot_a11y_tree"),
            "screen_width": pending.get("screen_width", 1920),
            "screen_height": pending.get("screen_height", 1080),
            "headless": pending.get("headless", False),
            "os_type": pending.get("os_type", "Ubuntu"),
            "client_password": pending.get("client_password", "password"),
            "snapshot_name": pending.get("snapshot_name"),
            "require_terminal": pending.get("require_terminal"),
            "require_a11y_tree": pending.get("require_a11y_tree", True),
            "sleep_after_execution": pending.get("sleep_after_execution", 2),
            "enable_recording": pending.get("enable_recording", True),
        }
        self.config["osworld"] = osworld_defaults
        self.config["osworld_available"] = False
        self._pending_osworld_kwargs = {}
        super()._initialize_config()

    def _validate_config(self):
        super()._validate_config()
        osworld_config = self.config.get("osworld", {})
        if not osworld_config.get("action_space"):
            raise ValueError("action_space is required")
        observation_type = osworld_config.get("observation_type")
        valid_obs = {"screenshot", "a11y_tree", "screenshot_a11y_tree", "som"}
        if observation_type not in valid_obs:
            raise ValueError(f"Invalid observation_type '{observation_type}'")

    def _initialize_tools(self):
        return

    def initialize_with_task_config(self, task_config: Dict[str, Any]) -> bool:
        self._task_env_config = task_config
        env_specific_config = task_config.get(self.mode, {})
        return self._apply_task_config(env_specific_config)

    def _apply_task_config(self, env_config: Dict[str, Any]) -> bool:
        if not env_config:
            return True
        if "proxy" in env_config:
            self._task_use_proxy = env_config["proxy"]
        return True

    # ---------------------------------------------------------------------
    # Resource management
    # ---------------------------------------------------------------------
    def allocate_resource(self, worker_id: str, timeout: float = 60.0) -> bool:
        """从资源管理器分配 VM 并在本地初始化 Controller"""
        if not self.resource_manager:
            logger.error("Resource manager not set")
            return False

        try:
            # 1. 获取纯数据连接信息
            result = self.resource_manager.allocate(
                worker_id=worker_id,
                timeout=timeout
            )
            resource_id, conn_info = result
            
            # 2. 本地初始化控制器
            self._init_controllers_from_connection(resource_id, conn_info)
            self._allocated_resource_id = resource_id
            self.config["osworld_available"] = True
            
            # 3. 注册工具
            if not self._tools_registered:
                self._register_tools()
                self._tools_registered = True
                logger.info(f"Registered {len(self.tools)} OSWorld tools")
            
            logger.info(f"[resource] worker={worker_id} acquired vm={resource_id}")
            return True
        except Exception as exc:
            logger.error(f"Failed to allocate resource: {exc}", exc_info=True)
            return False

    def _init_controllers_from_connection(self, vm_id: str, conn_info: Dict[str, Any]):
        """在 Worker 本地根据连接信息初始化控制器"""
        vm_ip = conn_info.get("ip")
        server_port = conn_info.get("port", 5000)
        osworld_conf = self.config.get("osworld", {})
        
        # 使用配置中的缓存目录或默认值
        cache_dir = "cache" 
        
        # 初始化 PythonController
        self.controller = PythonController(
            vm_ip=vm_ip,
            server_port=server_port,
            instance_id=vm_id
        )
        
        # 初始化 SetupController
        self.setup_controller = SetupController(
            vm_ip=vm_ip,
            server_port=server_port,
            chromium_port=conn_info.get("chromium_port", 9222),
            vlc_port=conn_info.get("vlc_port", 8080),
            cache_dir=cache_dir,
            client_password=osworld_conf.get("client_password", "password"),
            screen_width=osworld_conf.get("screen_width", 1920),
            screen_height=osworld_conf.get("screen_height", 1080),
            vm_readiness_probe=None # Attach 模式无需 Probe
        )
        logger.info(f"Controllers initialized for VM {vm_id} at {vm_ip}:{server_port}")

    def release_resource(self, worker_id: str, reset: bool = True) -> None:
        """释放资源并清理本地控制器"""
        self.controller = None
        self.setup_controller = None
        self.config["osworld_available"] = False
        
        if self._allocated_resource_id and self.resource_manager:
            try:
                self.resource_manager.release(
                    self._allocated_resource_id,
                    worker_id,
                    reset=reset,
                )
            except Exception as exc:
                logger.error(f"Failed to release resource: {exc}", exc_info=True)

        self._allocated_resource_id = None
        self._tools_registered = False

    def get_allocated_resource_id(self) -> Optional[str]:
        return self._allocated_resource_id

    def cleanup(self, worker_id: str, reset: bool = True) -> None:
        self.env_close()
        self.release_resource(worker_id, reset=reset)

    def env_start(self) -> None:
        if self.controller is None:
            logger.warning("Controller not set. Call allocate_resource() first.")

    def env_close(self) -> None:
        self.controller = None

    # =====================================================================
    # 1. 核心：重写 run_task 以适配 OSWorld 的生命周期与多模态交互
    # =====================================================================
    def run_task(self, task: Dict[str, Any], agent_config: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
        """
        覆盖基类 run_task。
        结合 env_task_init/env_task_end 管理生命周期，并处理多模态观察流。
        """
        task_id = task.get("id", "unknown")
        question = task.get("question", "")
        
        # 获取配置
        model_name = agent_config.get("model_name", "gpt-4o")
        max_turns = agent_config.get("max_turns", 15)
        max_retries = agent_config.get("max_retries", 3)
        output_dir = agent_config.get("output_dir", "results")
        
        # 准备任务输出目录
        task_output_dir = os.path.join(output_dir, "task_output", task_id)
        os.makedirs(task_output_dir, exist_ok=True)

        logger.info(f"Starting run_task for {task_id}")

        # -----------------------------------------------------------------
        # 1. 环境初始化 (Setup VM, Cache, Recording)
        # -----------------------------------------------------------------
        try:
            # env_task_init 内部调用 _internal_reset -> setup_controller.setup
            # 这利用了 task metadata 中的 config 来配置环境（如登录账号、打开应用）
            initial_obs = self.env_task_init(task)
        except Exception as e:
            logger.error(f"Environment initialization failed: {e}", exc_info=True)
            return {
                "task_id": task_id, 
                "error": str(e), 
                "success": False
            }

        # -----------------------------------------------------------------
        # 2. 构建初始对话历史 (Inject Initial Screenshot & A11y Tree)
        # -----------------------------------------------------------------
        system_prompt = self.get_system_prompt(question)
        messages = [{"role": "system", "content": system_prompt}]
        
        # 构建 User 消息：包含 Question + 初始截图 + 初始 A11y Tree
        user_content = [{"type": "text", "text": f"Question: {question}\n"}]
        
        if initial_obs:
            if "text" in initial_obs and initial_obs["text"]:
                user_content.append({
                    "type": "text", 
                    "text": f"Accessibility Tree:\n{initial_obs['text']}"
                })
            if "image" in initial_obs and initial_obs["image"]:
                user_content.append({
                    "type": "image_url", 
                    "image_url": {"url": f"data:image/png;base64,{initial_obs['image']}"}
                })
        
        messages.append({"role": "user", "content": user_content})

        # -----------------------------------------------------------------
        # 3. Agent 交互循环 (LLM -> Tool -> Obs)
        # -----------------------------------------------------------------
        client = self._get_openai_client()
        turn_count = 0
        final_answer = None
        
        while turn_count < max_turns:
            logger.info(f"Turn {turn_count} processing...")
            
            # (A) 调用 LLM
            response_msg = None
            for attempt in range(max_retries):
                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        tools=self.get_tool_schemas(),
                        tool_choice="auto"
                    )
                    response_msg = response.choices[0].message
                    break
                except Exception as e:
                    logger.warning(f"LLM API error (attempt {attempt}): {e}")
                    time.sleep(2)
            
            if not response_msg:
                logger.error("Failed to get response from LLM after retries.")
                break
            
            # 记录 LLM 回复
            messages.append(response_msg.model_dump())
            
            # (B) 处理工具调用
            tool_calls = response_msg.tool_calls
            if tool_calls:
                for tool_call in tool_calls:
                    func_name = tool_call.function.name
                    try:
                        args = json.loads(tool_call.function.arguments)
                    except:
                        args = {}
                    
                    logger.info(f"Executing tool: {func_name} with args: {args}")
                    
                    # 执行工具 (内部调用 self._internal_step)
                    # execute_tool 捕获异常并返回结果，这里结果通常是 _internal_step 返回的 raw obs dict
                    tool_result = self.execute_tool(func_name, args)
                    
                    # (C) 处理观察结果 (Observation)
                    # 我们需要将工具执行结果转化为 LLM 可读的消息
                    tool_resp_content = "Action executed successfully."
                    obs_content_blocks = []

                    # 检查结果是否包含观察数据 (截图/Tree)
                    # 注意：execute_tool 返回的如果是 dict，通常包含 status, response, observation
                    # 这里的逻辑假设 tool_result 是工具返回的标准结构
                    
                    # 提取观察数据
                    obs_data = {}
                    if isinstance(tool_result, dict):
                        # 适配 osworld_tools 的返回格式 {'status':..., 'response':..., 'observation':...}
                        tool_resp_content = tool_result.get('response', str(tool_result))
                        obs_data = tool_result.get('observation', {})
                    elif isinstance(tool_result, str):
                        tool_resp_content = tool_result
                    
                    if obs_data:
                        # 确保格式化（如果工具层没做）
                        formatted = obs_data if "image" in obs_data else self.format_observation_by_type(obs_data, output_format="dict")
                        
                        # 添加 Tree
                        if formatted.get("text"):
                            obs_content_blocks.append({
                                "type": "text", 
                                "text": f"Observation (Accessibility Tree):\n{formatted['text']}"
                            })
                        # 添加 Image
                        if formatted.get("image"):
                            obs_content_blocks.append({
                                "type": "image_url", 
                                "image_url": {"url": f"data:image/png;base64,{formatted['image']}"}
                            })

                    # 添加 Tool Role 消息 (主要用于确认执行)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": tool_resp_content
                    })
                    
                    # 添加 User Role 消息 (携带新的 Screenshot/Tree)
                    if obs_content_blocks:
                        messages.append({"role": "user", "content": obs_content_blocks})
            
            else:
                # (D) 没有工具调用 -> 视为最终答案
                final_answer = response_msg.content
                logger.info("Final answer received.")
                break
            
            turn_count += 1

        # -----------------------------------------------------------------
        # 4. 任务收尾 (Extract Answer, Stop Recording, Save Trajectory)
        # -----------------------------------------------------------------
        if not final_answer:
            final_answer = self._extract_final_answer(messages)
            
        # 调用 env_task_end 保存视频和轨迹文件
        self.env_task_end(task_id, task_output_dir, final_answer)
        
        return {
            "task_id": task_id,
            "question": question,
            "answer": final_answer,
            "messages": messages,
            "success": True,
            "error": None
        }

    # ---------------------------------------------------------------------
    # Core Interactions (Replace DesktopEnv)
    # ---------------------------------------------------------------------
    def _internal_reset(self, task_config: Dict[str, Any]):
        """
        替代 DesktopEnv.reset
        VM 重置已由 Manager 在 release() 时处理，此处只处理 Task Setup。
        """
        if not self.controller or not self.setup_controller:
            raise ValueError("Controllers not initialized")

        logger.info(f"Resetting for task {task_config.get('id')}...")
        self._action_history = []
        self._step_no = 0
        
        # 1. 设置任务信息 & 解析 Evaluator
        metadata = task_config.get("metadata", {})
        task_id = task_config.get("id", "unknown")
        
        task_cache_dir = os.path.join("cache", task_id)
        os.makedirs(task_cache_dir, exist_ok=True)
        self.setup_controller.reset_cache_dir(task_cache_dir)
        
        # 保存 instruction (question) 供 get_obs 使用
        self._current_instruction = task_config.get("question", "")

        if "evaluator" in metadata:
             self._setup_evaluators(metadata["evaluator"])

        # 2. 执行 SetupController (Task Config)
        config_list = metadata.get("config", [])
        use_proxy = metadata.get("proxy", False)
        
        if use_proxy:
             client_pwd = self.config.get("osworld", {}).get("client_password", "password")
             self.setup_controller._proxy_setup(client_pwd)
        
        if config_list:
            logger.info("Executing task setup...")
            success = self.setup_controller.setup(config_list, use_proxy)
            if not success:
                logger.warning("Task setup reported failure")

        return self._internal_get_obs()

    # =====================================================================
    # 2. 优化路径记录：保存动作、文本和图像 (覆盖原 _internal_step)
    # =====================================================================
    def _internal_step(self, action: Union[str, Dict], pause: float = 2):
        """
        替代 DesktopEnv.step。
        优化：在执行动作后，将完整的 [动作 + 文本状态 + 图像状态] 记录到 trajectory。
        """
        self._step_no += 1
        self._action_history.append(action)
        
        # --- Action Execution ---
        action_type = action if isinstance(action, str) else action.get('action_type')
        if action_type in ['WAIT', 'FAIL', 'DONE']:
            if action_type == 'WAIT': time.sleep(pause)
        
        action_space = self.config.get("osworld", {}).get("action_space", "computer_13")
        if action_space == "computer_13":
            self.controller.execute_action(action)
        elif action_space in ["pyautogui", "claude_computer_use"]:
             if action_type not in ['WAIT', 'FAIL', 'DONE']:
                cmd = action if isinstance(action, str) else action['command']
                fixed_cmd = _fix_pyautogui_less_than_bug(cmd)
                self.controller.execute_python_command(fixed_cmd)

        time.sleep(pause)
        
        # --- Get Observation ---
        obs = self._internal_get_obs()
        
        # --- Record Trajectory (Text & Image) ---
        # 使用 format_observation_by_type 确保图像转为 base64，文本经过裁剪处理
        formatted_obs = self.format_observation_by_type(obs, output_format="dict")
        
        if isinstance(formatted_obs, dict):
            step_record = {
                "step": self._step_no,
                "action": action,
                "timestamp": datetime.now().isoformat(),
                # 同时保留两类模态数据
                "text": formatted_obs.get("text", ""),   # Processed Accessibility Tree
                "image": formatted_obs.get("image", "")  # Base64 Screenshot
            }
            self._current_trajectory.append(step_record)
        
        return obs

    def _internal_get_obs(self):
        """替代 DesktopEnv._get_obs"""
        if not self.controller:
            return {}
        
        # 定义是否需要各个部分
        require_a11y = self.config["osworld"].get("require_a11y_tree", True)
        require_terminal = self.config["osworld"].get("require_terminal", False)

        return {
            "screenshot": self.controller.get_screenshot(),
            "accessibility_tree": self.controller.get_accessibility_tree() if require_a11y else None,
            "terminal": self.controller.get_terminal_output() if require_terminal else None,
            "instruction": getattr(self, "_current_instruction", "")
        }

    # =====================================================================
    # 兼容性接口 (适配 osworld_tools.py)
    # =====================================================================

    def step(self, action: Union[str, Dict], pause: float = None):
        """适配工具调用的标准 step 接口"""
        if pause is None:
            pause = self.config.get("osworld", {}).get("sleep_after_execution", 2)
        return self._internal_step(action, pause)

    def get_obs(self):
        """适配工具调用的标准 get_obs 接口"""
        return self._internal_get_obs()

    def get_config(self, key: str) -> Any:
        """适配工具调用的配置获取接口"""
        return self.config.get(key)

    # ---------------------------------------------------------------------
    # Evaluation Logic
    # ---------------------------------------------------------------------
    def _setup_evaluators(self, evaluator_config: Dict):
        """解析 Evaluator 配置"""
        self.evaluator_config = evaluator_config
        func = evaluator_config["func"]
        
        if isinstance(func, list):
             self.metric = [getattr(metrics, f) for f in func]
        else:
             self.metric = getattr(metrics, func)
        
        self.metric_conj = evaluator_config.get("conj", "and")
        
        if "result" in evaluator_config and len(evaluator_config["result"]) > 0:
            res_conf = evaluator_config["result"]
            if isinstance(res_conf, list):
                self.result_getter = [getattr(getters, f"get_{r['type']}") for r in res_conf]
            else:
                self.result_getter = getattr(getters, f"get_{res_conf['type']}")
        else:
            self.result_getter = [None] * len(self.metric) if isinstance(self.metric, list) else None

        if "expected" in evaluator_config and len(evaluator_config["expected"]) > 0:
            exp_conf = evaluator_config["expected"]
            if isinstance(exp_conf, list):
                self.expected_getter = [getattr(getters, f"get_{e['type']}") if e else None for e in exp_conf]
            else:
                self.expected_getter = getattr(getters, f"get_{exp_conf['type']}")
        else:
            self.expected_getter = [None] * len(self.metric) if isinstance(self.metric, list) else None

        opts = evaluator_config.get("options", {})
        if isinstance(opts, list):
            self.metric_options = [o if o else {} for o in opts]
        else:
            self.metric_options = opts

    def _internal_evaluate(self) -> float:
        """替代 DesktopEnv.evaluate"""
        postconfig = self.evaluator_config.get("postconfig", [])
        if postconfig:
            self.setup_controller.setup(postconfig, False)

        if self.evaluator_config.get('func') == "infeasible":
            if len(self._action_history) > 0 and self._action_history[-1] == "FAIL":
                return 1.0
            else:
                return 0.0

        if isinstance(self.metric, list):
            results = []
            for idx, metric_fn in enumerate(self.metric):
                try:
                    res_getter = self.result_getter[idx]
                    res_conf = self.evaluator_config["result"][idx]
                    result_state = res_getter(self, res_conf)
                except FileNotFoundError:
                    if self.metric_conj == 'and': return 0.0
                    continue

                if self.expected_getter and self.evaluator_config.get("expected"):
                    exp_getter = self.expected_getter[idx]
                    exp_conf = self.evaluator_config["expected"][idx]
                    expected_state = exp_getter(self, exp_conf) if exp_getter else None
                    score = metric_fn(result_state, expected_state, **self.metric_options[idx])
                else:
                    score = metric_fn(result_state, **self.metric_options[idx])

                if self.metric_conj == 'and' and float(score) == 0.0:
                    return 0.0
                elif self.metric_conj == 'or' and float(score) == 1.0:
                    return 1.0
                else:
                    results.append(float(score))

            if not results: return 0.0
            return sum(results) / len(results) if self.metric_conj == 'and' else max(results)
        else:
            try:
                res_getter = self.result_getter
                res_conf = self.evaluator_config["result"]
                result_state = res_getter(self, res_conf)
            except FileNotFoundError:
                return 0.0

            if self.expected_getter and self.evaluator_config.get("expected"):
                exp_getter = self.expected_getter
                exp_conf = self.evaluator_config["expected"]
                expected_state = exp_getter(self, exp_conf)
                score = self.metric(result_state, expected_state, **self.metric_options)
            else:
                score = self.metric(result_state, **self.metric_options)

            return float(score)

    def _internal_start_recording(self):
        if self.controller: self.controller.start_recording()

    def _internal_end_recording(self, output_path: str):
        if self.controller: self.controller.end_recording(output_path)

    # ---------------------------------------------------------------------
    # Observation formatting / Tools / Lifecycle (Keep existing)
    # ---------------------------------------------------------------------

    def _encode_image(self, image_content: bytes) -> str:
        if not image_content: return ""
        return base64.b64encode(image_content).decode("utf-8")

    def _linearize_accessibility_tree(self, accessibility_tree: Dict[str, Any]) -> str:
        def _traverse(node, depth=0):
            lines = []
            indent = "  " * depth
            role = node.get("role", "unknown")
            name = node.get("name", "")
            description = node.get("description", "")
            node_info = f"{indent}[{role}]"
            if name: node_info += f" {name}"
            if description: node_info += f" - {description}"
            lines.append(node_info)
            for child in node.get("children", []):
                if isinstance(child, dict):
                    lines.extend(_traverse(child, depth + 1))
            return lines

        if not accessibility_tree: return ""
        if isinstance(accessibility_tree, (str, bytes, bytearray)):
            try:
                return accessibility_tree.decode("utf-8") if isinstance(accessibility_tree, (bytes, bytearray)) else accessibility_tree
            except UnicodeDecodeError:
                return repr(accessibility_tree)
        if not isinstance(accessibility_tree, dict): return str(accessibility_tree)
        return "\n".join(_traverse(accessibility_tree))

    def _trim_accessibility_tree(self, linearized_tree: str, max_tokens: int) -> str:
        max_chars = max_tokens * 4
        if len(linearized_tree) <= max_chars: return linearized_tree
        return linearized_tree[:max_chars] + "\n...[accessibility tree truncated]"

    def _format_observation_for_llm(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        osworld_config = self.config.get("osworld", {})
        max_tokens = osworld_config.get("a11y_tree_max_tokens", 10000)
        a11y_tree = obs.get("accessibility_tree", {})
        linearized = self._linearize_accessibility_tree(a11y_tree)
        trimmed = self._trim_accessibility_tree(linearized, max_tokens)
        base64_image = self._encode_image(obs.get("screenshot", b""))
        return {"screenshot": base64_image, "a11y_tree": trimmed}

    def format_observation_by_type(self, raw_obs: Dict[str, Any], output_format: str = "dict") -> Union[Dict[str, Any], List[Observation]]:
        if not raw_obs: return {} if output_format == "dict" else []
        osworld_config = self.config.get("osworld", {})
        observation_type = osworld_config.get("observation_type", "screenshot_a11y_tree")
        include_screenshot = observation_type in {"screenshot", "screenshot_a11y_tree", "som"}
        include_a11y_tree = observation_type in {"a11y_tree", "screenshot_a11y_tree", "som"}
        formatted = self._format_observation_for_llm(raw_obs)
        base64_image = formatted.get("screenshot", "") if include_screenshot else ""
        linearized_a11y_tree = formatted.get("a11y_tree", "") if include_a11y_tree else ""

        if output_format == "dict":
            result = {}
            if include_a11y_tree and linearized_a11y_tree: result["text"] = linearized_a11y_tree
            if include_screenshot and base64_image: result["image"] = base64_image
            return result
        
        # For other formats (List[Observation] etc.), keep simple or expand as needed
        return {}

    # Task Lifecycle
    def env_task_init(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.controller: raise ValueError("Controller not initialized")
        task_id = task.get("id", "unknown")
        logger.info(f"Initializing OSWorld environment for task {task_id}...")
        self._current_task_id = task_id
        
        # Record Task Mapping
        if self.controller and self.controller.instance_id:
            try:
                get_instance_tracker().record_instance_task(self.controller.instance_id, task_id)
            except Exception: pass

        self._internal_reset(task)
        if self.config.get("osworld", {}).get("enable_recording", True):
            try: self._internal_start_recording()
            except Exception: pass
        
        self._current_trajectory = []
        raw_obs = self._internal_get_obs()
        if not raw_obs: return None
        formatted_obs = cast(Dict[str, Any], self.format_observation_by_type(raw_obs, output_format="dict"))
        self._current_trajectory.append({
            "step": 0, 
            "type": "initial_observation", 
            "timestamp": datetime.now().isoformat(),
            "text": formatted_obs.get("text", ""), 
            "image": formatted_obs.get("image", "")
        })
        return formatted_obs

    def env_task_end(self, task_id: str, task_output_dir: Optional[str] = None, final_answer: Optional[str] = None) -> Optional[Dict[str, Any]]:
        enable_recording = self.config.get("osworld", {}).get("enable_recording", True)
        if enable_recording and task_output_dir:
            try:
                self._internal_end_recording(os.path.join(task_output_dir, f"task_{task_id}.mp4"))
            except Exception: pass
        if task_output_dir and self._current_trajectory:
            self._save_trajectory_to_files(task_output_dir)
        self._current_trajectory = []
        self._current_task_id = None
        return {"answer": final_answer} if final_answer is not None else None
    
    def _save_trajectory_to_files(self, output_dir: str):
        """Save trajectory to jsonl"""
        file_path = os.path.join(output_dir, "trajectory.jsonl")
        with open(file_path, "w", encoding="utf-8") as f:
            for step in self._current_trajectory:
                f.write(json.dumps(step) + "\n")

    def _register_tools(self):
        """注册工具（在 Controller 可用后调用）"""
        if self.controller is None:
            raise ValueError("Controller must be set before registering tools.")
        
        action_space = self.config.get("osworld", {}).get("action_space", "computer_13")
        if action_space == "computer_13":
            self._register_computer13_tools()
        elif action_space == "pyautogui":
            self._register_pyautogui_tools()
        else:
            self._register_computer13_tools()

    def _register_computer13_tools(self):
        from tools.osworld_tools import (
            MouseMoveTool, MouseClickTool, MouseRightClickTool, MouseDoubleClickTool,
            MouseButtonTool, MouseDragTool, ScrollTool, TypeTool, KeyPressTool,
            KeyHoldTool, HotkeyTool, ControlTool
        )
        tools = [
            MouseMoveTool(self), MouseClickTool(self), MouseRightClickTool(self),
            MouseDoubleClickTool(self), MouseButtonTool(self), MouseDragTool(self),
            ScrollTool(self), TypeTool(self), KeyPressTool(self), KeyHoldTool(self),
            HotkeyTool(self), ControlTool(self)
        ]
        for tool in tools: self.register_tool(tool)

    def _register_pyautogui_tools(self):
        from tools.osworld_tools import ExecutePythonScriptTool, ControlTool
        tools = [ExecutePythonScriptTool(self), ControlTool(self)]
        for tool in tools: self.register_tool(tool)

    # =====================================================================
    # 3. 修复崩溃问题 (添加 _extract_final_answer)
    # =====================================================================
    def _extract_final_answer(self, messages: List[Dict[str, Any]]) -> Optional[str]:
        """防止 AttributeError 崩溃"""
        if not messages:
            return None
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                content = msg.get("content")
                if isinstance(content, str): return content
                return str(content) if content is not None else None
        return None