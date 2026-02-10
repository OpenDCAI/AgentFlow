# src/utils/desktop_env/providers/aliyun/manager.py
import os
import logging
import time
import signal
import threading
import multiprocessing
import requests
from datetime import datetime, timedelta, timezone

from alibabacloud_ecs20140526.client import Client as ECSClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ecs20140526 import models as ecs_models
from alibabacloud_tea_util.client import Client as UtilClient
from sandbox.server.backends.resources.utils.desktop_env.providers.base import VMManager
from sandbox.server.backends.resources.utils.desktop_env.providers.aliyun.config import ENABLE_TTL, DEFAULT_TTL_MINUTES

# 检查必要的环境变量
for env_name in [
    "ALIYUN_REGION",
    "ALIYUN_VSWITCH_ID",
    "ALIYUN_SECURITY_GROUP_ID",
    "ALIYUN_IMAGE_ID",
    "ALIYUN_ACCESS_KEY_ID",
    "ALIYUN_ACCESS_KEY_SECRET",
    "ALIYUN_INSTANCE_TYPE",
]:
    if not os.getenv(env_name):
        raise EnvironmentError(f"{env_name} must be set in the environment variables.")


logger = logging.getLogger("desktopenv.providers.aliyun.AliyunVMManager")
logger.setLevel(logging.INFO)

ALIYUN_INSTANCE_TYPE = os.getenv("ALIYUN_INSTANCE_TYPE")
ALIYUN_ACCESS_KEY_ID = os.getenv("ALIYUN_ACCESS_KEY_ID")
ALIYUN_ACCESS_KEY_SECRET = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
ALIYUN_REGION = os.getenv("ALIYUN_REGION")
ALIYUN_IMAGE_ID = os.getenv("ALIYUN_IMAGE_ID")
ALIYUN_SECURITY_GROUP_ID = os.getenv("ALIYUN_SECURITY_GROUP_ID")
ALIYUN_VSWITCH_ID = os.getenv("ALIYUN_VSWITCH_ID")
ALIYUN_RESOURCE_GROUP_ID = os.getenv("ALIYUN_RESOURCE_GROUP_ID")

WAIT_DELAY = 20
MAX_ATTEMPTS = 15


def _can_register_signals() -> bool:
    """
    signal.signal 只能在主解释器的主线程调用。BaseManager 等子进程或线程中
    调用会直接抛出 ValueError。这里做一次统一判断。
    """
    return (
        multiprocessing.current_process().name == "MainProcess"
        and threading.current_thread() is threading.main_thread()
    )


