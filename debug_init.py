#!/usr/bin/env python3
"""
诊断脚本：检查 OSWorldEnvironment 初始化问题
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from envs.osworld_environment import OSWorldEnvironment

def test_initialization():
    """测试环境初始化"""
    print("=" * 60)
    print("测试 OSWorldEnvironment 初始化")
    print("=" * 60)
    
    # 模拟最小配置
    config = {
        "path_to_vm": "/tmp/test.vmx",  # 假路径，用于测试
        "provider_name": "vmware",
    }
    
    try:
        print("\n1. 开始创建 OSWorldEnvironment...")
        env = OSWorldEnvironment(**config)
        print("\n2. 环境对象创建成功")
        
        # 检查 DesktopEnv 是否初始化
        if hasattr(env, '_desktop_env'):
            if env._desktop_env is None:
                print("\n❌ 问题确认：_desktop_env 是 None")
                print("   这意味着 DesktopEnv 没有被初始化")
            else:
                print("\n✓ DesktopEnv 已初始化")
        else:
            print("\n❌ 问题确认：_desktop_env 属性不存在")
            
        # 检查配置
        print(f"\n3. 配置检查：")
        print(f"   osworld_available: {env.config.get('osworld_available', 'NOT SET')}")
        print(f"   osworld config exists: {'osworld' in env.config}")
        
        if 'osworld' in env.config:
            osworld_config = env.config['osworld']
            print(f"   path_to_vm: {osworld_config.get('path_to_vm')}")
            print(f"   provider_name: {osworld_config.get('provider_name')}")
        
    except Exception as e:
        print(f"\n❌ 初始化失败：{e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_initialization()

