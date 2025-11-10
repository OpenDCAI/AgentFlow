#!/usr/bin/env python3
"""Test import structure after refactoring."""

print("Testing imports...")

# Test 1: Import data models directly
try:
    from envs.data_models import Observation, TrajectoryStep, TaskTrajectory
    print("✓ Data models imported successfully from envs.data_models")
except ImportError as e:
    print(f"✗ Failed to import data models: {e}")

# Test 2: Import base classes directly
try:
    from envs.enviroment import Environment, Tool
    print("✓ Base classes imported successfully from envs.enviroment")
except ImportError as e:
    print(f"✗ Failed to import base classes: {e}")

# Test 3: Import OSWorld environment
try:
    from envs.osworld_environment import OSWorldEnvironment
    print("✓ OSWorldEnvironment imported successfully")
except ImportError as e:
    print(f"✗ Failed to import OSWorldEnvironment: {e}")

# Test 4: Import individual environments (may fail due to tool dependencies)
try:
    from envs.math_environment import MathEnvironment
    print("✓ MathEnvironment imported successfully")
except ImportError as e:
    print(f"⚠ MathEnvironment import failed (tool dependency): {e}")

try:
    from envs.python_environment import PythonEnvironment
    print("✓ PythonEnvironment imported successfully")
except ImportError as e:
    print(f"⚠ PythonEnvironment import failed (tool dependency): {e}")

try:
    from envs.rag_environment import RAGEnvironment
    print("✓ RAGEnvironment imported successfully")
except ImportError as e:
    print(f"⚠ RAGEnvironment import failed (tool dependency): {e}")

try:
    from envs.web_environment import WebEnvironment
    print("✓ WebEnvironment imported successfully")
except ImportError as e:
    print(f"⚠ WebEnvironment import failed (tool dependency): {e}")

try:
    from envs.tbench_environment import TBenchEnvironment
    print("✓ TBenchEnvironment imported successfully")
except ImportError as e:
    print(f"⚠ TBenchEnvironment import failed: {e}")

# Test 5: Check that envs package exports work
print("\nTesting package-level imports...")
try:
    import envs
    assert hasattr(envs, 'Observation')
    assert hasattr(envs, 'Environment')
    assert hasattr(envs, 'OSWorldEnvironment') is False  # OSWorld not in __init__.py
    print("✓ Package-level imports working correctly")
except (ImportError, AssertionError) as e:
    print(f"✗ Package-level imports failed: {e}")

print("\n✓ Import structure test completed!")
