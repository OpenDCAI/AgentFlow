"""
Example usage of the Environment classes for AgentFlow.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enviroment import (
    Environment, 
    MathEnvironment,
    PythonEnvironment,
    RAGEnvironment,
    WebEnvironment,
    create_math_environment, 
    create_web_environment
)


def example_basic_usage():
    """Basic usage example."""
    print("=== Basic Environment Usage ===")
    
    # Create a math environment
    env = create_math_environment()
    
    # Get environment info
    info = env.get_environment_info()
    print(f"Environment mode: {info['mode']}")
    print(f"Available tools: {info['tools']}")
    print(f"Tool descriptions:\n{env.get_tool_descriptions()}")
    
    # Execute a tool
    result = env.execute_tool("calculator", {"expressions": ["2+2", "sqrt(16)", "pow(2,3)"]})
    print(f"Calculator result: {result}")


def example_inheritance_usage():
    """Example of using inheritance architecture."""
    print("\n=== Inheritance Architecture Example ===")
    
    # Create different environment types
    math_env = MathEnvironment()
    print(f"Math environment mode: {math_env.mode}")
    print(f"Math environment tools: {math_env.list_tools()}")
    
    # Create web environment with custom config
    web_env = WebEnvironment(
        web_search_top_k=3,
        web_search_type="search"
    )
    print(f"Web environment mode: {web_env.mode}")
    print(f"Web environment tools: {web_env.list_tools()}")
    
    # Show that they are different types
    print(f"Math env is MathEnvironment: {isinstance(math_env, MathEnvironment)}")
    print(f"Math env is WebEnvironment: {isinstance(math_env, WebEnvironment)}")
    print(f"Both are Environment: {isinstance(math_env, Environment) and isinstance(web_env, Environment)}")


def example_custom_configuration():
    """Example with custom configuration."""
    print("\n=== Custom Configuration Example ===")
    
    # Create web environment with custom config
    env = WebEnvironment(
        model_name="gpt-4",
        web_search_top_k=5,
        web_search_type="news",
        custom_param="custom_value"
    )
    
    print(f"Environment mode: {env.mode}")
    print(f"Model name: {env.get_config('model_name')}")
    print(f"Custom param: {env.get_config('custom_param')}")
    print(f"Web search top_k: {env.get_config('web_search_top_k')}")
    print(f"Available tools: {env.list_tools()}")


def example_tool_management():
    """Example of tool management."""
    print("\n=== Tool Management Example ===")
    
    env = create_math_environment()
    
    # List tools
    print(f"Available tools: {env.list_tools()}")
    
    # Get specific tool
    calculator = env.get_tool("calculator")
    if calculator:
        print(f"Calculator tool found: {calculator.name}")
        print(f"Calculator description: {calculator.description}")
    
    # Try to get non-existent tool
    non_existent = env.get_tool("non_existent")
    print(f"Non-existent tool: {non_existent}")


def example_environment_persistence():
    """Example of saving and loading environment."""
    print("\n=== Environment Persistence Example ===")
    
    # Create and save environment
    env = create_web_environment(web_search_top_k=10)
    env.save_environment("example_env.json")
    
    # Create new environment and load
    new_env = MathEnvironment()  # Start with different mode
    print(f"Before load: {new_env.mode}")
    
    new_env.load_environment("example_env.json")
    print(f"After load: {new_env.mode}")
    print(f"Loaded tools: {new_env.list_tools()}")
    
    # Clean up
    import os
    if os.path.exists("example_env.json"):
        os.remove("example_env.json")


if __name__ == "__main__":
    # Run all examples
    example_basic_usage()
    example_inheritance_usage()
    example_custom_configuration()
    example_tool_management()
    example_environment_persistence()
    
    print("\n=== All examples completed ===")