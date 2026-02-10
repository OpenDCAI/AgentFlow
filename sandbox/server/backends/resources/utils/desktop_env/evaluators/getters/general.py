import logging
import shlex
from typing import Dict, Tuple, Union, List, Any
import requests

logger = logging.getLogger("desktopenv.getters.general")


def _wrap_command_with_proxy(
    command: Union[str, List[str]],
    shell: bool,
    use_proxy: bool,
) -> Tuple[Union[str, List[str]], bool]:
    if not use_proxy:
        return command, shell

    proxy_env = (
        "export http_proxy=http://127.0.0.1:18888; "
        "export https_proxy=http://127.0.0.1:18888; "
        "export HTTP_PROXY=http://127.0.0.1:18888; "
        "export HTTPS_PROXY=http://127.0.0.1:18888; "
        "export no_proxy=localhost,127.0.0.1,::1; "
        "export NO_PROXY=localhost,127.0.0.1,::1; "
    )

    if shell:
        wrapped = f"{proxy_env}{command}"
        return f"bash -lc {shlex.quote(wrapped)}", True

    if isinstance(command, list):
        cmd_str = " ".join(shlex.quote(part) for part in command)
    else:
        cmd_str = command
    wrapped = f"{proxy_env}{cmd_str}"
    return ["bash", "-lc", wrapped], False


def get_vm_command_line(env, config: Dict[str, Any]):
    vm_ip = env.vm_ip
    port = env.server_port
    command = config["command"]
    shell = bool(config.get("shell", False))
    command, shell = _wrap_command_with_proxy(command, shell, env.current_use_proxy)

    response = requests.post(f"http://{vm_ip}:{port}/execute", json={"command": command, "shell": shell})

    print(response.json())

    if response.status_code == 200:
        return response.json()["output"]
    else:
        logger.error("Failed to get vm command line. Status code: %d", response.status_code)
        return None

def get_vm_command_error(env, config: Dict[str, Any]):
    vm_ip = env.vm_ip
    port = env.server_port
    command = config["command"]
    shell = bool(config.get("shell", False))
    command, shell = _wrap_command_with_proxy(command, shell, env.current_use_proxy)

    response = requests.post(f"http://{vm_ip}:{port}/execute", json={"command": command, "shell": shell})

    print(response.json())

    if response.status_code == 200:
        return response.json()["error"]
    else:
        logger.error("Failed to get vm command line error. Status code: %d", response.status_code)
        return None


def get_vm_terminal_output(env, config: Dict[str, Any]):
    return env.controller.get_terminal_output()