def _allocate_vm(screen_size=(1920, 1080)):
    """
    Allocate a new Aliyun ECS instance (Enhanced Logging Version)
    """
    assert screen_size == (1920, 1080), "Only 1920x1080 screen size is supported"

    config = open_api_models.Config(
        access_key_id=ALIYUN_ACCESS_KEY_ID,
        access_key_secret=ALIYUN_ACCESS_KEY_SECRET,
        region_id=ALIYUN_REGION,
    )
    client = ECSClient(config)
    instance_id = None
    
    # 信号处理逻辑
    signal_handlers_enabled = _can_register_signals()
    original_sigint_handler = None
    original_sigterm_handler = None

    if signal_handlers_enabled:
        original_sigint_handler = signal.getsignal(signal.SIGINT)
        original_sigterm_handler = signal.getsignal(signal.SIGTERM)

        def signal_handler(sig, frame):
            if instance_id:
                signal_name = "SIGINT" if sig == signal.SIGINT else "SIGTERM"
                logger.warning(f"Received {signal_name}, terminating {instance_id}...")
                try:
                    delete_request = ecs_models.DeleteInstancesRequest(
                        region_id=ALIYUN_REGION,
                        instance_ids=UtilClient.to_jsonstring([instance_id]),
                        force=True,
                    )
                    client.delete_instances(delete_request)
                    logger.info(f"Terminated {instance_id} after {signal_name}.")
                except Exception as cleanup_error:
                    logger.error(f"Cleanup failed: {cleanup_error}")

            # 恢复原有信号处理并退出
            signal.signal(signal.SIGINT, original_sigint_handler)
            signal.signal(signal.SIGTERM, original_sigterm_handler)

            if sig == signal.SIGINT:
                raise KeyboardInterrupt
            else:
                import sys
                sys.exit(0)
    else:
        signal_handler = None

    try:
        # 设置信号处理器
        if signal_handlers_enabled and signal_handler:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

        logger.info(f"Creating ECS in {ALIYUN_REGION}, Image: {ALIYUN_IMAGE_ID}")

        # TTL configuration
        ttl_enabled = ENABLE_TTL
        ttl_minutes = DEFAULT_TTL_MINUTES
        ttl_seconds = max(0, int(ttl_minutes) * 60)
        now_utc = datetime.now(timezone.utc)
        min_eta = now_utc + timedelta(minutes=30)
        raw_eta = now_utc + timedelta(seconds=ttl_seconds)
        effective_eta = raw_eta if raw_eta > min_eta else min_eta
        effective_eta = (effective_eta + timedelta(seconds=59)).replace(second=0, microsecond=0)
        auto_release_str = effective_eta.strftime('%Y-%m-%dT%H:%M:%SZ')

        def _build_request(with_ttl: bool) -> ecs_models.RunInstancesRequest:
            kwargs = dict(
                region_id=ALIYUN_REGION,
                image_id=ALIYUN_IMAGE_ID,
                instance_type=ALIYUN_INSTANCE_TYPE,
                security_group_id=ALIYUN_SECURITY_GROUP_ID,
                v_switch_id=ALIYUN_VSWITCH_ID,
                instance_name=f"OSWorld-Desktop-{int(time.time())}",
                description="OSWorld Desktop Environment Instance",
                internet_max_bandwidth_out=10,
                internet_charge_type="PayByTraffic",
                instance_charge_type="PostPaid",
                # 注意：如果您的实例类型不支持 cloud_essd，请在此处修改为 cloud_efficiency
                system_disk=ecs_models.RunInstancesRequestSystemDisk(
                    size="50", category="cloud_essd",
                ),
                deletion_protection=False,
            )
            if ALIYUN_RESOURCE_GROUP_ID:
                kwargs["resource_group_id"] = ALIYUN_RESOURCE_GROUP_ID
            if with_ttl and ttl_enabled and ttl_seconds > 0:
                kwargs["auto_release_time"] = auto_release_str
            return ecs_models.RunInstancesRequest(**kwargs)

        # 辅助函数：打印阿里云详细错误
        def log_aliyun_error(e, phase):
            logger.error(f"[{phase}] Aliyun API Error Details:")
            logger.error(f"  Exception Type: {type(e).__name__}")
            logger.error(f"  Message: {str(e)}")
            # 尝试提取阿里云 SDK 特有的错误字段
            if hasattr(e, 'code'): logger.error(f"  Code: {e.code}")
            if hasattr(e, 'message'): logger.error(f"  Msg : {e.message}")
            if hasattr(e, 'data'): logger.error(f"  Data: {e.data}")
            if hasattr(e, 'request_id'): logger.error(f"  ReqID: {e.request_id}")

        try:
            # Attempt 1: Try with TTL
            request = _build_request(with_ttl=True)
            logger.info(f"Sending RunInstances Request (TTL): {request.to_map()}") 
            response = client.run_instances(request)
        except Exception as create_err:
            log_aliyun_error(create_err, "Attempt 1 (With TTL)") 
            
            logger.warning("Retrying without TTL...")
            try:
                # Attempt 2: Retry without TTL
                request = _build_request(with_ttl=False)
                logger.info(f"Sending RunInstances Request (No TTL): {request.to_map()}") 
                response = client.run_instances(request)
            except Exception as retry_err:
                log_aliyun_error(retry_err, "Attempt 2 (No TTL)") 
                raise retry_err

        instance_ids = response.body.instance_id_sets.instance_id_set
        if not instance_ids:
            raise RuntimeError("Aliyun returned empty instance_id_set")

        instance_id = instance_ids[0]
        logger.info(f"ECS instance {instance_id} created successfully")

        # Record instance creation
        # Tracker removed

        # Wait for the instance to be running
        logger.info(f"Waiting for instance {instance_id} to be running...")
        _wait_for_instance_running(client, instance_id)
        logger.info(f"Instance {instance_id} is now Running.")

    except KeyboardInterrupt:
        logger.warning("VM allocation interrupted by user (SIGINT).")
        if instance_id:
            logger.info(f"Terminating instance {instance_id} due to interruption.")
            try:
                delete_request = ecs_models.DeleteInstancesRequest(
                    region_id=ALIYUN_REGION,
                    instance_ids=UtilClient.to_jsonstring([instance_id]),
                    force=True,
                )
                client.delete_instances(delete_request)
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup instance {instance_id}: {str(cleanup_error)}")
        raise
    except Exception as e:
        logger.error(f"Failed to allocate ECS instance: {str(e)}", exc_info=True)
        if instance_id:
            logger.info(f"Terminating instance {instance_id} due to an error.")
            try:
                delete_request = ecs_models.DeleteInstancesRequest(
                    region_id=ALIYUN_REGION,
                    instance_ids=UtilClient.to_jsonstring([instance_id]),
                    force=True,
                )
                client.delete_instances(delete_request)
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup instance {instance_id}: {str(cleanup_error)}")
        raise
    finally:
        if signal_handlers_enabled and original_sigint_handler and original_sigterm_handler:
            # Restore original signal handlers
            signal.signal(signal.SIGINT, original_sigint_handler)
            signal.signal(signal.SIGTERM, original_sigterm_handler)

    return instance_id


