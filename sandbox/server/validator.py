# sandbox/server/validator.py
"""
配置验证器 - Strict Mode 检查

用于 CI/CD 阶段验证配置文件的正确性：
- 检查所有 backend_class 路径是否可解析
- 检查 @tool 装饰器标记的方法是否存在
- 检查 @register_api_tool 注册的工具是否正确
- 检查配置文件的必填字段

使用方式：

1. 命令行：
   python -m sandbox validate --config dev
   python -m sandbox validate --config /path/to/config.json --strict

2. Python API：
   from sandbox.server.validator import validate_config, validate_all_configs
   
   result = validate_config("configs/profiles/dev.json", strict=True)
   if not result.is_valid:
       print(result.errors)

3. CI/CD 集成：
   python -m sandbox validate --all --strict --exit-on-error
"""

import os
import sys
import json
import logging
import importlib
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Type
from dataclasses import dataclass, field

logger = logging.getLogger("ConfigValidator")


# ============================================================================
# Validation Result
# ============================================================================

@dataclass
class ValidationError:
    """验证错误"""
    level: str           # "error" | "warning"
    category: str        # "backend_class" | "tool" | "config" | "api_tool"
    message: str
    location: str = ""   # 错误位置（如 "resources.vm.backend_class"）
    suggestion: str = "" # 修复建议


@dataclass
class ValidationResult:
    """验证结果"""
    config_path: str
    is_valid: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    
    # 统计信息
    backends_checked: int = 0
    backends_valid: int = 0
    tools_checked: int = 0
    tools_valid: int = 0
    api_tools_checked: int = 0
    api_tools_valid: int = 0
    
    def add_error(self, error: ValidationError):
        if error.level == "error":
            self.errors.append(error)
            self.is_valid = False
        else:
            self.warnings.append(error)
    
    def summary(self) -> str:
        """生成摘要"""
        lines = [
            f"Config: {self.config_path}",
            f"Status: {'✅ VALID' if self.is_valid else '❌ INVALID'}",
            f"",
            f"Backends: {self.backends_valid}/{self.backends_checked} valid",
            f"Tools: {self.tools_valid}/{self.tools_checked} valid",
            f"API Tools: {self.api_tools_valid}/{self.api_tools_checked} valid",
        ]
        
        if self.errors:
            lines.append(f"\nErrors ({len(self.errors)}):")
            for err in self.errors:
                lines.append(f"  ❌ [{err.category}] {err.message}")
                if err.location:
                    lines.append(f"     Location: {err.location}")
                if err.suggestion:
                    lines.append(f"     Suggestion: {err.suggestion}")
        
        if self.warnings:
            lines.append(f"\nWarnings ({len(self.warnings)}):")
            for warn in self.warnings:
                lines.append(f"  ⚠️ [{warn.category}] {warn.message}")
        
        return "\n".join(lines)


# ============================================================================
# Validators
# ============================================================================

