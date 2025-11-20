from __future__ import annotations

import logging
import os
import time
import re
import functools
from typing import Callable, Any, Optional, Tuple
from typing import List, Dict, Union
import gymnasium as gym

from utils.desktop_env.controllers.python import PythonController
from utils.desktop_env.controllers.setup import SetupController, VMReadinessProbe
from utils.desktop_env.evaluators import metrics, getters
from utils.desktop_env.providers import create_vm_manager_and_provider
from utils.instance_tracker import get_instance_tracker

logger = logging.getLogger("desktopenv.env")

Metric = Callable[[Any, Any], float]
Getter = Callable[[gym.Env, Dict[str, Any]], Any]

MAX_RETRIES = 5 # Maximum retries for environment setup
            


def _fix_pyautogui_less_than_bug(command: str) -> str:
    """
    Fix PyAutoGUI '<' character bug by converting it to hotkey("shift", ',') calls.
    
    This fixes the known PyAutoGUI issue where typing '<' produces '>' instead.
    References:
    - https://github.com/asweigart/pyautogui/issues/198
    - https://github.com/xlang-ai/OSWorld/issues/257
    
    Args:
        command (str): The original pyautogui command
        
    Returns:
        str: The fixed command with '<' characters handled properly
    """
    # Pattern to match press('<') or press('\u003c') calls  
    press_pattern = r'pyautogui\.press\(["\'](?:<|\\u003c)["\']\)'

    # Handle press('<') calls
    def replace_press_less_than(match):
        return 'pyautogui.hotkey("shift", ",")'
    
    # First handle press('<') calls
    command = re.sub(press_pattern, replace_press_less_than, command)

    # Pattern to match typewrite calls with quoted strings
    typewrite_pattern = r'pyautogui\.typewrite\((["\'])(.*?)\1\)'
    
    # Then handle typewrite calls
    def process_typewrite_match(match):
        quote_char = match.group(1)
        content = match.group(2)
        
        # Preprocess: Try to decode Unicode escapes like \u003c to actual '<'
        # This handles cases where '<' is represented as escaped Unicode
        try:
            # Attempt to decode unicode escapes
            decoded_content = content.encode('utf-8').decode('unicode_escape')
            content = decoded_content
        except UnicodeDecodeError:
            # If decoding fails, proceed with original content to avoid breaking existing logic
            pass  # English comment: Graceful degradation - fall back to original content if decoding fails
        
        # Check if content contains '<'
        if '<' not in content:
            return match.group(0)
        
        # Split by '<' and rebuild
        parts = content.split('<')
        result_parts = []
        
        for i, part in enumerate(parts):
            if i == 0:
                # First part
                if part:
                    result_parts.append(f"pyautogui.typewrite({quote_char}{part}{quote_char})")
            else:
                # Add hotkey for '<' and then typewrite for the rest
                result_parts.append('pyautogui.hotkey("shift", ",")')
                if part:
                    result_parts.append(f"pyautogui.typewrite({quote_char}{part}{quote_char})")
        
        return '; '.join(result_parts)
    
    command = re.sub(typewrite_pattern, process_typewrite_match, command)
    
    return command