def _wait_for_instance_running(
    client: ECSClient, instance_id: str, max_attempts: int = MAX_ATTEMPTS
):
    """Wait for instance to reach Running state"""
    for _ in range(max_attempts):
        try:
            req = ecs_models.DescribeInstancesRequest(
                region_id=ALIYUN_REGION,
                instance_ids=UtilClient.to_jsonstring([instance_id]),
            )
            response = client.describe_instances(req)

            if response.body.instances.instance:
                instance = response.body.instances.instance[0]
                status = instance.status
                logger.info(f"Instance {instance_id} status: {status}")

                if status == "Running":
                    return
                elif status in ["Stopped", "Stopping"]:
                    start_req = ecs_models.StartInstanceRequest(instance_id=instance_id)
                    client.start_instance(start_req)
                    logger.info(f"Started instance {instance_id}")

            time.sleep(WAIT_DELAY)

        except Exception as e:
            logger.warning(f"Error checking instance status: {e}")
            time.sleep(WAIT_DELAY)

    raise TimeoutError(
        f"Instance {instance_id} did not reach Running state within {max_attempts * WAIT_DELAY} seconds"
    )


def _wait_until_server_ready(public_ip: str):
    """Wait until the server is ready"""
    for _ in range(MAX_ATTEMPTS):
        try:
            logger.info(f"Checking server status on {public_ip}...")
            response = requests.get(f"http://{public_ip}:5000/", timeout=2)
            if response.status_code == 404:
                logger.info(f"Server {public_ip} is ready")
                return
        except Exception:
            pass  # 发生异常时不立即 sleep，而是统一在循环底部 sleep
        
        # [修改点] 将 sleep 移到 try/except 块之外，确保每次重试前都等待
        time.sleep(WAIT_DELAY)

    raise TimeoutError(
        f"Server {public_ip} did not respond within {MAX_ATTEMPTS * WAIT_DELAY} seconds"
    )


class AliyunVMManager(VMManager):
    """
    Aliyun ECS VM Manager for managing virtual machines on Aliyun Cloud.

    Aliyun ECS does not need to maintain a registry of VMs, as it can dynamically allocate and deallocate VMs.
    """

    def __init__(self, **kwargs):
        self.initialize_registry()

    def initialize_registry(self, **kwargs):
        pass

    def add_vm(self, vm_path, lock_needed=True, **kwargs):
        pass

    def _add_vm(self, vm_path):
        pass

    def delete_vm(self, vm_path, lock_needed=True, **kwargs):
        pass

    def _delete_vm(self, vm_path):
        pass

    def occupy_vm(self, vm_path, pid, lock_needed=True, **kwargs):
        pass

    def _occupy_vm(self, vm_path, pid):
        pass

    def check_and_clean(self, lock_needed=True, **kwargs):
        pass

    def _check_and_clean(self):
        pass

    def list_free_vms(self, lock_needed=True, **kwargs):
        pass

    def _list_free_vms(self):
        pass

    def get_vm_path(self, screen_size=(1920, 1080), **kwargs):
        """Get a VM path (instance ID) for use"""
        logger.info(
            f"Allocating new ECS instance in region {ALIYUN_REGION} with screen size {screen_size}"
        )

        try:
            instance_id = _allocate_vm(screen_size)
            logger.info(f"Successfully allocated instance {instance_id}")
            return instance_id

        except Exception as e:
            logger.error(f"Failed to allocate instance: {str(e)}")
            raise
