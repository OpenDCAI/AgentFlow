"""
实例跟踪工具 - 记录所有创建的实例ID、IP地址以及创建和清理时间
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import threading

logger = logging.getLogger("instance_tracker")

# 线程锁，确保多进程/多线程环境下文件写入安全
_file_lock = threading.Lock()


class InstanceTracker:
    """实例跟踪器，用于记录实例的创建和清理信息"""
    
    def __init__(self, output_file: str = "/home/lb/AgentFlow/results/instance_jsonl/instance.jsonl"):
        """
        初始化实例跟踪器
        
        Args:
            output_file: 输出文件路径，每行一个JSON对象
        """
        self.output_file = output_file
        # 确保目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        logger.info(f"InstanceTracker initialized, output file: {output_file}")
    
    def record_instance_created(
        self,
        instance_id: str,
        ip_address: Optional[str] = None,
        provider: Optional[str] = None,
        region: Optional[str] = None
    ) -> None:
        """
        记录实例创建信息
        
        Args:
            instance_id: 实例ID
            ip_address: IP地址（如果已获取）
            provider: 云服务提供商名称（如 aliyun, aws等）
            region: 区域
        """
        create_time = datetime.now().isoformat()
        
        instance_info = {
            "instance_id": instance_id,
            "ip_address": ip_address,
            "provider": provider,
            "region": region,
            "create_time": create_time,
            "cleanup_time": None,
            "current_task_id": None,
            "task_history": [],
        }
        
        self._write_instance_info(instance_info)
        logger.info(f"Recorded instance creation: {instance_id} at {create_time}")
    
    def record_instance_ip(
        self,
        instance_id: str,
        ip_address: str
    ) -> None:
        """
        更新实例的IP地址（当IP地址获取到后调用）
        
        注意：由于JSONL格式是追加模式，这里会添加一条新记录
        保持原有记录不变，新记录包含更新的IP地址
        
        Args:
            instance_id: 实例ID
            ip_address: IP地址
        """
        update_time = datetime.now().isoformat()
        
        # 读取现有记录，找到对应实例并更新
        instances = self._read_all_instances()
        
        # 查找是否有未清理的实例记录
        updated = False
        for inst in instances:
            if inst.get("instance_id") == instance_id and inst.get("cleanup_time") is None:
                # 如果IP地址不同，创建更新记录
                if inst.get("ip_address") != ip_address:
                    inst["ip_address"] = ip_address
                    inst["ip_update_time"] = update_time
                    # 重写所有记录
                    self._rewrite_all_instances(instances)
                    updated = True
                    logger.info(f"Updated IP address for instance {instance_id}: {ip_address}")
                    break
        
        # 如果没有找到记录，创建新记录
        if not updated:
            instance_info = {
                "instance_id": instance_id,
                "ip_address": ip_address,
                "ip_update_time": update_time,
                "create_time": update_time,  # 如果没有创建记录，使用当前时间
                "cleanup_time": None,
                "current_task_id": None,
                "task_history": [],
            }
            self._write_instance_info(instance_info)
            logger.info(f"Recorded IP address for instance {instance_id}: {ip_address}")
    
    def record_instance_task(
        self,
        instance_id: str,
        task_id: str
    ) -> None:
        """
        记录实例与某个 task 的关联关系，用于事后追踪。

        Args:
            instance_id: 实例ID
            task_id: 任务ID
        """
        assign_time = datetime.now().isoformat()

        instances = self._read_all_instances()
        for inst in instances:
            if inst.get("instance_id") == instance_id and inst.get("cleanup_time") is None:
                history = inst.setdefault("task_history", [])
                if not isinstance(history, list):
                    history = []
                    inst["task_history"] = history
                history.append({"task_id": task_id, "assigned_time": assign_time})
                inst["current_task_id"] = task_id
                inst["last_task_assigned_time"] = assign_time
                self._rewrite_all_instances(instances)
                logger.info(f"Recorded task {task_id} for instance {instance_id}")
                return

        # 如果实例记录不存在，创建一个最小记录
        instance_info = {
            "instance_id": instance_id,
            "ip_address": None,
            "create_time": assign_time,
            "cleanup_time": None,
            "current_task_id": task_id,
            "last_task_assigned_time": assign_time,
            "task_history": [{"task_id": task_id, "assigned_time": assign_time}],
        }
        self._write_instance_info(instance_info)
        logger.info(f"Recorded task {task_id} for new instance entry {instance_id}")

    def record_instance_cleaned(
        self,
        instance_id: str
    ) -> None:
        """
        记录实例清理信息
        
        Args:
            instance_id: 实例ID
        """
        cleanup_time = datetime.now().isoformat()
        
        # 读取现有记录，找到对应实例并更新清理时间
        instances = self._read_all_instances()
        
        for inst in instances:
            if inst.get("instance_id") == instance_id and inst.get("cleanup_time") is None:
                inst["cleanup_time"] = cleanup_time
                inst["current_task_id"] = None
                # 重写所有记录（更新清理时间）
                self._rewrite_all_instances(instances)
                logger.info(f"Recorded instance cleanup: {instance_id} at {cleanup_time}")
                return
        
        # 如果没有找到记录，创建新记录
        instance_info = {
            "instance_id": instance_id,
            "ip_address": None,
            "create_time": None,
            "cleanup_time": cleanup_time
        }
        self._write_instance_info(instance_info)
        logger.info(f"Recorded cleanup for unknown instance: {instance_id} at {cleanup_time}")
    
    def _write_instance_info(self, instance_info: Dict[str, Any]) -> None:
        """将实例信息写入JSONL文件（追加模式）"""
        with _file_lock:
            try:
                with open(self.output_file, "a", encoding="utf-8") as f:
                    json_line = json.dumps(instance_info, ensure_ascii=False)
                    f.write(json_line + "\n")
            except Exception as e:
                logger.error(f"Failed to write instance info to {self.output_file}: {e}")
    
    def _read_all_instances(self) -> list:
        """读取所有实例记录"""
        instances = []
        if not os.path.exists(self.output_file):
            return instances
        
        with _file_lock:
            try:
                with open(self.output_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                instance_info = json.loads(line)
                                instances.append(instance_info)
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse JSON line: {line}")
            except Exception as e:
                logger.error(f"Failed to read instance info from {self.output_file}: {e}")
        
        return instances
    
    def _rewrite_all_instances(self, instances: list) -> None:
        """重写所有实例记录（用于更新）"""
        with _file_lock:
            try:
                # 使用临时文件确保原子性
                temp_file = self.output_file + ".tmp"
                with open(temp_file, "w", encoding="utf-8") as f:
                    for instance_info in instances:
                        json_line = json.dumps(instance_info, ensure_ascii=False)
                        f.write(json_line + "\n")
                
                # 原子替换
                os.replace(temp_file, self.output_file)
            except Exception as e:
                logger.error(f"Failed to rewrite instance info to {self.output_file}: {e}")


# 全局实例跟踪器单例
_global_tracker: Optional[InstanceTracker] = None


def get_instance_tracker() -> InstanceTracker:
    """获取全局实例跟踪器单例"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = InstanceTracker()
    return _global_tracker

