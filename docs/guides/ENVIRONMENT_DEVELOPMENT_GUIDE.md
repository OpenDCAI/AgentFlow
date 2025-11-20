# AgentFlow Environment Development Guide

## Overview

AgentFlow environments share a unified lifecycle and are created through a central factory (`envs.factory`). This guide explains how to add a new environment that plays well with the AgentRunner and existing infrastructure.

## 1. Know the Lifecycle

All environments must implement the following hooks defined in `envs/environment.py`:

- `__init__(self, **kwargs)`: Set up configuration. Pass `defer_init=True` to the base class if heavy resources should wait until `env_start()`.
- `_initialize_tools(self)`: Register tools and do heavy initialization. Called automatically unless deferred.
- `env_start(self)`: Optional environment-wide setup (called once per benchmark run). Typically used when `defer_init=True`.
- `env_task_init(self, task)`: Reset for a specific task and return the initial observation (dict with optional `text` / `image`).
- `env_task_end(self, task_id, task_output_dir, final_answer)`: Task cleanup (recordings, logs).
- `env_close(self)`: Environment-wide cleanup.

Other helpers you can override:
- `get_system_prompt(question)`: Customize prompt construction.
- `format_observation_for_message(observation)`: Convert raw data to message parts if you stay with raw observations.
- `format_initial_observation_for_message(initial_obs)`: Convert the simplified dict returned by `env_task_init` to message parts.
- `has_internal_evaluation()`: Return `True` if the environment can compute its own score (e.g., OSWorld).

## 2. Create Your Environment Class

```python
from envs.environment import Environment

class MyEnvironment(Environment):
    @property
    def mode(self) -> str:
        return "myenv"

    def _initialize_tools(self):
        # Register tools, set up connections, etc.
        self.register_tool(MyTool(self))

    def env_task_init(self, task):
        # Perform task-specific reset
        self._setup_state(task)
        return {"text": "Initial state description"}

    def env_task_end(self, task_id, task_output_dir=None, final_answer=None):
        # Save logs, recordings, etc.
        pass

    def env_close(self):
        # Release any long-lived resources
        self._cleanup()
```

If your environment spins up heavy resources (VMs, containers, external services), instantiate the base class with `defer_init=True` via `super().__init__(defer_init=True, **kwargs)`. Then perform the heavy setup inside `_initialize_tools()`. The base class will call `_initialize_tools()` the first time `env_start()` runs.

## 3. Register the Environment

Registration lets the factory return the new environment without modifying runner code.

```python
from envs.factory import register_environment
register_environment("myenv", MyEnvironment)
```

The built-in environments are auto-registered in `envs/factory.py`. Custom registrations can live in your own modules (e.g., plugin packages) as long as they execute before the environment is needed.

## 4. Use it with AgentRunner

```python
from run_osworld import AgentRunner, AgentConfig
from envs.factory import register_environment

register_environment("myenv", MyEnvironment)

config = AgentConfig(model_name="gpt-4")
runner = AgentRunner(config)
runner.setup_environment("myenv", **env_kwargs)
runner.load_benchmark("data.jsonl")
runner.run_benchmark(parallel=False)
```

No changes to `AgentRunner` are required; the factory handles instantiation.

## 5. Support Parallel Execution

AgentFlow supports multi-process execution. To ensure compatibility:

- Use `defer_init=True` in environments with heavy resources (VMs, containers). The main process will skip initialization, while worker processes call `env_start()` to spin up their own instances.
- If you store initialization arguments (e.g., credentials), keep them in simple serializable structures; they are passed to workers via the factory.
- Clean up resources in `env_close()` so worker shutdowns do not leak resources.

## 6. Provide Observations and Evaluation

- Use `format_observation_by_type()` if your environment needs to support different observation modes (text/image combos).
- If the environment can evaluate tasks internally (e.g., verifying file states), implement `has_internal_evaluation()` to return `True` and provide an `evaluate()` method returning a score.
- For logging/recordings, store data inside `env_task_init()` / `env_task_end()`.

## 7. Testing Checklist

Before shipping a new environment:

- [ ] `env_task_init` returns the expected observation format
- [ ] Tools are correctly registered and discoverable (`environment.list_tools()`)
- [ ] `env_start` / `env_close` properly manage resources
- [ ] Parallel mode works (`runner.run_benchmark(parallel=True)`) without extra resources left behind
- [ ] Internal evaluation (if any) returns consistent scores
- [ ] Error cases are handled gracefully (failed reset, missing config, etc.)

Following these steps keeps new environments consistent with the rest of AgentFlow and ensures seamless integration with the runner and multi-process execution.
