import json
import logging
import os
import os.path
from pathlib import Path
import platform
import shutil
import sqlite3
import tempfile
import time
import traceback
import uuid
from datetime import datetime, timedelta
from typing import Any, Union, Optional, Callable
from typing import Dict, List

import requests
from playwright.sync_api import sync_playwright, TimeoutError
# [延迟导入] pydrive 只在 _googledrive_setup 中使用，移到函数内部导入
# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive, GoogleDriveFile, GoogleDriveFileList
# [延迟导入] requests_toolbelt 只在文件上传相关函数中使用，移到函数内部导入
# from requests_toolbelt.multipart.encoder import MultipartEncoder

from sandbox.server.backends.resources.utils.desktop_env.controllers.python import PythonController
from sandbox.server.backends.resources.utils.desktop_env.evaluators.metrics.utils import compare_urls
from sandbox.server.backends.resources.utils.desktop_env.proxy_pool import get_global_proxy_pool, init_proxy_pool
# 当前环境中没有 AWS provider，且其他 provider 暂未实现 proxy_pool
# 因此禁用代理池相关功能
_PROXY_POOL_AVAILABLE = True

_UTILS_DIR = Path(__file__).resolve().parents[2]
_DEFAULT_PROXY_CONFIG = str(_UTILS_DIR / "osworld-settings" / "proxy" / "dataimpulse.json")

PROXY_CONFIG_FILE = os.getenv("PROXY_CONFIG_FILE", _DEFAULT_PROXY_CONFIG)  # Default proxy config file

logger = logging.getLogger("desktopenv.setup")

FILE_PATH = os.path.dirname(os.path.abspath(__file__))

if _PROXY_POOL_AVAILABLE and init_proxy_pool is not None:
    init_proxy_pool(PROXY_CONFIG_FILE)  # initialize the global proxy pool
else:
    logger.info("Proxy pool provider not available; proxy setup will be disabled.")

MAX_RETRIES = 20


class VMReadinessProbe:
    """
    基于云厂商 API 的实例状态探测器，用于在 HTTP 探活前确认 VM 是否已就绪。
    """

    def __init__(
        self,
        status_fetcher: Callable[[], Optional[str]],
        ready_states: Optional[List[str]] = None,
        timeout: int = 300,
        interval: int = 5,
        label: str = "vm",
    ):
        self.status_fetcher = status_fetcher
        self.ready_states = set(ready_states or ["Running"])
        self.timeout = timeout
        self.interval = interval
        self.label = label

    def wait_until_ready(self) -> bool:
        start = time.time()
        while time.time() - start < self.timeout:
            try:
                status = self.status_fetcher()
            except Exception as exc:
                error_msg = str(exc)
                # 如果实例不存在，立即返回False，不再等待
                if "not found" in error_msg.lower():
                    logger.error(
                        "VM readiness probe (%s): instance not found, stopping probe. Error: %s",
                        self.label,
                        exc
                    )
                    return False
                logger.warning(
                    "VM readiness probe (%s) failed to fetch status: %s", self.label, exc
                )
                status = None

            if status in self.ready_states:
                logger.info(
                    "VM readiness probe (%s): status=%s, continue setup.",
                    self.label,
                    status,
                )
                return True

            logger.info(
                "VM readiness probe (%s): status=%s, waiting %ss...",
                self.label,
                status or "unknown",
                self.interval,
            )
            time.sleep(self.interval)

        logger.warning(
            "VM readiness probe (%s) timed out after %ss, falling back to HTTP polling.",
            self.label,
            self.timeout,
        )
        return False


