# src/utils/resource_pools/vm_pool.py
# -*- coding: utf-8 -*-
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from utils.desktop_env.providers import create_vm_manager_and_provider
from utils.resource_pools.base import AbstractPoolManager, ResourceEntry, ResourceStatus

logger = logging.getLogger(__name__)


@dataclass
class VMResourceEntry(ResourceEntry):
    """VM 特有的资源条目"""
    ip: Optional[str] = None
    port: int = 5000
    chromium_port: int = 9222
    vnc_port: int = 8006
    vlc_port: int = 8080
    path_to_vm: Optional[str] = None


class VMPoolImpl(AbstractPoolManager):
    """
    VM 池资源管理器实现 (Server 端)
    继承 AbstractPoolManager，实现 VM 具体逻辑。
    """
    def __init__(
        self,
        num_vms: int = 5,
        provider_name: str = "aliyun",
        region: Optional[str] = None,
        path_to_vm: Optional[str] = None,
        snapshot_name: str = "init_state",
        action_space: str = "computer_13",
        screen_size: Tuple[int, int] = (1920, 1080),
        headless: bool = True,
        require_a11y_tree: bool = True,
        require_terminal: bool = False,
        os_type: str = "Ubuntu",
        client_password: str = "password",
        **kwargs,
    ):
        # 初始化基类
        super().__init__(num_items=num_vms)
        
        # 保存 VM 特定配置
        self.provider_name = provider_name
        self.region = region
        self.path_to_vm_template = path_to_vm
        self.snapshot_name = snapshot_name
        self.action_space = action_space
        self.screen_size = screen_size
        self.headless = headless
        self.require_a11y_tree = require_a11y_tree
        self.require_terminal = require_terminal
        self.os_type = os_type
        self.client_password = client_password
        self.extra_kwargs = kwargs

    def _create_resource(self, index: int) -> VMResourceEntry:
        """实现 VM 创建逻辑"""
        vm_id = f"vm_{index + 1}"
        logger.info("Initializing %s...", vm_id)
        
        manager, provider = create_vm_manager_and_provider(
            self.provider_name, self.region or "", use_proxy=False
        )

        # 准备配置
        desktop_env_kwargs = {
            "provider_name": self.provider_name,
            "region": self.region,
            "path_to_vm": self.path_to_vm_template,
            "snapshot_name": self.snapshot_name,
            "action_space": self.action_space,
            "screen_size": self.screen_size,
            "headless": self.headless,
            "require_a11y_tree": self.require_a11y_tree,
            "require_terminal": self.require_terminal,
            "os_type": self.os_type,
            "client_password": self.client_password,
            **self.extra_kwargs,
        }

        # 解析 VM 路径
        if self.path_to_vm_template:
            vm_path = self.path_to_vm_template
        else:
            vm_path = manager.get_vm_path(
                os_type=self.os_type,
                region=self.region or "",
                screen_size=self.screen_size,
            )
        
        if not vm_path:
            raise RuntimeError(f"Failed to resolve vm_path for {vm_id}")

        # 启动 VM
        provider.start_emulator(vm_path, self.headless, self.os_type)
        
        # 获取 IP
        vm_ip_ports = provider.get_ip_address(vm_path).split(":")
        vm_ip = vm_ip_ports[0]
        
        # 构造 Entry
        entry = VMResourceEntry(
            resource_id=vm_id,
            status=ResourceStatus.FREE,
            ip=vm_ip,
            port=int(vm_ip_ports[1]) if len(vm_ip_ports) > 1 else 5000,
            chromium_port=int(vm_ip_ports[2]) if len(vm_ip_ports) > 2 else 9222,
            vnc_port=int(vm_ip_ports[3]) if len(vm_ip_ports) > 3 else 8006,
            vlc_port=int(vm_ip_ports[4]) if len(vm_ip_ports) > 4 else 8080,
            path_to_vm=vm_path,
            config=desktop_env_kwargs
        )
        logger.info("✓ %s initialized: ip=%s", vm_id, vm_ip)
        return entry

    def _validate_resource(self, entry: ResourceEntry) -> bool:
        # 确保是 VM Entry 且 IP 存在
        if not isinstance(entry, VMResourceEntry): return False
        if entry.ip is None:
            logger.warning(f"VM {entry.resource_id} has no IP")
            return False
        return True

    def _get_connection_info(self, entry: ResourceEntry) -> Dict[str, Any]:
        # 返回 VM 连接信息
        assert isinstance(entry, VMResourceEntry)
        return {
            "id": entry.resource_id,
            "ip": entry.ip,
            "port": entry.port,
            "chromium_port": entry.chromium_port,
            "vnc_port": entry.vnc_port,
            "vlc_port": entry.vlc_port,
            "path_to_vm": entry.path_to_vm,
            "config": entry.config,
        }

    def _reset_resource(self, entry: ResourceEntry) -> None:
        # Revert VM Snapshot
        assert isinstance(entry, VMResourceEntry)
        if not entry.path_to_vm: return

        _, provider = create_vm_manager_and_provider(
            self.provider_name, self.region or "", use_proxy=False
        )
        
        new_vm_path = provider.revert_to_snapshot(entry.path_to_vm, self.snapshot_name)
        if new_vm_path and new_vm_path != entry.path_to_vm:
            logger.info(f"VM {entry.resource_id} path changed: {entry.path_to_vm} -> {new_vm_path}")
            entry.path_to_vm = new_vm_path

        # 重置后更新 IP
        vm_ip_ports = provider.get_ip_address(entry.path_to_vm).split(":")
        new_ip = vm_ip_ports[0]
        if new_ip != entry.ip:
            logger.info(f"VM {entry.resource_id} IP changed: {entry.ip} -> {new_ip}")
            entry.ip = new_ip
            if len(vm_ip_ports) > 1:
                entry.port = int(vm_ip_ports[1])
                # ... update other ports if needed

    def _stop_resource(self, entry: ResourceEntry) -> None:
        assert isinstance(entry, VMResourceEntry)
        if not entry.path_to_vm: return
        _, provider = create_vm_manager_and_provider(
            self.provider_name, self.region or "", use_proxy=False
        )
        provider.stop_emulator(entry.path_to_vm)