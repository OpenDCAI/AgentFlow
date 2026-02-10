from sandbox.server.backends.resources.utils.desktop_env.providers.base import VMManager, Provider


def create_vm_manager_and_provider(provider_name: str, region: str, use_proxy: bool = False):
    """
    Factory function to get the Virtual Machine Manager and Provider instances based on the provided provider name.
    
    Args:
        provider_name (str): The name of the provider (e.g., "docker", "aliyun")
        region (str): The region for the provider
        use_proxy (bool): Whether to use proxy-enabled providers (reserved for future use)
    """
    provider_name = provider_name.lower().strip()
    if provider_name == "docker":
        from sandbox.server.backends.resources.utils.desktop_env.providers.docker.manager import DockerVMManager
        from sandbox.server.backends.resources.utils.desktop_env.providers.docker.provider import DockerProvider
        return DockerVMManager(), DockerProvider(region)
    elif provider_name == "aliyun":
        from sandbox.server.backends.resources.utils.desktop_env.providers.aliyun.manager import AliyunVMManager
        from sandbox.server.backends.resources.utils.desktop_env.providers.aliyun.provider import AliyunProvider
        return AliyunVMManager(), AliyunProvider()
    else:
        raise NotImplementedError(f"{provider_name} not implemented!")