class SetupController:
    def __init__(self, vm_ip: str, server_port: int = 5000, chromium_port: int = 9222, vlc_port: int = 8080, cache_dir: str = "cache", client_password: str = "", screen_width: int = 1920, screen_height: int = 1080, vm_readiness_probe: Optional[VMReadinessProbe] = None):
        self.vm_ip: str = vm_ip
        self.server_port: int = server_port
        self.chromium_port: int = chromium_port
        self.vlc_port: int = vlc_port
        self.http_server: str = f"http://{vm_ip}:{server_port}"
        self.http_server_setup_root: str = f"http://{vm_ip}:{server_port}/setup"
        self.cache_dir: str = cache_dir
        self.use_proxy: bool = False
        self.client_password: str = client_password
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.vm_readiness_probe = vm_readiness_probe

    def reset_cache_dir(self, cache_dir: str):
        self.cache_dir = cache_dir

    def setup(self, config: List[Dict[str, Any]], use_proxy: bool = False)-> bool:
        """
        Args:
            config (List[Dict[str, Any]]): list of dict like {str: Any}. each
              config dict has the structure like
                {
                    "type": str, corresponding to the `_{:}_setup` methods of
                      this class
                    "parameters": dict like {str, Any} providing the keyword
                      parameters
                }
        """
        self.use_proxy = use_proxy

        if self.vm_readiness_probe is not None:
            self.vm_readiness_probe.wait_until_ready()

        # make sure connection can be established
        logger.info(f"try to connect {self.http_server}")
        retry = 0
        while retry < MAX_RETRIES:
            try:
                _ = requests.get(self.http_server + "/terminal", timeout=10)
                logger.info(f"Successfully connected to {self.http_server}")
                break
            except requests.exceptions.ConnectionError as e:
                # 连接错误：可能是IP地址不存在或VM未启动
                retry += 1
                if retry < MAX_RETRIES:
                    logger.warning(
                        f"Connection failed to {self.http_server} (retry {retry}/{MAX_RETRIES}): {e}. "
                        f"This may indicate the VM IP address has changed after reset."
                    )
                    time.sleep(5)
                else:
                    logger.error(
                        f"Failed to connect to {self.http_server} after {MAX_RETRIES} retries. "
                        f"The VM IP address may have changed after reset, or the VM is not accessible."
                    )
            except Exception as e:
                # 其他异常
                retry += 1
                if retry < MAX_RETRIES:
                    logger.warning(f"Request failed (retry {retry}/{MAX_RETRIES}): {e}")
                    time.sleep(5)
                else:
                    logger.error(f"Request failed after {MAX_RETRIES} retries: {e}")
            
            if retry == MAX_RETRIES:
                return False
                

        for i, cfg in enumerate(config):
            config_type: str = cfg["type"]
            parameters: Dict[str, Any] = cfg["parameters"]

            # Assumes all the setup the functions should follow this name
            # protocol
            setup_function: str = "_{:}_setup".format(config_type)
            assert hasattr(self, setup_function), f'Setup controller cannot find init function {setup_function}'
            
            try:
                logger.info(f"Executing setup step {i+1}/{len(config)}: {setup_function}")
                getattr(self, setup_function)(**parameters)
                logger.info(f"SETUP COMPLETED: {setup_function}({str(parameters)})")
            except Exception as e:
                logger.error(f"SETUP FAILED at step {i+1}/{len(config)}: {setup_function}({str(parameters)})")
                logger.error(f"Error details: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise Exception(f"Setup step {i+1} failed: {setup_function} - {e}") from e
        
        return True

    def _download_setup(self, files: List[Dict[str, str]]):
        """
        Args:
            files (List[Dict[str, str]]): files to download. lisf of dict like
              {
                "url": str, the url to download
                "path": str, the path on the VM to store the downloaded file
              }
        """
        # [新增] 确保缓存目录存在
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

        # [延迟导入] 只在需要上传文件时才导入 requests_toolbelt
        try:
            from requests_toolbelt.multipart.encoder import MultipartEncoder
        except ImportError as e:
            logger.error(f"Failed to import requests_toolbelt: {e}")
            raise ImportError("requests_toolbelt is required for file upload operations. Install it with: pip install requests-toolbelt") from e

        for f in files:
            url: str = f["url"]
            path: str = f["path"]
            cache_path: str = os.path.join(self.cache_dir, "{:}_{:}".format(
                uuid.uuid5(uuid.NAMESPACE_URL, url),
                os.path.basename(path)))
            if not url or not path:
                raise Exception(f"Setup Download - Invalid URL ({url}) or path ({path}).")

            if not os.path.exists(cache_path):
                logger.info(f"Cache file not found, downloading from {url} to {cache_path}")
                max_retries = 3
                downloaded = False
                e = None
                for i in range(max_retries):
                    try:
                        logger.info(f"Download attempt {i+1}/{max_retries} for {url}")
                        response = requests.get(url, stream=True, timeout=300)  # Add 5 minute timeout
                        response.raise_for_status()
                        
                        # Get file size if available
                        total_size = int(response.headers.get('content-length', 0))
                        if total_size > 0:
                            logger.info(f"File size: {total_size / (1024*1024):.2f} MB")

                        downloaded_size = 0
                        with open(cache_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded_size += len(chunk)
                                    if total_size > 0 and downloaded_size % (1024*1024) == 0:  # Log every MB
                                        progress = (downloaded_size / total_size) * 100
                                        logger.info(f"Download progress: {progress:.1f}%")
                        
                        logger.info(f"File downloaded successfully to {cache_path} ({downloaded_size / (1024*1024):.2f} MB)")
                        downloaded = True
                        break

                    except requests.RequestException as e:
                        logger.error(
                            f"Failed to download {url} caused by {e}. Retrying... ({max_retries - i - 1} attempts left)")
                        # Clean up partial download
                        if os.path.exists(cache_path):
                            os.remove(cache_path)
                if not downloaded:
                    raise requests.RequestException(f"Failed to download {url}. No retries left.")

            form = MultipartEncoder({
                "file_path": path,
                "file_data": (os.path.basename(path), open(cache_path, "rb"))
            })
            headers = {"Content-Type": form.content_type}

            # send request to server to upload file
            try:
                logger.info(f"Uploading {os.path.basename(path)} to VM at {path}")
                response = requests.post(self.http_server + "/setup" + "/upload", headers=headers, data=form, timeout=600)  # 10 minute timeout for upload
                if response.status_code == 200:
                    logger.info(f"File uploaded successfully: {path}")
                else:
                    logger.error(f"Failed to upload file {path}. Status code: {response.status_code}, Response: {response.text}")
                    raise requests.RequestException(f"Upload failed with status {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.error(f"An error occurred while trying to upload {path}: {e}")
                raise

    def _upload_file_setup(self, files: List[Dict[str, str]]):
        """
        Args:
            files (List[Dict[str, str]]): files to download. lisf of dict like
              {
                "local_path": str, the local path to the file to upload
                "path": str, the path on the VM to store the downloaded file
              }
        """
        # [延迟导入] 只在需要上传文件时才导入 requests_toolbelt
        try:
            from requests_toolbelt.multipart.encoder import MultipartEncoder
        except ImportError as e:
            logger.error(f"Failed to import requests_toolbelt: {e}")
            raise ImportError("requests_toolbelt is required for file upload operations. Install it with: pip install requests-toolbelt") from e

        for f in files:
            local_path: str = f["local_path"]
            path: str = f["path"]

            if not os.path.exists(local_path):
                raise Exception(f"Setup Upload - Invalid local path ({local_path}).")

            file_size = None
            try:
                file_size = os.path.getsize(local_path)
            except Exception:
                pass

            max_retries = 3
            last_error: Optional[Exception] = None

            for attempt in range(max_retries):
                try:
                    logger.info(
                        f"Uploading {os.path.basename(local_path)}{f' ({file_size} bytes)' if file_size is not None else ''} "
                        f"to VM at {path} (attempt {attempt + 1}/{max_retries})"
                    )

                    # Open the file inside each attempt to ensure fresh stream position
                    with open(local_path, "rb") as fp:
                        form = MultipartEncoder({
                            "file_path": path,
                            "file_data": (os.path.basename(path), fp)
                        })
                        headers = {"Content-Type": form.content_type}

                        # Explicit connect/read timeout to avoid hanging forever
                        response = requests.post(
                            self.http_server + "/setup" + "/upload",
                            headers=headers,
                            data=form,
                            timeout=(10, 600)
                        )

                        if response.status_code == 200:
                            logger.info(f"File uploaded successfully: {path}")
                            last_error = None
                            break
                        else:
                            msg = f"Failed to upload file {path}. Status code: {response.status_code}, Response: {response.text}"
                            logger.error(msg)
                            last_error = requests.RequestException(msg)

                except requests.exceptions.RequestException as e:
                    last_error = e
                    logger.error(f"Upload attempt {attempt + 1} failed for {path}: {e}")

                # Exponential backoff between retries
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

            if last_error is not None:
                raise last_error

    def _change_wallpaper_setup(self, path: str):
        if not path:
            raise Exception(f"Setup Wallpaper - Invalid path ({path}).")

        payload = json.dumps({"path": path})
        headers = {
            'Content-Type': 'application/json'
        }

        # send request to server to change wallpaper
        try:
            response = requests.post(self.http_server + "/setup" + "/change_wallpaper", headers=headers, data=payload)
            if response.status_code == 200:
                logger.info("Command executed successfully: %s", response.text)
            else:
                logger.error("Failed to change wallpaper. Status code: %s", response.text)
        except requests.exceptions.RequestException as e:
            logger.error("An error occurred while trying to send the request: %s", e)

    def _tidy_desktop_setup(self, **config):
        raise NotImplementedError()

    def _open_setup(self, path: str):
        if not path:
            raise Exception(f"Setup Open - Invalid path ({path}).")

        payload = json.dumps({"path": path})
        headers = {
            'Content-Type': 'application/json'
        }

        # send request to server to open file
        try:
            # The server-side call is now blocking and can take time.
            # We set a timeout that is slightly longer than the server's timeout (1800s).
            response = requests.post(self.http_server + "/setup" + "/open_file", headers=headers, data=payload, timeout=1810)
            response.raise_for_status()  # This will raise an exception for 4xx and 5xx status codes
            logger.info("Command executed successfully: %s", response.text)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to open file '{path}'. An error occurred while trying to send the request or the server responded with an error: {e}")
            raise Exception(f"Failed to open file '{path}'. An error occurred while trying to send the request or the server responded with an error: {e}") from e

    def _launch_setup(self, command: Union[str, List[str]], shell: bool = False):
        if not command:
            raise Exception("Empty command to launch.")

        if not shell and isinstance(command, str) and len(command.split()) > 1:
            logger.warning("Command should be a list of strings. Now it is a string. Will split it by space.")
            command = command.split()
            
        if command[0] == "google-chrome" and self.use_proxy:
            command.append("--proxy-server=http://127.0.0.1:18888")  # Use the proxy server set up by _proxy_setup

        payload = json.dumps({"command": command, "shell": shell})
        headers = {"Content-Type": "application/json"}

        try:
            logger.info("REQUEST ADDRESS: %s", self.http_server + "/setup" + "/launch")
            response = requests.post(self.http_server + "/setup" + "/launch", headers=headers, data=payload)
            if response.status_code == 200:
                logger.info("Command executed successfully: %s", response.text)
            else:
                logger.error("Failed to launch application. Status code: %s", response.text)
        except requests.exceptions.RequestException as e:
            logger.error("An error occurred while trying to send the request: %s", e)

    def _execute_setup(
            self,
            command: List[str],
            stdout: str = "",
            stderr: str = "",
            shell: bool = False,
            until: Optional[Dict[str, Any]] = None
    ):
        if not command:
            raise Exception("Empty command to launch.")

        until_conditions: Dict[str, Any] = until or {}
        terminates: bool = False
        nb_failings = 0

        def replace_screen_env_in_command(command):
            password = self.client_password
            width = self.screen_width
            height = self.screen_height
            width_half = str(width // 2)
            height_half = str(height // 2)
            new_command_list = []
            new_command = ""
            if isinstance(command, str):
                new_command = command.replace("{CLIENT_PASSWORD}", password)
                new_command = new_command.replace("{SCREEN_WIDTH_HALF}", width_half)
                new_command = new_command.replace("{SCREEN_HEIGHT_HALF}", height_half)
                new_command = new_command.replace("{SCREEN_WIDTH}", str(width))
                new_command = new_command.replace("{SCREEN_HEIGHT}", str(height))
                return new_command
            else:
                for item in command:
                    item = item.replace("{CLIENT_PASSWORD}", password)
                    item = item.replace("{SCREEN_WIDTH_HALF}", width_half)
                    item = item.replace("{SCREEN_HEIGHT_HALF}", height_half)
                    item = item.replace("{SCREEN_WIDTH}", str(width))
                    item = item.replace("{SCREEN_HEIGHT}", str(height))
                    new_command_list.append(item)
                return new_command_list
        command = replace_screen_env_in_command(command)
        payload = json.dumps({"command": command, "shell": shell})
        headers = {"Content-Type": "application/json"}

        while not terminates:
            try:
                response = requests.post(self.http_server + "/setup" + "/execute", headers=headers, data=payload)
                if response.status_code == 200:
                    results: Dict[str, str] = response.json()
                    if stdout:
                        with open(os.path.join(self.cache_dir, stdout), "w") as f:
                            f.write(results["output"])
                    if stderr:
                        with open(os.path.join(self.cache_dir, stderr), "w") as f:
                            f.write(results["error"])
                    logger.info("Command executed successfully: %s -> %s"
                                , " ".join(command) if isinstance(command, list) else command
                                , response.text
                                )
                else:
                    logger.error("Failed to launch application. Status code: %s", response.text)
                    results = None
                    nb_failings += 1
            except requests.exceptions.RequestException as e:
                logger.error("An error occurred while trying to send the request: %s", e)
                traceback.print_exc()

                results = None
                nb_failings += 1

            if len(until_conditions) == 0:
                terminates = True
            elif results is not None:
                terminates = "returncode" in until_conditions and results["returncode"] == until_conditions["returncode"] \
                             or "stdout" in until_conditions and until_conditions["stdout"] in results["output"] \
                             or "stderr" in until_conditions and until_conditions["stderr"] in results["error"]
            terminates = terminates or nb_failings >= 5
            if not terminates:
                time.sleep(0.3)

    def _execute_with_verification_setup(
            self,
            command: List[str],
            verification: Dict[str, Any] = None,
            max_wait_time: int = 10,
            check_interval: float = 1.0,
            shell: bool = False
    ):
        """Execute command with verification of results
        
        Args:
            command: Command to execute
            verification: Dict with verification criteria:
                - window_exists: Check if window with this name exists
                - command_success: Execute this command and check if it succeeds
            max_wait_time: Maximum time to wait for verification
            check_interval: Time between verification checks
            shell: Whether to use shell
        """
        if not command:
            raise Exception("Empty command to launch.")

        verification = verification or {}
        
        payload = json.dumps({
            "command": command, 
            "shell": shell,
            "verification": verification,
            "max_wait_time": max_wait_time,
            "check_interval": check_interval
        })
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(self.http_server + "/setup" + "/execute_with_verification", 
                                   headers=headers, data=payload, timeout=max_wait_time + 10)
            if response.status_code == 200:
                result = response.json()
                logger.info("Command executed and verified successfully: %s -> %s"
                            , " ".join(command) if isinstance(command, list) else command
                            , response.text
                            )
                return result
            else:
                logger.error("Failed to execute with verification. Status code: %s", response.text)
                raise Exception(f"Command verification failed: {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error("An error occurred while trying to send the request: %s", e)
            traceback.print_exc()
            raise Exception(f"Request failed: {e}")

    def _command_setup(self, command: List[str], **kwargs):
        self._execute_setup(command, **kwargs)

    def _sleep_setup(self, seconds: float):
        time.sleep(seconds)

    def _act_setup(self, action_seq: List[Union[Dict[str, Any], str]]):
        # TODO
        raise NotImplementedError()

    def _replay_setup(self, trajectory: str):
        """
        Args:
            trajectory (str): path to the replay trajectory file
        """

        # TODO
        raise NotImplementedError()

    def _activate_window_setup(self, window_name: str, strict: bool = False, by_class: bool = False):
        if not window_name:
            raise Exception(f"Setup Open - Invalid path ({window_name}).")

        payload = json.dumps({"window_name": window_name, "strict": strict, "by_class": by_class})
        headers = {
            'Content-Type': 'application/json'
        }

        # send request to server to open file
        try:
            response = requests.post(self.http_server + "/setup" + "/activate_window", headers=headers, data=payload)
            if response.status_code == 200:
                logger.info("Command executed successfully: %s", response.text)
            else:
                logger.error(f"Failed to activate window {window_name}. Status code: %s", response.text)
        except requests.exceptions.RequestException as e:
            logger.error("An error occurred while trying to send the request: %s", e)

    def _close_window_setup(self, window_name: str, strict: bool = False, by_class: bool = False):
        if not window_name:
            raise Exception(f"Setup Open - Invalid path ({window_name}).")

        payload = json.dumps({"window_name": window_name, "strict": strict, "by_class": by_class})
        headers = {
            'Content-Type': 'application/json'
        }

        # send request to server to open file
        try:
            response = requests.post(self.http_server + "/setup" + "/close_window", headers=headers, data=payload)
            if response.status_code == 200:
                logger.info("Command executed successfully: %s", response.text)
            else:
                logger.error(f"Failed to close window {window_name}. Status code: %s", response.text)
        except requests.exceptions.RequestException as e:
            logger.error("An error occurred while trying to send the request: %s", e)

    def _proxy_setup(self, client_password: str = ""):
        """Setup system-wide proxy configuration using proxy pool
        
        Args:
            client_password (str): Password for sudo operations, defaults to "password"
        """
        if not _PROXY_POOL_AVAILABLE or get_global_proxy_pool is None:
            logger.warning("Proxy pool provider is unavailable; skipping proxy setup.")
            return False
        logger.info("Proxy setup client_password length: %s", len(client_password or ""))

        retry = 0
        while retry < MAX_RETRIES:
            try:
                _ = requests.get(self.http_server + "/terminal")
                break
            except:
                time.sleep(5)
                retry += 1
                logger.info(f"retry: {retry}/{MAX_RETRIES}")
            
            if retry == MAX_RETRIES:
                return False
            
        # Get proxy from global proxy pool
        proxy_pool = get_global_proxy_pool()
        current_proxy = proxy_pool.get_next_proxy()
        
        if not current_proxy:
            logger.error("No proxy available from proxy pool")
            raise Exception("No proxy available from proxy pool")
        
        # Format proxy URL
        proxy_url = proxy_pool._format_proxy_url(current_proxy)
        logger.info(f"Setting up proxy: {current_proxy.host}:{current_proxy.port}")
        
        # Configure system proxy environment variables  
        proxy_commands = [
            f"echo '{client_password}' | sudo -S bash -c 'for i in $(seq 1 60); do "
            "fuser /var/lib/apt/lists/lock >/dev/null 2>&1 || "
            "fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 || exit 0; "
            "sleep 1; done; exit 1'",
            f"echo '{client_password}' | sudo -S bash -c \"apt-get update\"", ## TODO: remove this line if ami is already updated
            f"echo '{client_password}' | sudo -S bash -c \"apt-get install -y tinyproxy\"", ## TODO: remove this line if tinyproxy is already installed
            f"echo '{client_password}' | sudo -S bash -c \"echo 'Port 18888' > /tmp/tinyproxy.conf\"",
            f"echo '{client_password}' | sudo -S bash -c \"echo 'Allow 127.0.0.1' >> /tmp/tinyproxy.conf\"",
            f"echo '{client_password}' | sudo -S bash -c \"echo 'Upstream http {current_proxy.username}:{current_proxy.password}@{current_proxy.host}:{current_proxy.port}' >> /tmp/tinyproxy.conf\"",
            
            # CML commands to set environment variables for proxy
            f"echo 'export http_proxy={proxy_url}' >> ~/.bashrc",
            f"echo 'export https_proxy={proxy_url}' >> ~/.bashrc",
            f"echo 'export HTTP_PROXY={proxy_url}' >> ~/.bashrc",
            f"echo 'export HTTPS_PROXY={proxy_url}' >> ~/.bashrc",
            # Write to /etc/environment for global effect (non-interactive shells)
            f"echo '{client_password}' | sudo -S bash -c \"echo 'http_proxy=\\\"{proxy_url}\\\"' >> /etc/environment\"",
            f"echo '{client_password}' | sudo -S bash -c \"echo 'https_proxy=\\\"{proxy_url}\\\"' >> /etc/environment\"",
            f"echo '{client_password}' | sudo -S bash -c \"echo 'no_proxy=\\\"localhost,127.0.0.1,::1\\\"' >> /etc/environment\"",
            f"echo '{client_password}' | sudo -S bash -c \"echo 'HTTP_PROXY=\\\"{proxy_url}\\\"' >> /etc/environment\"",
            f"echo '{client_password}' | sudo -S bash -c \"echo 'HTTPS_PROXY=\\\"{proxy_url}\\\"' >> /etc/environment\"",
            f"echo '{client_password}' | sudo -S bash -c \"echo 'NO_PROXY=\\\"localhost,127.0.0.1,::1\\\"' >> /etc/environment\"",
        ]

        # Execute all proxy configuration commands
        for cmd in proxy_commands:
            try:
                self._execute_setup([cmd], shell=True)
            except Exception as e:
                logger.error(f"Failed to execute proxy setup command: {e}")
                proxy_pool.mark_proxy_failed(current_proxy)
                raise

        self._launch_setup(["tinyproxy -c /tmp/tinyproxy.conf -d"], shell=True)

        gnome_proxy_commands = [
            "bash -lc \"gsettings set org.gnome.system.proxy mode 'manual'\"",
            "bash -lc \"gsettings set org.gnome.system.proxy.http host '127.0.0.1'\"",
            "bash -lc \"gsettings set org.gnome.system.proxy.http port 18888\"",
            "bash -lc \"gsettings set org.gnome.system.proxy.https host '127.0.0.1'\"",
            "bash -lc \"gsettings set org.gnome.system.proxy.https port 18888\"",
            "bash -lc \"gsettings set org.gnome.system.proxy ignore-hosts \\\"['localhost', '127.0.0.1', '::1']\\\"\"",
        ]
        for cmd in gnome_proxy_commands:
            try:
                self._execute_setup([cmd], shell=True)
            except Exception as e:
                logger.warning("GNOME proxy setting failed: %s", e)

        # Reload environment variables
        reload_cmd = "source /etc/environment"
        try:
            logger.info(f"Proxy setup completed successfully for {current_proxy.host}:{current_proxy.port}")
            proxy_pool.mark_proxy_success(current_proxy)
        except Exception as e:
            logger.error(f"Failed to reload environment variables: {e}")
            proxy_pool.mark_proxy_failed(current_proxy)
            raise

    # Chrome setup
    def _chrome_open_tabs_setup(self, urls_to_open: List[str]):
        host = self.vm_ip
        port = self.chromium_port  # fixme: this port is hard-coded, need to be changed from config file

        remote_debugging_url = f"http://{host}:{port}"
        logger.info("Connect to Chrome @: %s", remote_debugging_url)
        for attempt in range(15):
            if attempt > 0:
                time.sleep(5)

            browser = None
            with sync_playwright() as p:
                try:
                    browser = p.chromium.connect_over_cdp(remote_debugging_url)
                    # break
                except Exception as e:
                    if attempt < 14:
                        logger.error(f"Attempt {attempt + 1}: Failed to connect, retrying. Error: {e}")
                        # time.sleep(10)
                        continue
                    else:
                        logger.error(f"Failed to connect after multiple attempts: {e}")
                        raise e

                if not browser:
                    return

                logger.info("Opening %s...", urls_to_open)
                context = browser.contexts[0] if browser.contexts else browser.new_context()
                for i, url in enumerate(urls_to_open):
                    page = context.new_page()  # Create a new page (tab) within the existing context
                    try:
                        page.goto(url, timeout=60000)
                    except:
                        logger.warning("Opening %s exceeds time limit", url)  # only for human test
                    logger.info(f"Opened tab {i + 1}: {url}")

                    if i == 0:
                        # clear the default tab
                        if context.pages:
                            default_page = context.pages[0]
                            default_page.close()

                # Do not close the context or browser; they will remain open after script ends
                return browser, context

    def _chrome_close_tabs_setup(self, urls_to_close: List[str]):
        time.sleep(5)  # Wait for Chrome to finish launching

        host = self.vm_ip
        port = self.chromium_port  # fixme: this port is hard-coded, need to be changed from config file

        remote_debugging_url = f"http://{host}:{port}"
        with sync_playwright() as p:
            browser = None
            for attempt in range(15):
                try:
                    browser = p.chromium.connect_over_cdp(remote_debugging_url)
                    break
                except Exception as e:
                    if attempt < 14:
                        logger.error(f"Attempt {attempt + 1}: Failed to connect, retrying. Error: {e}")
                        time.sleep(5)
                    else:
                        logger.error(f"Failed to connect after multiple attempts: {e}")
                        raise e

            if not browser:
                return

            context = browser.contexts[0] if browser.contexts else browser.new_context()
            for i, url in enumerate(urls_to_close):
                for page in context.pages:

                    # if two urls are the same, close the tab
                    if compare_urls(page.url, url):
                        context.pages.pop(context.pages.index(page))
                        page.close()
                        logger.info(f"Closed tab {i + 1}: {url}")
                        break

            # Do not close the context or browser; they will remain open after script ends
            return browser, context

    # google drive setup
    def _googledrive_setup(self, **config):
        """ Clean google drive space (eliminate the impact of previous experiments to reset the environment)
        @args:
            config(Dict[str, Any]): contain keys
                settings_file(str): path to google drive settings file, which will be loaded by pydrive.auth.GoogleAuth()
                operation(List[str]): each operation is chosen from ['delete', 'upload']
                args(List[Dict[str, Any]]): parameters for each operation
            different args dict for different operations:
                for delete:
                    query(str): query pattern string to search files or folder in google drive to delete, please refer to
                        https://developers.google.com/drive/api/guides/search-files?hl=en about how to write query string.
                    trash(bool): whether to delete files permanently or move to trash. By default, trash=false, completely delete it.
                for mkdirs:
                    path(List[str]): the path in the google drive to create folder
                for upload:
                    path(str): remote url to download file
                    dest(List[str]): the path in the google drive to store the downloaded file
        """
        # [延迟导入] 只在需要时才导入 pydrive
        try:
            from pydrive.auth import GoogleAuth
            from pydrive.drive import GoogleDrive, GoogleDriveFile, GoogleDriveFileList
        except ImportError as e:
            logger.error(f"Failed to import pydrive: {e}. Please install it with: pip install pydrive")
            raise ImportError("pydrive is required for Google Drive operations. Install it with: pip install pydrive") from e

        settings_file = config.get('settings_file', str(_UTILS_DIR / 'osworld-settings' / 'googledrive' / 'settings.yml'))
        gauth = GoogleAuth(settings_file=settings_file)
        drive = GoogleDrive(gauth)

        def mkdir_in_googledrive(paths: Union[str, List[str]]):
            paths = [paths] if isinstance(paths, str) else paths
            parent_id = 'root'
            for p in paths:
                q = f'"{parent_id}" in parents and title = "{p}" and mimeType = "application/vnd.google-apps.folder" and trashed = false'
                folder = drive.ListFile({'q': q}).GetList()
                if len(folder) == 0:  # not exists, create it
                    parents = {} if parent_id == 'root' else {'parents': [{'id': parent_id}]}
                    file = drive.CreateFile({'title': p, 'mimeType': 'application/vnd.google-apps.folder', **parents})
                    file.Upload()
                    parent_id = file['id']
                else:
                    parent_id = folder[0]['id']
            return parent_id

        for oid, operation in enumerate(config['operation']):
            if operation == 'delete':  # delete a specific file
                # query pattern string, by default, remove all files/folders not in the trash to the trash
                params = config['args'][oid]
                q = params.get('query', '')
                trash = params.get('trash', False)
                q_file = f"( {q} ) and mimeType != 'application/vnd.google-apps.folder'" if q.strip() else "mimeType != 'application/vnd.google-apps.folder'"
                filelist: GoogleDriveFileList = drive.ListFile({'q': q_file}).GetList()
                q_folder = f"( {q} ) and mimeType = 'application/vnd.google-apps.folder'" if q.strip() else "mimeType = 'application/vnd.google-apps.folder'"
                folderlist: GoogleDriveFileList = drive.ListFile({'q': q_folder}).GetList()
                for file in filelist:  # first delete file, then folder
                    file: GoogleDriveFile
                    if trash:
                        file.Trash()
                    else:
                        file.Delete()
                for folder in folderlist:
                    folder: GoogleDriveFile
                    # note that, if a folder is trashed/deleted, all files and folders in it will be trashed/deleted
                    if trash:
                        folder.Trash()
                    else:
                        folder.Delete()
            elif operation == 'mkdirs':
                params = config['args'][oid]
                mkdir_in_googledrive(params['path'])
            elif operation == 'upload':
                params = config['args'][oid]
                url = params['url']
                with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmpf:
                    response = requests.get(url, stream=True)
                    response.raise_for_status()
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            tmpf.write(chunk)
                    tmpf.close()
                    paths = [params['path']] if params['path'] != list else params['path']
                    parent_id = mkdir_in_googledrive(paths[:-1])
                    parents = {} if parent_id == 'root' else {'parents': [{'id': parent_id}]}
                    file = drive.CreateFile({'title': paths[-1], **parents})
                    file.SetContentFile(tmpf.name)
                    file.Upload()
                return
            else:
                raise ValueError('[ERROR]: not implemented clean type!')

    def _login_setup(self, **config):
        """ Login to a website with account and password information.
        @args:
            config(Dict[str, Any]): contain keys
                settings_file(str): path to the settings file
                platform(str): platform to login, implemented platforms include:
                    googledrive: https://drive.google.com/drive/my-drive

        """
        host = self.vm_ip
        port = self.chromium_port

        remote_debugging_url = f"http://{host}:{port}"
        with sync_playwright() as p:
            browser = None
            for attempt in range(15):
                try:
                    browser = p.chromium.connect_over_cdp(remote_debugging_url)
                    break
                except Exception as e:
                    if attempt < 14:
                        logger.error(f"Attempt {attempt + 1}: Failed to connect, retrying. Error: {e}")
                        time.sleep(5)
                    else:
                        logger.error(f"Failed to connect after multiple attempts: {e}")
                        raise e
            if not browser:
                return

            context = browser.contexts[0]
            platform = config['platform']

            if platform == 'googledrive':
                url = 'https://drive.google.com/drive/my-drive'
                page = context.new_page()  # Create a new page (tab) within the existing context
                try:
                    page.goto(url, timeout=60000)
                except:
                    logger.warning("Opening %s exceeds time limit", url)  # only for human test
                logger.info(f"Opened new page: {url}")
                settings = json.load(open(config['settings_file']))
                email, password = settings['email'], settings['password']

                try:
                    page.wait_for_selector('input[type="email"]', state="visible", timeout=3000)
                    page.fill('input[type="email"]', email)
                    page.click('#identifierNext > div > button')
                    page.wait_for_selector('input[type="password"]', state="visible", timeout=5000)
                    page.fill('input[type="password"]', password)
                    page.click('#passwordNext > div > button')
                    page.wait_for_load_state('load', timeout=5000)
                except TimeoutError:
                    logger.info('[ERROR]: timeout when waiting for google drive login page to load!')
                    return

            else:
                raise NotImplementedError

            return browser, context

    def _update_browse_history_setup(self, **config):
        # [延迟导入] 只在需要上传文件时才导入 requests_toolbelt
        try:
            from requests_toolbelt.multipart.encoder import MultipartEncoder
        except ImportError as e:
            logger.error(f"Failed to import requests_toolbelt: {e}")
            raise ImportError("requests_toolbelt is required for file upload operations. Install it with: pip install requests-toolbelt") from e

        cache_path = os.path.join(self.cache_dir, "history_new.sqlite")
        db_url = "https://huggingface.co/datasets/xlangai/ubuntu_osworld_file_cache/resolve/main/chrome/44ee5668-ecd5-4366-a6ce-c1c9b8d4e938/history_empty.sqlite?download=true"
        if not os.path.exists(cache_path):
            max_retries = 3
            downloaded = False
            e = None
            for i in range(max_retries):
                try:
                    response = requests.get(db_url, stream=True)
                    response.raise_for_status()

                    with open(cache_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    logger.info("File downloaded successfully")
                    downloaded = True
                    break

                except requests.RequestException as e:
                    logger.error(
                        f"Failed to download {db_url} caused by {e}. Retrying... ({max_retries - i - 1} attempts left)")
            if not downloaded:
                raise requests.RequestException(f"Failed to download {db_url}. No retries left. Error: {e}")
        else:
            logger.info("File already exists in cache directory")
        # copy a new history file in the tmp folder
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = os.path.join(tmp_dir, "history_empty.sqlite")
            shutil.copy(cache_path, db_path)

            history = config['history']

            for history_item in history:
                url = history_item['url']
                title = history_item['title']
                visit_time = datetime.now() - timedelta(seconds=history_item['visit_time_from_now_in_seconds'])

                # Chrome use ms from 1601-01-01 as timestamp
                epoch_start = datetime(1601, 1, 1)
                chrome_timestamp = int((visit_time - epoch_start).total_seconds() * 1000000)

                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO urls (url, title, visit_count, typed_count, last_visit_time, hidden)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (url, title, 1, 0, chrome_timestamp, 0))

                url_id = cursor.lastrowid

                cursor.execute('''
                    INSERT INTO visits (url, visit_time, from_visit, transition, segment_id, visit_duration)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (url_id, chrome_timestamp, 0, 805306368, 0, 0))

                conn.commit()
                conn.close()

            logger.info('Fake browsing history added successfully.')

            controller = PythonController(self.vm_ip, self.server_port)

            # get the path of the history file according to the platform
            os_type = controller.get_vm_platform()

            def _get_command_output(command: str) -> str:
                result = controller.execute_python_command(command)
                if not result or "output" not in result:
                    raise RuntimeError("Failed to resolve Chrome history path from VM.")
                return str(result["output"]).strip()

            if os_type == 'Windows':
                chrome_history_path = _get_command_output(
                    """import os; print(os.path.join(os.getenv('USERPROFILE'), "AppData", "Local", "Google", "Chrome", "User Data", "Default", "History"))"""
                )
            elif os_type == 'Darwin':
                chrome_history_path = _get_command_output(
                    """import os; print(os.path.join(os.getenv('HOME'), "Library", "Application Support", "Google", "Chrome", "Default", "History"))"""
                )
            elif os_type == 'Linux':
                if "arm" in platform.machine():
                    chrome_history_path = _get_command_output(
                        "import os; print(os.path.join(os.getenv('HOME'), 'snap', 'chromium', 'common', 'chromium', 'Default', 'History'))"
                    )
                else:
                    chrome_history_path = _get_command_output(
                        "import os; print(os.path.join(os.getenv('HOME'), '.config', 'google-chrome', 'Default', 'History'))"
                    )
            else:
                raise Exception('Unsupported operating system')

            form = MultipartEncoder({
                "file_path": chrome_history_path,
                "file_data": (os.path.basename(chrome_history_path), open(db_path, "rb"))
            })
            headers = {"Content-Type": form.content_type}

            # send request to server to upload file
            try:
                response = requests.post(self.http_server + "/setup" + "/upload", headers=headers, data=form)
                if response.status_code == 200:
                    logger.info("Command executed successfully: %s", response.text)
                else:
                    logger.error("Failed to upload file. Status code: %s", response.text)
            except requests.exceptions.RequestException as e:
                logger.error("An error occurred while trying to send the request: %s", e)

            self._execute_setup(["sudo chown -R user:user /home/user/.config/google-chrome/Default/History"], shell=True)

# [新增] 补充缺失的 helper 函数
def execute_setup_steps(controller: PythonController, config: List[Dict[str, Any]]) -> bool:
    """
    根据给定的 PythonController 实例信息，初始化 SetupController 并执行配置步骤。
    
    Args:
        controller: 已初始化的 PythonController 实例 (包含 IP 和端口信息)
        config: 任务配置列表 (setup steps)
    
    Returns:
        bool: 执行是否成功
    """
    if not config:
        return True

    # 尝试从 controller 的 http_server 属性中解析端口 (格式通常为 http://ip:port)
    server_port = 5000
    try:
        if hasattr(controller, "http_server"):
            server_port = int(controller.http_server.split(":")[-1])
    except Exception as e:
        logger.warning(f"Could not parse port from controller, using default 5000: {e}")

    # 初始化 SetupController
    # 注意：这里使用默认的辅助端口 (chromium 9222, vlc 8080 等)，如果有特殊配置需从环境变量读取
    setup_controller = SetupController(
        vm_ip=controller.vm_ip, 
        server_port=server_port
    )
    
    # 执行 setup
    return setup_controller.setup(config)
