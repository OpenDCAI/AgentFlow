import os
import logging
import time
from datetime import datetime

from alibabacloud_ecs20140526.client import Client as ECSClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ecs20140526 import models as ecs_models
from alibabacloud_tea_util.client import Client as UtilClient

from sandbox.server.backends.resources.utils.desktop_env.providers.base import Provider
from sandbox.server.backends.resources.utils.desktop_env.providers.aliyun.manager import (
    _allocate_vm,
    _wait_for_instance_running,
    _wait_until_server_ready,
)


logger = logging.getLogger("desktopenv.providers.aliyun.AliyunProvider")
logger.setLevel(logging.INFO)


class AliyunProvider(Provider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.region = os.getenv("ALIYUN_REGION", "eu-central-1")
        self.client = self._create_client()
        # Whether to use private IP instead of public IP. Default: enabled.
        # Priority: explicit kwarg > env var ALIYUN_USE_PRIVATE_IP > default True
        env_use_private = os.getenv("ALIYUN_USE_PRIVATE_IP", "1").lower() in {"1", "true", "yes", "on"}
        kw_flag = kwargs.get("use_private_ip", None)
        self.use_private_ip = env_use_private if kw_flag is None else bool(kw_flag)

    def _create_client(self) -> ECSClient:
        config = open_api_models.Config(
            access_key_id=os.getenv("ALIYUN_ACCESS_KEY_ID"),
            access_key_secret=os.getenv("ALIYUN_ACCESS_KEY_SECRET"),
            region_id=self.region,
        )
        return ECSClient(config)

    def start_emulator(self, path_to_vm: str, headless: bool, *args, **kwargs):
        logger.info("Starting Aliyun ECS instance...")

        try:
            # Check the current state of the instance
            response = self._describe_instance(path_to_vm)
            if not response.body.instances.instance:
                logger.error(f"Instance {path_to_vm} not found")
                return

            instance = response.body.instances.instance[0]
            state = instance.status
            logger.info(f"Instance {path_to_vm} current state: {state}")

            if state == "Running":
                # If the instance is already running, skip starting it
                logger.info(
                    f"Instance {path_to_vm} is already running. Skipping start."
                )
                return

            if state == "Stopped":
                # Start the instance if it's currently stopped
                req = ecs_models.StartInstanceRequest(instance_id=path_to_vm)
                self.client.start_instance(req)
                logger.info(f"Instance {path_to_vm} is starting...")

                # Wait until the instance reaches 'Running' state
                _wait_for_instance_running(self.client, path_to_vm)
                logger.info(f"Instance {path_to_vm} is now running.")
            else:
                # For all other states (Pending, Starting, etc.), log a warning
                logger.warning(
                    f"Instance {path_to_vm} is in state '{state}' and cannot be started."
                )

        except Exception as e:
            logger.error(
                f"Failed to start the Aliyun ECS instance {path_to_vm}: {str(e)}"
            )
            raise

    def get_ip_address(self, path_to_vm: str) -> str:
        logger.info("Getting Aliyun ECS instance IP address...")

        try:
            response = self._describe_instance(path_to_vm)
            if not response.body.instances.instance:
                logger.error(f"Instance {path_to_vm} not found")
                return ""

            instance = response.body.instances.instance[0]

            # Get private and public IP addresses
            private_ip = ""
            public_ip = ""

            if hasattr(instance, "vpc_attributes") and instance.vpc_attributes:
                private_ip = (
                    instance.vpc_attributes.private_ip_address.ip_address[0]
                    if instance.vpc_attributes.private_ip_address.ip_address
                    else ""
                )

            if hasattr(instance, "public_ip_address") and instance.public_ip_address:
                public_ip = (
                    instance.public_ip_address.ip_address[0]
                    if instance.public_ip_address.ip_address
                    else ""
                )

            if hasattr(instance, "eip_address") and instance.eip_address:
                public_ip = instance.eip_address.ip_address or public_ip

            # Select which IP to use based on configuration
            ip_to_use = private_ip if (self.use_private_ip and private_ip) else public_ip

            if not ip_to_use:
                logger.warning("No usable IP address available (private/public both missing)")
                return ""

            _wait_until_server_ready(ip_to_use)
            if public_ip:
                vnc_url = f"http://{public_ip}:5910/vnc.html"
                logger.info(f"🖥️  VNC Web Access URL: {vnc_url}")
                logger.info("=" * 80)
            logger.info(f"📡 Public IP: {public_ip}")
            logger.info(f"🏠 Private IP: {private_ip}")
            logger.info(f"🔧 Using IP: {'Private' if ip_to_use == private_ip else 'Public'} -> {ip_to_use}")
            logger.info("=" * 80)
            print(f"\n🌐 VNC Web Access URL: {vnc_url}")
            print(
                "📍 Please open the above address in the browser "
                "for remote desktop access\n"
            )

            return ip_to_use

        except Exception as e:
            logger.error(
                f"Failed to retrieve IP address for the instance {path_to_vm}: {str(e)}"
            )
            raise

    def save_state(self, path_to_vm: str, snapshot_name: str):
        logger.info("Saving Aliyun ECS instance state...")

        try:
            req = ecs_models.CreateImageRequest(
                region_id=self.region,
                instance_id=path_to_vm,
                image_name=snapshot_name,
                description=f"Snapshot created at {datetime.now().isoformat()}",
            )
            response = self.client.create_image(req)
            image_id = response.body.image_id
            logger.info(
                f"Image {image_id} created successfully from instance {path_to_vm}."
            )
            return image_id

        except Exception as e:
            logger.error(
                f"Failed to create image from the instance {path_to_vm}: {str(e)}"
            )
            raise

    def revert_to_snapshot(self, path_to_vm: str, snapshot_name: str):
        logger.info(f"Reverting Aliyun ECS instance to snapshot: {snapshot_name}...")

        # --- 尝试策略 A: 快速回滚 (ResetDisk) ---
        if snapshot_name and snapshot_name.startswith("s-"):
            logger.info(f"⚡ Attempting FAST ROLLBACK (ResetDisk) with snapshot {snapshot_name}...")
            try:
                # 1. 确保实例处于稳定状态
                self._wait_until_instance_stable(path_to_vm)
                
                # 2. 停止实例 (Stop Instance)
                status = self._get_instance_status(path_to_vm)
                if status == "Running":
                    logger.info(f"Stopping instance {path_to_vm} before disk rollback...")
                    stop_req = ecs_models.StopInstanceRequest(instance_id=path_to_vm, force_stop=True)
                    self.client.stop_instance(stop_req)
                    self._wait_for_instance_status(path_to_vm, "Stopped") 
                elif status != "Stopped":
                    self._wait_for_instance_status(path_to_vm, "Stopped") 
                
                # 3. 获取系统盘 ID
                system_disk_id = self._get_system_disk_id(path_to_vm)
                
                # 4. 执行云盘回滚
                logger.info(f"Rolling back disk {system_disk_id} using snapshot ID {snapshot_name}...")
                reset_disk_req = ecs_models.ResetDiskRequest(
                    disk_id=system_disk_id,
                    snapshot_id=snapshot_name
                )
                self.client.reset_disk(reset_disk_req)
                
                # 等待回滚完成
                self._wait_for_disk_status(system_disk_id, target_status="In_use")

                # 5. 启动实例
                logger.info(f"Starting instance {path_to_vm} after disk rollback...")
                start_req = ecs_models.StartInstanceRequest(instance_id=path_to_vm)
                self.client.start_instance(start_req)
                
                # 6. 等待就绪
                _wait_for_instance_running(self.client, path_to_vm)
                
                # 更新 IP 记录
                # ip_address = self.get_ip_address(path_to_vm)
                # if ip_address:
                #     pass # Tracker removed

                return path_to_vm

            except Exception as e:
                logger.warning(f"⚠️ Fast rollback failed (Snapshot: {snapshot_name}): {e}")
                logger.warning("🔄 Falling back to DELETE & RECREATE strategy...")
                # 这里不 raise，而是让代码继续向下执行，进入策略 B
        
        else:
            logger.info(f"🐢 Snapshot name '{snapshot_name}' is not a valid ID format. Using DELETE & RECREATE strategy.")

        # --- 尝试策略 B: 慢速重建 (Delete & Recreate) ---
        # 如果策略 A 成功，上面已经 return 了，不会执行到这里
        # 如果策略 A 失败（或者根本没尝试），则执行这里
        
        try:
            # Step 1: 确保旧实例状态稳定以便删除
            try:
                self._wait_until_instance_stable(path_to_vm)
            except Exception as e:
                logger.warning(f"Wait for stable failed ({e}), attempting force delete anyway...")

            # Step 2: 删除旧实例
            self._delete_instance_with_retries(path_to_vm)

            # Step 3: 基于基础镜像创建新实例
            new_instance_id = _allocate_vm()
            logger.info(f"Instance {new_instance_id} recreated successfully.")

            # 获取新实例 IP
            # ip_address = self.get_ip_address(new_instance_id)
            
            # if ip_address:
            #     pass # Tracker removed

            return new_instance_id

        except Exception as e:
            # 如果连重建都失败了，那就是真的失败了
            logger.error(f"❌ Both rollback strategies failed for {path_to_vm}: {str(e)}")
            raise

    def stop_emulator(self, path_to_vm: str, region: str = None):
        logger.info(f"Stopping Aliyun ECS instance {path_to_vm}...")

        # 记录实例清理（在实际删除前记录）
        # Tracker removed

        try:
            req = ecs_models.DeleteInstancesRequest(
                region_id=self.region, instance_id=[path_to_vm], force=True
            )
            self.client.delete_instances(req)
            logger.info(f"Instance {path_to_vm} has been deleted.")

        except Exception as e:
            logger.error(
                f"Failed to stop the Aliyun ECS instance {path_to_vm}: {str(e)}"
            )
            raise

    def _describe_instance(
        self, instance_id: str
    ) -> ecs_models.DescribeInstancesResponse:
        """Get instance details"""
        req = ecs_models.DescribeInstancesRequest(
            region_id=self.region, instance_ids=UtilClient.to_jsonstring([instance_id])
        )
        return self.client.describe_instances(req)

    def _get_instance_status(self, instance_id: str) -> str:
        response = self._describe_instance(instance_id)
        if not response.body.instances.instance:
            raise ValueError(f"Instance {instance_id} not found")
        return response.body.instances.instance[0].status

    def _get_system_disk_id(self, instance_id: str) -> str:
        """调用 DescribeDisks 获取实例的系统盘ID"""
        req = ecs_models.DescribeDisksRequest(
            region_id=self.region,
            instance_id=instance_id,
            disk_type='system'  # 筛选系统盘
        )
        # client.describe_disks() 需要手动引入 alibabacloud_ecs20140526.models
        response = self.client.describe_disks(req) 
        
        if response.body.disks.disk and response.body.disks.disk[0]:
            return response.body.disks.disk[0].disk_id
        
        raise ValueError(f"System disk not found for instance {instance_id}")

    def _wait_for_disk_status(self, disk_id: str, target_status: str = "In_use", timeout: int = 300, interval: int = 5):
        """
        等待云盘恢复到指定状态 (例如回滚完成后的 'In_use' 状态)
        """
        start_time = time.time()
        logger.info(f"Waiting for disk {disk_id} to become '{target_status}'...")
        
        while True:
            try:
                # 查询指定磁盘的状态
                req = ecs_models.DescribeDisksRequest(
                    region_id=self.region,
                    disk_ids=UtilClient.to_jsonstring([disk_id])
                )
                response = self.client.describe_disks(req)
                
                if response.body.disks.disk:
                    current_status = response.body.disks.disk[0].status
                    
                    if current_status == target_status:
                        logger.info(f"Disk {disk_id} status is now '{target_status}'. Rollback complete.")
                        return
                    
                    # 打印中间状态 (如 Resetting)
                    logger.info(f"Disk {disk_id} status is '{current_status}', waiting for '{target_status}'... ({int(time.time() - start_time)}s)")
                else:
                    logger.warning(f"Disk {disk_id} not found during wait.")

            except Exception as e:
                logger.warning(f"Error checking disk status: {e}")

            # 超时检查
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Disk {disk_id} failed to reach '{target_status}' within {timeout}s.")
            
            time.sleep(interval)

    def _wait_for_instance_status(self, instance_id: str, target_status: str, timeout: int = 300, interval: int = 5):
        """等待实例达到指定状态 (如 'Stopped')"""
        start_time = time.time()
        while True:
            status = self._get_instance_status(instance_id)
            if status == target_status:
                logger.info(f"Instance {instance_id} status is now '{target_status}'.")
                return status
            
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Instance {instance_id} failed to reach '{target_status}' state within {timeout}s. Current status: {status}"
                )
            logger.info(f"Instance {instance_id} status is '{status}', waiting for '{target_status}'... ({int(elapsed)}s elapsed)")
            time.sleep(interval)

    def get_instance_status(self, instance_id: str) -> str:
        """
        对外暴露的实例状态查询，用于构建更智能的就绪检测。
        """
        return self._get_instance_status(instance_id)

    def _wait_until_instance_stable(
        self,
        instance_id: str,
        pending_states = ("Initializing", "Pending", "Starting", "Stopping"),
        timeout: int = 300,
        interval: int = 5,
    ) -> str:
        """
        等待实例脱离初始化/过渡状态，避免在删除/快照操作时触发 IncorrectInstanceStatus 错误。
        """
        start_time = time.time()
        while True:
            status = self._get_instance_status(instance_id)
            if status not in pending_states:
                logger.info(f"Instance {instance_id} status is now '{status}', proceed with snapshot revert.")
                return status

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Instance {instance_id} still in transitional state '{status}' after {timeout}s."
                )

            logger.info(
                f"Instance {instance_id} status '{status}' not ready for deletion, waiting {interval}s..."
            )
            time.sleep(interval)

    def _delete_instance_with_retries(
        self,
        instance_id: str,
        max_attempts: int = 5,
        backoff_seconds: int = 5,
    ) -> None:
        """
        删除实例时增加重试，避免 Aliyun 返回 IncorrectInstanceStatus.Initializing 导致任务失败。
        """
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            try:
                logger.info(f"[DeleteInstance] Attempt {attempt}/{max_attempts} for {instance_id}")
                req = ecs_models.DeleteInstancesRequest(
                    region_id=self.region,
                    instance_id=[instance_id],
                    force=True,
                )
                self.client.delete_instances(req)
                logger.info(f"Old instance {instance_id} has been deleted.")
                return
            except Exception as exc:
                message = str(exc)
                if "IncorrectInstanceStatus.Initializing" in message:
                    wait_time = backoff_seconds * attempt
                    logger.warning(
                        f"Instance {instance_id} still initializing during deletion "
                        f"(attempt {attempt}/{max_attempts}), waiting {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    self._wait_until_instance_stable(instance_id)
                    continue
                raise

        raise TimeoutError(
            f"Failed to delete instance {instance_id} after {max_attempts} attempts due to initializing state."
        )