class ConfigValidator:
    """配置验证器"""
    
    def __init__(self, strict: bool = False):
        """
        初始化验证器
        
        Args:
            strict: 严格模式，将警告视为错误
        """
        self.strict = strict
    
    def validate(self, config_path: str) -> ValidationResult:
        """
        验证配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            验证结果
        """
        result = ValidationResult(config_path=config_path)
        
        # 1. 检查文件是否存在
        if not os.path.exists(config_path):
            result.add_error(ValidationError(
                level="error",
                category="config",
                message=f"Config file not found: {config_path}"
            ))
            return result
        
        # 2. 加载配置
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            result.add_error(ValidationError(
                level="error",
                category="config",
                message=f"Invalid JSON: {e}"
            ))
            return result
        
        # 3. 验证 resources 中的 backend_class
        self._validate_resources(config, result)
        
        # 4. 验证 apis 配置
        self._validate_apis(config, result)
        
        # 5. 验证必填字段
        self._validate_required_fields(config, result)
        
        return result
    
    def _validate_resources(self, config: Dict, result: ValidationResult):
        """验证 resources 配置"""
        resources = config.get("resources", {})
        
        for name, res_config in resources.items():
            # 跳过注释字段
            if name.startswith("_"):
                continue
            
            result.backends_checked += 1
            
            # 检查是否启用
            if not res_config.get("enabled", True):
                result.backends_valid += 1
                continue
            
            backend_class = res_config.get("backend_class")
            if not backend_class:
                result.add_error(ValidationError(
                    level="warning" if not self.strict else "error",
                    category="backend_class",
                    message=f"Resource '{name}' has no backend_class",
                    location=f"resources.{name}.backend_class",
                    suggestion="Add a backend_class path or set enabled=false"
                ))
                continue
            
            # 验证 backend_class 是否可解析
            is_valid, error_msg, backend_cls = self._validate_class_path(backend_class)
            
            if not is_valid:
                result.add_error(ValidationError(
                    level="error",
                    category="backend_class",
                    message=f"Cannot resolve backend_class for '{name}': {error_msg}",
                    location=f"resources.{name}.backend_class",
                    suggestion=f"Check if the module path '{backend_class}' is correct"
                ))
            else:
                result.backends_valid += 1
                
                # 验证后端类的工具
                if backend_cls:
                    self._validate_backend_tools(name, backend_cls, result)
    
    def _validate_class_path(self, class_path: str) -> Tuple[bool, str, Optional[Type]]:
        """
        验证类路径是否可解析
        
        Returns:
            (is_valid, error_message, class_object)
        """
        try:
            module_path, class_name = class_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            return True, "", cls
        except ValueError:
            return False, "Invalid class path format (expected 'module.ClassName')", None
        except ImportError as e:
            return False, f"Module import failed: {e}", None
        except AttributeError:
            return False, f"Class '{class_name}' not found in module '{module_path}'", None
        except Exception as e:
            return False, f"Unexpected error: {e}", None
    
    def _validate_backend_tools(self, backend_name: str, backend_cls: Type, result: ValidationResult):
        """验证后端类中的工具"""
        from .core.decorators import TOOL_MARKER, get_tool_metadata
        
        # 尝试实例化后端以扫描工具
        try:
            # 检查类中是否有 @tool 标记的方法
            tool_methods = []
            for attr_name in dir(backend_cls):
                if attr_name.startswith("_"):
                    continue
                try:
                    attr = getattr(backend_cls, attr_name)
                    if callable(attr) and hasattr(attr, TOOL_MARKER):
                        tool_methods.append(attr_name)
                        result.tools_checked += 1
                        result.tools_valid += 1
                except Exception:
                    pass
            
            if not tool_methods:
                # 检查是否有 register_tools 方法（另一种注册方式）
                if hasattr(backend_cls, 'register_tools'):
                    result.add_error(ValidationError(
                        level="warning",
                        category="tool",
                        message=f"Backend '{backend_name}' uses register_tools() method, cannot statically verify tools",
                        location=f"resources.{backend_name}",
                        suggestion="Consider using @tool decorator for better static analysis"
                    ))
                else:
                    result.add_error(ValidationError(
                        level="warning",
                        category="tool",
                        message=f"Backend '{backend_name}' has no @tool decorated methods",
                        location=f"resources.{backend_name}"
                    ))
                    
        except Exception as e:
            result.add_error(ValidationError(
                level="warning",
                category="tool",
                message=f"Failed to inspect backend '{backend_name}' tools: {e}",
                location=f"resources.{backend_name}"
            ))
    
    def _validate_apis(self, config: Dict, result: ValidationResult):
        """验证 apis 配置"""
        apis = config.get("apis", {})
        
        # 获取已注册的 API 工具
        try:
            from .backends.tools import get_all_api_tools, get_required_config_keys
            
            api_tools = get_all_api_tools()
            required_keys = get_required_config_keys()
            
            result.api_tools_checked = len(api_tools)
            
            # 检查是否所有需要的配置键都存在
            for config_key in required_keys:
                if config_key not in apis:
                    result.add_error(ValidationError(
                        level="warning" if not self.strict else "error",
                        category="api_tool",
                        message=f"Missing config key '{config_key}' in apis section",
                        location=f"apis.{config_key}",
                        suggestion=f"Add '{config_key}' configuration for related API tools"
                    ))
                else:
                    result.api_tools_valid += 1
                    
        except ImportError:
            result.add_error(ValidationError(
                level="warning",
                category="api_tool",
                message="Cannot import API tools module for validation"
            ))
    
    def _validate_required_fields(self, config: Dict, result: ValidationResult):
        """验证必填字段"""
        # server 配置
        server = config.get("server", {})
        if not server.get("title"):
            result.add_error(ValidationError(
                level="warning",
                category="config",
                message="Missing server.title",
                location="server.title",
                suggestion="Add a descriptive title for your server"
            ))