class DesktopEnv(gym.Env):
    _typeid = "DesktopEnv"
    """
    DesktopEnv with OpenAI Gym interface. It provides a desktop environment for setting and evaluating desktop automation tasks.
    """
    def __init__(
            self,
            provider_name: str = "vmware",
            region: str = None,
            path_to_vm: str = None,
            snapshot_name: str = "init_state",
            action_space: str = "pyautogui",
            cache_dir: str = "cache",
            screen_size: Tuple[int] = (int(os.environ.get("SCREEN_WIDTH", 1920)), int(os.environ.get("SCREEN_HEIGHT", 1080))),
            headless: bool = False,
            require_a11y_tree: bool = True,
            require_terminal: bool = False,
            os_type: str = "Ubuntu",
            enable_proxy: bool = False,
            client_password: str = "",
            remote_ip: Optional[str] = None,
            remote_port: Optional[int] = None,
            remote_chromium_port: Optional[int] = None,
            remote_vnc_port: Optional[int] = None,
            remote_vlc_port: Optional[int] = None,
    ):
        """
        Args:
            provider_name (str): virtualization provider name, default to "vmware"
            region (str): the region for allocate machines, work for cloud services, default to  "us-east-1"
            path_to_vm (str): path to .vmx file
            snapshot_name (str): snapshot name to revert to, default to "init_state"
            action_space (str): "computer_13" | "pyautogui"
            cache_dir (str): cache directory to cache task-related stuffs like
              reference file for evaluation
            screen_size (Tuple[int]): screen size of the VM
            headless (bool): whether to run the VM in headless mode
            require_a11y_tree (bool): whether to require accessibility tree
            require_terminal (bool): whether to require terminal output
            os_type (str): operating system type, default to "Ubuntu"
            enable_proxy (bool): whether to enable proxy support, default to False
            remote_ip (str, optional): IP address of remote VM (Attach Mode). If provided, skips VM startup.
            remote_port (int, optional): Server port of remote VM (Attach Mode), default 5000
            remote_chromium_port (int, optional): Chromium port of remote VM (Attach Mode), default 9222
            remote_vnc_port (int, optional): VNC port of remote VM (Attach Mode), default 8006
            remote_vlc_port (int, optional): VLC port of remote VM (Attach Mode), default 8080
        """
        # Initialize VM manager and vitualization provider
        self.region = region
        self.provider_name = provider_name
        self.enable_proxy = enable_proxy  # Store proxy enablement setting
        if client_password == "":
            if self.provider_name == "aws":
                self.client_password = "osworld-public-evaluation"
            else:
                self.client_password = "password"
        else:
            self.client_password = client_password

        self.screen_width = screen_size[0]
        self.screen_height = screen_size[1]

        # Default 
        self.server_port = 5000
        self.chromium_port = 9222
        self.vnc_port = 8006
        self.vlc_port = 8080
        
        # Initialize with default (no proxy) provider
        self.current_use_proxy = False
        self.manager, self.provider = create_vm_manager_and_provider(provider_name, region, use_proxy=False)

        self.os_type = os_type

        # Track whether environment has been used (step/setup) to optimize snapshot revert
        # docker, aws, gcp, azure are always unused as the emulator starts from a clean state
        # vmware, virtualbox are always used as the emulator starts from a dirty state
        if self.provider_name in {"docker", "aws", "gcp", "azure", "aliyun", "volcengine"}:
            self.is_environment_used = False
        elif self.provider_name in {"vmware", "virtualbox"}:
            self.is_environment_used = True
        else:
            raise ValueError(f"Invalid provider name: {self.provider_name}")

        # Initialize environment variables
        if path_to_vm:
            self.path_to_vm = os.path.abspath(os.path.expandvars(os.path.expanduser(path_to_vm))) \
                if provider_name in {"vmware", "virtualbox"} else path_to_vm
        else:
            self.path_to_vm = self.manager.get_vm_path(os_type=self.os_type, region=region, screen_size=(self.screen_width, self.screen_height))
        
        self.snapshot_name = snapshot_name
        self.cache_dir_base: str = cache_dir
        # todo: add the logic to get the screen size from the VM
        self.headless = headless
        self.require_a11y_tree = require_a11y_tree
        self.require_terminal = require_terminal

        # Attach Mode: If remote_ip is provided, skip VM startup and connect directly
        self.remote_ip = remote_ip
        self.remote_port = remote_port or 5000
        self.remote_chromium_port = remote_chromium_port or 9222
        self.remote_vnc_port = remote_vnc_port or 8006
        self.remote_vlc_port = remote_vlc_port or 8080

        # Initialize emulator and controller
        if self.remote_ip:
            # Attach Mode: Skip VM startup, connect directly to remote VM
            logger.info(f"Attach Mode: Connecting to remote VM at {self.remote_ip}:{self.remote_port}")
            self._attach_to_remote_vm()
        else:
            # Normal Mode: Start VM and get IP
            logger.info("Initializing...")
            self._start_emulator()

        # mode: human or machine
        self.instruction = None
        assert action_space in ["computer_13", "pyautogui", "claude_computer_use", "autoglm_computer_use"]
        self.action_space = action_space  # todo: refactor it to the ActType

        # episodic stuffs, like counters, will be updated or reset
        # when calling self.reset()
        self._traj_no: int = -1
        self._step_no: int = 0
        self.action_history: List[Dict[str, any]] = []
        self._snapshot_revert_count: int = 0
        self._pending_snapshot_ip_log: bool = False

    def _attach_to_remote_vm(self):
        """
        Attach Mode: Connect to a remote VM without starting it locally.
        This is used in distributed worker architecture where the Manager starts VMs
        and Workers connect to them.
        """
        if not hasattr(self, "_snapshot_revert_count"):
            self._snapshot_revert_count = 0
        if not hasattr(self, "_pending_snapshot_ip_log"):
            self._pending_snapshot_ip_log = False
        
        # Use provided remote IP and ports
        self.vm_ip = self.remote_ip
        self.server_port = self.remote_port
        self.chromium_port = self.remote_chromium_port
        self.vnc_port = self.remote_vnc_port
        self.vlc_port = self.remote_vlc_port
        
        # Initialize controller with remote IP
        # Note: path_to_vm may be None in attach mode, use remote_ip as instance_id if needed
        instance_id = self.path_to_vm if self.path_to_vm else self.remote_ip
        self.controller = PythonController(
            vm_ip=self.vm_ip,
            server_port=self.server_port,
            instance_id=instance_id
        )
        
        # Build readiness probe (may be None if provider doesn't support it)
        readiness_probe = self._build_vm_readiness_probe()
        self.setup_controller = SetupController(
            vm_ip=self.vm_ip,
            server_port=self.server_port,
            chromium_port=self.chromium_port,
            vlc_port=self.vlc_port,
            cache_dir=self.cache_dir_base,
            client_password=self.client_password,
            screen_width=self.screen_width,
            screen_height=self.screen_height,
            vm_readiness_probe=readiness_probe
        )
        
        logger.info(
            f"Attached to remote VM: ip={self.vm_ip} "
            f"(server_port={self.server_port}, chromium_port={self.chromium_port})"
        )

    def _start_emulator(self):
        if not hasattr(self, "_snapshot_revert_count"):
            self._snapshot_revert_count = 0
        if not hasattr(self, "_pending_snapshot_ip_log"):
            self._pending_snapshot_ip_log = False
        try:
            # Power on the virtual machine
            self.provider.start_emulator(self.path_to_vm, self.headless, self.os_type)

            # Get the ip from the virtual machine, and setup the controller
            vm_ip_ports = self.provider.get_ip_address(self.path_to_vm).split(':')
            self.vm_ip = vm_ip_ports[0]
            # Get the ports from the virtual machine (for Docker provider only)
            if len(vm_ip_ports) > 1:
                self.server_port = int(vm_ip_ports[1])
                self.chromium_port = int(vm_ip_ports[2])
                self.vnc_port = int(vm_ip_ports[3])
                self.vlc_port = int(vm_ip_ports[4])
            
            # 记录实例IP地址
            try:
                if self.path_to_vm and self.vm_ip:
                    tracker = get_instance_tracker()
                    tracker.record_instance_ip(self.path_to_vm, self.vm_ip)
            except Exception as e:
                logger.warning(f"Failed to record instance IP: {e}")
            
            self.controller = PythonController(vm_ip=self.vm_ip, server_port=self.server_port, instance_id=self.path_to_vm)
            readiness_probe = self._build_vm_readiness_probe()
            self.setup_controller = SetupController(vm_ip=self.vm_ip, server_port=self.server_port, chromium_port=self.chromium_port, vlc_port=self.vlc_port, cache_dir=self.cache_dir_base, client_password=self.client_password, screen_width=self.screen_width, screen_height=self.screen_height, vm_readiness_probe=readiness_probe)
            if self._pending_snapshot_ip_log:
                logger.info(
                    f"[snapshot #{self._snapshot_revert_count}] vm_id={self.path_to_vm} "
                    f"ip={self.vm_ip} (server_port={self.server_port})"
                )
                self._pending_snapshot_ip_log = False

        except Exception as e:
            try:
                self.provider.stop_emulator(self.path_to_vm)
            except Exception as stop_err:
                logger.warning(f"Cleanup after interrupt failed: {stop_err}")
            raise

    def _revert_to_snapshot(self):
        # Revert to certain snapshot of the virtual machine, and refresh the path to vm and ip of vm
        # due to the fact it could be changed when implemented by cloud services
        next_revert_id = self._snapshot_revert_count + 1
        previous_vm_path = self.path_to_vm
        path_to_vm = self.provider.revert_to_snapshot(self.path_to_vm, self.snapshot_name)
        logger.info(
            f"[snapshot #{next_revert_id}] revert_to_snapshot completed "
            f"(provider={self.provider_name}, previous_vm={previous_vm_path}, new_vm={path_to_vm})"
        )
        self._snapshot_revert_count = next_revert_id
        self._pending_snapshot_ip_log = True
        if path_to_vm:
            if path_to_vm != self.path_to_vm:
                # Ensure VM registry tracks the new instance id returned by provider
                try:
                    self.manager.delete_vm(self.path_to_vm, self.region)
                except Exception as exc:
                    logger.warning("Failed to delete old VM entry %s: %s", self.path_to_vm, exc)
                try:
                    self.manager.add_vm(path_to_vm, self.region)
                    self.manager.occupy_vm(path_to_vm, os.getpid(), self.region)
                except Exception as exc:
                    logger.warning("Failed to register new VM entry %s: %s", path_to_vm, exc)
                self.path_to_vm = path_to_vm
                # 注意：revert_to_snapshot() 内部已经通过 _allocate_vm() 记录了实例创建
                # 这里不需要重复记录，但可以记录IP地址更新
        else:
            logger.warning(
                "[snapshot #%d] provider did not return a new vm identifier; "
                "will keep using previous vm id %s until next allocation.",
                self._snapshot_revert_count,
                self.path_to_vm,
            )

        readiness_probe = self._build_vm_readiness_probe()
        if readiness_probe and self.path_to_vm:
            logger.info(
                "[snapshot #%d] waiting for provider readiness probe before continuing...",
                self._snapshot_revert_count,
            )
            readiness_probe.wait_until_ready()
        
        # 重置后，无论实例ID是否改变，都需要重新获取IP地址并更新Controller
        # 这对于云厂商（如阿里云、AWS）特别重要，因为重置后IP地址可能会改变
        # 即使实例ID不变，IP地址也可能因为重新分配而改变
        logger.info(
            f"[snapshot #{next_revert_id}] Resetting VM, updating IP address and controllers..."
        )
        try:
            # 确保VM已启动
            self.provider.start_emulator(self.path_to_vm, self.headless, self.os_type)
            
            # 获取新的IP地址（无论实例ID是否改变，IP都可能变化）
            vm_ip_ports = self.provider.get_ip_address(self.path_to_vm).split(':')
            new_vm_ip = vm_ip_ports[0]
            
            # 检查IP是否真的改变了
            ip_changed = (not hasattr(self, 'vm_ip')) or (self.vm_ip != new_vm_ip)
            
            if ip_changed:
                logger.info(
                    f"[snapshot #{next_revert_id}] IP address changed: {getattr(self, 'vm_ip', 'N/A')} -> {new_vm_ip}"
                )
            else:
                logger.info(
                    f"[snapshot #{next_revert_id}] IP address unchanged: {new_vm_ip}"
                )
            
            # 更新IP地址和端口
            self.vm_ip = new_vm_ip
            if len(vm_ip_ports) > 1:
                self.server_port = int(vm_ip_ports[1])
                self.chromium_port = int(vm_ip_ports[2])
                self.vnc_port = int(vm_ip_ports[3])
                self.vlc_port = int(vm_ip_ports[4])
            
            # 记录更新的IP地址
            try:
                if self.path_to_vm and new_vm_ip:
                    tracker = get_instance_tracker()
                    tracker.record_instance_ip(self.path_to_vm, new_vm_ip)
            except Exception as e:
                logger.warning(f"Failed to record instance IP: {e}")
            
            # 重新创建Controller以使用新的IP地址（即使IP没变，也要确保Controller是最新的）
            self.controller = PythonController(vm_ip=self.vm_ip, server_port=self.server_port, instance_id=self.path_to_vm)
            readiness_probe_updated = self._build_vm_readiness_probe()
            self.setup_controller = SetupController(
                vm_ip=self.vm_ip,
                server_port=self.server_port,
                chromium_port=self.chromium_port,
                vlc_port=self.vlc_port,
                cache_dir=self.cache_dir_base,
                client_password=self.client_password,
                screen_width=self.screen_width,
                screen_height=self.screen_height,
                vm_readiness_probe=readiness_probe_updated
            )
            
            logger.info(
                f"[snapshot #{next_revert_id}] IP address and controllers updated: {new_vm_ip} "
                f"(server_port={self.server_port})"
            )
        except Exception as exc:
            logger.error(
                f"[snapshot #{next_revert_id}] Failed to update IP address after reset: {exc}",
                exc_info=True
            )
            # 不抛出异常，让后续流程继续，但会在连接时失败并重试

    def _save_state(self, snapshot_name=None):
        # Save the current virtual machine state to a certain snapshot name
        self.provider.save_state(self.path_to_vm, snapshot_name)

    def _fetch_status_for_probe(self, provider_status_fetcher):
        """
        供 VMReadinessProbe 使用的实例方法，避免局部函数导致的 pickling 问题。
        """
        return provider_status_fetcher(self.path_to_vm)

    def _build_vm_readiness_probe(self) -> Optional[VMReadinessProbe]:
        """
        若云厂商实现了实例状态查询，则构造 readiness probe，避免只依赖 HTTP 探活。
        """
        status_fetcher = getattr(self.provider, "get_instance_status", None)
        if not callable(status_fetcher):
            return None

        def _parse_int(env_name: str, default: int) -> int:
            value = os.getenv(env_name)
            if value is None:
                return default
            try:
                return int(value)
            except ValueError:
                logger.warning("Invalid value for %s: %s, fallback to %d", env_name, value, default)
                return default

        timeout = _parse_int("VM_READINESS_TIMEOUT", 300)
        interval = _parse_int("VM_READINESS_INTERVAL", 5)
        ready_states = getattr(self.provider, "READY_STATES", ("Running",))

        readiness_fetcher = functools.partial(self._fetch_status_for_probe, status_fetcher)

        return VMReadinessProbe(
            status_fetcher=readiness_fetcher,
            ready_states=list(ready_states),
            timeout=timeout,
            interval=interval,
            label=f"{self.provider_name}:{self.path_to_vm}",
        )

    def close(self):
        # 在 Attach 模式下，不关闭 VM（VM 由 Manager 管理）
        if self.remote_ip:
            logger.info(f"Attach Mode: Skipping VM close (VM managed by Manager)")
            return
        
        # 记录实例清理
        try:
            if self.path_to_vm:
                tracker = get_instance_tracker()
                tracker.record_instance_cleaned(self.path_to_vm)
        except Exception as e:
            logger.warning(f"Failed to record instance cleanup: {e}")
        
        # Close (release) the virtual machine
        if self.path_to_vm:
            self.provider.stop_emulator(self.path_to_vm)

    def reset(self, task_config: Optional[Dict[str, Any]] = None, seed=None, options=None) -> Dict[str, Any]:
        
        # Reset to certain task in OSWorld
        logger.info("Resetting environment...")
        logger.info("Switching task...")
        logger.info("Setting counters...")
        self._traj_no += 1
        self._step_no = 0
        self.action_history.clear()

        for attempt in range(MAX_RETRIES):
            # Only revert to snapshot if environment has been used (step/setup)
            # This optimization is especially important for cloud providers like AWS
            # where unnecessary snapshot operations are costly and time-consuming
            
            if task_config is not None:
                # Only consider task proxy requirement if proxy is enabled at system level
                # FIX: Adapt to BenchmarkItem structure - proxy is in metadata
                # BenchmarkItem structure: {id, question, answer, metadata: {proxy, config, evaluator, ...}}
                metadata = task_config.get("metadata", {})
                task_use_proxy = metadata.get("proxy", False) and self.enable_proxy
                if not self.enable_proxy and metadata.get("proxy", False):
                    logger.info("Task requires proxy but proxy is disabled at system level, ignoring proxy requirement.")
                
                if task_use_proxy != self.current_use_proxy:
                    # keep because get_info_from_website depend on this
                    self.current_use_proxy = task_use_proxy
            
            if self.is_environment_used:
                logger.info("Environment has been used, reverting to snapshot {}...".format(self.snapshot_name))
                self._revert_to_snapshot()
                logger.info("Starting emulator...")
                self._start_emulator()
                logger.info("Emulator started.")
                # Reset the usage flag after reverting
                self.is_environment_used = False
            else:
                logger.info("Environment is clean, skipping snapshot revert (provider: {}).".format(self.provider_name))
                # 即使环境是干净的，在VM池场景中，VM可能在池中被重置了
                # 需要检查并更新IP地址，确保Controller使用正确的IP
                # 这对于云厂商（如阿里云）特别重要，因为VM重置后IP会改变
                try:
                    # 检查当前IP是否仍然有效
                    # 如果VM在池中被重置，path_to_vm可能已经改变，需要重新获取IP
                    if self.path_to_vm:
                        logger.info("Checking and updating IP address for clean environment (VM pool scenario)...")
                        # 确保VM已启动
                        self.provider.start_emulator(self.path_to_vm, self.headless, self.os_type)
                        # 获取当前IP地址
                        vm_ip_ports = self.provider.get_ip_address(self.path_to_vm).split(':')
                        current_vm_ip = vm_ip_ports[0]
                        
                        # 检查IP是否改变
                        if hasattr(self, 'vm_ip') and self.vm_ip != current_vm_ip:
                            logger.info(
                                f"IP address changed in VM pool: {self.vm_ip} -> {current_vm_ip}, updating controllers..."
                            )
                            # 更新IP地址和端口
                            self.vm_ip = current_vm_ip
                            if len(vm_ip_ports) > 1:
                                self.server_port = int(vm_ip_ports[1])
                                self.chromium_port = int(vm_ip_ports[2])
                                self.vnc_port = int(vm_ip_ports[3])
                                self.vlc_port = int(vm_ip_ports[4])
                            
                            # 记录更新的IP地址
                            try:
                                if self.path_to_vm and current_vm_ip:
                                    tracker = get_instance_tracker()
                                    tracker.record_instance_ip(self.path_to_vm, current_vm_ip)
                            except Exception as e:
                                logger.warning(f"Failed to record instance IP: {e}")
                            
                            # 重新创建Controller以使用新的IP地址
                            self.controller = PythonController(vm_ip=self.vm_ip, server_port=self.server_port, instance_id=self.path_to_vm)
                            readiness_probe_updated = self._build_vm_readiness_probe()
                            self.setup_controller = SetupController(
                                vm_ip=self.vm_ip,
                                server_port=self.server_port,
                                chromium_port=self.chromium_port,
                                vlc_port=self.vlc_port,
                                cache_dir=self.cache_dir_base,
                                client_password=self.client_password,
                                screen_width=self.screen_width,
                                screen_height=self.screen_height,
                                vm_readiness_probe=readiness_probe_updated
                            )
                            logger.info(f"Controllers updated with new IP: {current_vm_ip}")
                        else:
                            logger.debug(f"IP address unchanged: {current_vm_ip}")
                except Exception as exc:
                    logger.warning(
                        f"Failed to check/update IP address for clean environment: {exc}. "
                        f"This is normal if VM hasn't been reset in pool."
                    )

            if task_config is not None:
                # FIX: Adapt to BenchmarkItem structure - proxy is in metadata
                metadata = task_config.get("metadata", {})
                if metadata.get("proxy", False) and self.enable_proxy:
                    # If using proxy and proxy is enabled, set up the proxy configuration
                    self.setup_controller._proxy_setup(self.client_password)
                self._set_task_info(task_config)
                self.setup_controller.reset_cache_dir(self.cache_dir)
                logger.info("Setting up environment...")
                success = self.setup_controller.setup(self.config, metadata.get("proxy", False) and self.enable_proxy)
                if success:
                    # Mark environment as used when setup is successfully executed
                    if self.config:  # Only mark as used if there were actual setup operations
                        self.is_environment_used = True
                    break
                else:
                    logger.error(
                        "Environment setup failed, retrying (%d/%d)...",
                        attempt + 1,
                        MAX_RETRIES,
                    )
                    time.sleep(5)
            else:
                break
            
        instance_info = f"[instance_id={self.path_to_vm}]" if self.path_to_vm else ""
        logger.info("%s Environment setup complete.", instance_info)

        observation = self._get_obs()
        return observation

    def _get_obs(self):
        # We provide screenshot, accessibility_tree (optional), terminal (optional), and instruction.
        # can be customized and scaled
        return {
            "screenshot": self.controller.get_screenshot(),
            "accessibility_tree": self.controller.get_accessibility_tree() if self.require_a11y_tree else None,
            "terminal": self.controller.get_terminal_output() if self.require_terminal else None,
            "instruction": self.instruction
        }

    def get_obs(self):
        return self._get_obs()

    def get_path_to_vm(self) -> Optional[str]:
        return getattr(self, "path_to_vm", None)

    def start_recording(self):
        self.controller.start_recording()

    def end_recording(self, output_path: str):
        self.controller.end_recording(output_path)

    @property
    def vm_platform(self):
        return self.controller.get_vm_platform()

    @property
    def vm_screen_size(self):
        return self.controller.get_vm_screen_size()

    def _set_task_info(self, task_config: Dict[str, Any]):
        """Set task info (proxy logic is handled in reset method)"""
        # FIX: Adapt to BenchmarkItem structure
        # BenchmarkItem has: {id, question, answer, metadata: {config, evaluator, ...}}
        # id and question are at top level, config is in metadata
        self.task_id: str = task_config["id"]
        self.cache_dir: str = os.path.join(self.cache_dir_base, self.task_id)
        os.makedirs(self.cache_dir, exist_ok=True)
        # Use "question" field from BenchmarkItem (converted from OSWorld's "instruction")
        self.instruction = task_config["question"]
        # self.instruction = task_config["instruction"]
        # FIX: config is in metadata for BenchmarkItem structure
        metadata = task_config.get("metadata", {})
        self.config = metadata.get("config", [])

        self._set_evaluator_info(task_config)

    def _set_evaluator_info(self, task_config: Dict[str, Any]):
        """Set evaluator information from task config"""
        # evaluator dict
        # func -> metric function string, or list of metric function strings
        # conj -> conjunction of multiple metrics if func is a list with length > 1, "and"/"or"
        # result -> result getter config, or list of result getter configs
        # expected (optional) -> expected getter config, or list of expected getter configs
        # options (optional) -> metric options, or list of metric options
        # if func is a str list, then result, expected (if exists), options (if exists) should also be lists of the same length
        # even if one of the metrics does not need expected or options field, it should be included in the list with None
        # FIX: Adapt to BenchmarkItem structure - evaluator is in metadata
        # Don't reassign task_config parameter, use a separate variable for metadata
        metadata = task_config.get("metadata", {})
        self.evaluator = metadata["evaluator"]
        self.metric: Metric = [getattr(metrics, func) for func in self.evaluator["func"]] \
            if isinstance(self.evaluator["func"], list) \
            else getattr(metrics, self.evaluator["func"])
        self.metric_conj: str = self.evaluator.get("conj", "and")  # take conjunction of multiple metrics
        if "result" in self.evaluator and len(self.evaluator["result"]) > 0:
            self.result_getter: Getter = [getattr(getters, "get_{:}".format(res["type"])) for res in
                                          self.evaluator["result"]] \
                if isinstance(self.evaluator["result"], list) \
                else getattr(getters, "get_{:}".format(self.evaluator["result"]["type"]))
        else:
            self.result_getter = [None] * len(self.metric) \
                if isinstance(self.metric, list) \
                else None

        if "expected" in self.evaluator and len(self.evaluator["expected"]) > 0:
            self.expected_getter: Getter = [getattr(getters, "get_{:}".format(exp["type"])) if exp else None for exp in
                                            self.evaluator["expected"]] \
                if isinstance(self.evaluator["expected"], list) \
                else getattr(getters, "get_{:}".format(self.evaluator["expected"]["type"]))
        else:
            self.expected_getter = [None] * len(self.metric) \
                if isinstance(self.metric, list) \
                else None
        self.metric_options: Union[List[Dict[str, Any]], Dict[str, Any]] = [opt if opt else {} for opt in
                                                                            self.evaluator["options"]] \
            if isinstance(self.evaluator.get("options", {}), list) \
            else self.evaluator["options"] \
            if "options" in self.evaluator \
            else [{}] * len(self.metric) \
            if isinstance(self.metric, list) \
            else {}

        assert (not isinstance(self.evaluator["func"], list)
                or (len(self.metric) == len(self.result_getter) == len(self.expected_getter) == len(
                    self.metric_options)))

    def step(self, action, pause: float=2):
        self._step_no += 1
        self.action_history.append(action)
        
        # Mark environment as used when step is called
        self.is_environment_used = True

        reward = 0  # todo: Define reward calculation for each example
        done = False  # todo: Define episode termination condition for each example
        info = {}
        logger.info(f"Step {self._step_no} in trajectory {self._traj_no} with action: {action}")
        # handle the special actions
        if action in ['WAIT', 'FAIL', 'DONE'] or (type(action) == dict and action['action_type'] in ['WAIT', 'FAIL', 'DONE']):
            if action == 'WAIT':
                time.sleep(pause)
            elif action == 'FAIL':
                done = True
                info = {"fail": True}
            elif action == 'DONE':
                done = True
                info = {"done": True}

        if self.action_space == "computer_13":
            # the set of all possible actions defined in the action representation
            self.controller.execute_action(action)
        elif self.action_space == "pyautogui" or self.action_space == "claude_computer_use":
            if action in ['WAIT', 'FAIL', 'DONE']:
                self.controller.execute_action(action)
            else:
                # the set of all possible python commands insides `pyautogui`
                if type(action) == str:
                    # Fix PyAutoGUI '<' character bug before execution
                    fixed_command = _fix_pyautogui_less_than_bug(action)
                    self.controller.execute_python_command(fixed_command)
                elif type(action) == dict:
                    # Fix PyAutoGUI '<' character bug before execution
                    fixed_command = _fix_pyautogui_less_than_bug(action['command'])
                    self.controller.execute_python_command(fixed_command)

        time.sleep(pause)
        observation = self._get_obs()

        return observation, reward, done, info

    def evaluate(self):
        """
        Evaluate whether the task is successfully completed.
        """

        postconfig = self.evaluator.get("postconfig", [])
        self.setup_controller.setup(postconfig, self.enable_proxy)
        # Mark environment as used if there were postconfig setup operations
        if postconfig:
            self.is_environment_used = True

        if self.evaluator['func'] == "infeasible":
            if len(self.action_history) > 0 and self.action_history[-1] == "FAIL":
                return 1
            else:
                return 0
        else:
            if len(self.action_history) > 0 and self.action_history[-1] == "FAIL":
                return 0

        if type(self.metric) == list:
            # Multiple metrics to evaluate whether the task is successfully completed
            results = []
            assert len(self.metric) == len(self.result_getter), "The number of metrics and result getters must be the same"
            if "expected" in self.evaluator:
                assert len(self.metric) == len(self.expected_getter), "The number of metrics and expected getters must be the same"
            for idx, metric in enumerate(self.metric):
                try:
                    config = self.evaluator["result"][idx]
                    result_state = self.result_getter[idx](self, config)
                except FileNotFoundError:
                    logger.error("File not found!")
                    if self.metric_conj == 'and':
                        return 0

                if "expected" in self.evaluator and self.expected_getter and self.evaluator["expected"]:
                    expected_state = self.expected_getter[idx](self, self.evaluator["expected"][idx])
                    metric: int = metric(result_state, expected_state, **self.metric_options[idx])
                else:
                    metric: int = metric(result_state, **self.metric_options[idx])

                if self.metric_conj == 'and' and float(metric) == 0.0:
                    return 0
                elif self.metric_conj == 'or' and float(metric) == 1.0:
                    return 1
                else:
                    results.append(metric)

            return sum(results) / len(results) if self.metric_conj == 'and' else max(results)
        else:
            # Single metric to evaluate whether the task is successfully completed
            try:
                result_state = self.result_getter(self, self.evaluator["result"])
            except FileNotFoundError:
                logger.error("File not found!")
                return 0

            if "expected" in self.evaluator and self.expected_getter and self.evaluator["expected"]:
                expected_state = self.expected_getter(self, self.evaluator["expected"])
                metric: float = self.metric(result_state, expected_state, **self.metric_options)
            else:
                metric: float = self.metric(result_state, **self.metric_options)

        return metric

    def render(self, mode='rgb_array'):
        if mode == 'rgb_array':
            return self.controller.get_screenshot()
        else:
            raise ValueError('Unsupported render mode: {}'.format(mode))