# ============================================================================
# Convenience Functions
# ============================================================================

def validate_config(config_path: str, strict: bool = False) -> ValidationResult:
    """
    验证单个配置文件
    
    Args:
        config_path: 配置文件路径
        strict: 严格模式
        
    Returns:
        验证结果
    """
    validator = ConfigValidator(strict=strict)
    return validator.validate(config_path)


def validate_all_configs(
    configs_dir: str = None,
    strict: bool = False
) -> Dict[str, ValidationResult]:
    """
    验证所有配置文件
    
    Args:
        configs_dir: 配置目录（默认 sandbox/configs/profiles）
        strict: 严格模式
        
    Returns:
        {config_path: ValidationResult}
    """
    if configs_dir is None:
        # 默认配置目录
        sandbox_dir = Path(__file__).parent.parent
        configs_dir = sandbox_dir / "configs" / "profiles"
    
    configs_dir = Path(configs_dir)
    if not configs_dir.exists():
        return {}
    
    results = {}
    validator = ConfigValidator(strict=strict)
    
    for config_file in configs_dir.glob("*.json"):
        result = validator.validate(str(config_file))
        results[str(config_file)] = result
    
    return results


def print_validation_report(results: Dict[str, ValidationResult]) -> bool:
    """
    打印验证报告
    
    Returns:
        是否全部通过
    """
    all_valid = True
    
    print("\n" + "=" * 70)
    print("🔍 Configuration Validation Report")
    print("=" * 70)
    
    for config_path, result in results.items():
        print(f"\n{result.summary()}")
        print("-" * 70)
        
        if not result.is_valid:
            all_valid = False
    
    print("\n" + "=" * 70)
    if all_valid:
        print("✅ All configurations are valid!")
    else:
        print("❌ Some configurations have errors. Please fix them before deployment.")
    print("=" * 70 + "\n")
    
    return all_valid


# ============================================================================
# CLI Support
# ============================================================================

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate Sandbox configuration files"
    )
    parser.add_argument(
        "--config", "-c",
        help="Config file or profile name (dev/prod/minimal)"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Validate all config files in profiles directory"
    )
    parser.add_argument(
        "--strict", "-s",
        action="store_true",
        help="Strict mode: treat warnings as errors"
    )
    parser.add_argument(
        "--exit-on-error",
        action="store_true",
        help="Exit with non-zero code if validation fails (for CI/CD)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only show errors, no detailed output"
    )
    
    args = parser.parse_args()
    
    # 配置文件路径映射
    sandbox_dir = Path(__file__).parent.parent
    config_profiles = {
        "dev": sandbox_dir / "configs/profiles/dev.json",
        "prod": sandbox_dir / "configs/profiles/production.json",
        "production": sandbox_dir / "configs/profiles/production.json",
        "minimal": sandbox_dir / "configs/profiles/minimal.json",
    }
    
    if args.all:
        # 验证所有配置
        results = validate_all_configs(strict=args.strict)
        all_valid = print_validation_report(results)
    elif args.config:
        # 验证单个配置
        config_path = args.config
        if config_path in config_profiles:
            config_path = str(config_profiles[config_path])
        
        result = validate_config(config_path, strict=args.strict)
        
        if not args.quiet:
            print(f"\n{result.summary()}\n")
        
        all_valid = result.is_valid
    else:
        parser.print_help()
        return
    
    if args.exit_on_error and not all_valid:
        sys.exit(1)


if __name__ == "__main__":
    main()

