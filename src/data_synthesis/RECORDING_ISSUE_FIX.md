# 屏幕录制问题修复总结

## 问题描述

运行探索式数据合成时出现录制失败错误：

```
Starting screen recording...
Failed to start recording. Status code: 400
Failed to start recording. Status code: 400
Failed to start recording. Status code: 400
Failed to start recording.
```

## 错误来源

错误信息来自 `/home/a1/sdb/tzw/AgentFlow/src/utils/desktop_env/controllers/python.py` 第 422 行：

```python
def start_recording(self):
    """Starts recording the screen."""
    for _ in range(self.retry_times):
        try:
            response = requests.post(self.http_server + "/start_recording")
            if response.status_code == 200:
                logger.info("Recording started successfully")
                return
            else:
                logger.error("Failed to start recording. Status code: %d", response.status_code)
                logger.info("Retrying to start recording.")
        except Exception as e:
            logger.error("An error occurred while trying to start recording: %s", e)
            logger.info("Retrying to start recording.")
        time.sleep(self.retry_interval)
    
    logger.error("Failed to start recording.")
```

### 调用链

1. `exploration_pipeline.py` → `env_task_init(dummy_task)`
2. `osworld_environment.py` → `start_recording()`
3. `python.py` (PythonController) → `start_recording()`
4. 向 HTTP 服务器发送 POST 请求 → 返回 400 错误

## 失败原因

Status code: 400 表示 HTTP 服务器拒绝了录制请求，可能的原因：
1. 录制服务未正确启动
2. 已有录制正在进行中
3. 服务器配置问题
4. ffmpeg 未正确配置

## 解决方案

### 方案1：禁用录制（推荐用于探索模式）

探索模式主要关注轨迹采样和数据生成，不需要视频录制。

#### 修改内容

**1. 在 `osworld_environment.py` 中添加 `enable_recording` 配置选项**

```python
# env_task_init 方法
# Start screen recording (optional, can be disabled)
# Check if recording is enabled (default: True for backward compatibility)
enable_recording = self.config.get("osworld", {}).get("enable_recording", True)

if enable_recording:
    print(f"   Starting screen recording...")
    try:
        self.start_recording()
    except Exception as e:
        print(f"   ⚠️  Warning: Screen recording failed: {e}")
        print(f"   ℹ️  Continuing without recording...")
else:
    print(f"   ℹ️  Screen recording disabled (enable_recording=False)")
```

```python
# env_task_end 方法
# End screen recording and save (if recording was enabled)
enable_recording = self.config.get("osworld", {}).get("enable_recording", True)

if enable_recording and task_output_dir:
    try:
        recording_path = os.path.join(task_output_dir, f"task_{task_id}.mp4")
        print(f"   Stopping screen recording...")
        self.end_recording(recording_path)
        print(f"   Recording saved to: {recording_path}")
    except Exception as e:
        print(f"   ⚠️  Warning: Failed to save recording: {e}")
```

**2. 在配置文件中禁用录制**

`osworld_exploration_config.json`:
```json
{
  "environment_kwargs": {
    "path_to_vm": "...",
    "provider_name": "vmware",
    "action_space": "computer_13",
    "observation_type": "screenshot_a11y_tree",
    "screen_width": 1920,
    "screen_height": 1080,
    "headless": true,
    "client_password": "password",
    "sleep_after_execution": 2.0,
    "enable_recording": false  // ⬅️ 添加此行
  },
  ...
}
```

### 方案2：修复录制服务（用于需要视频的场景）

如果确实需要视频录制，需要检查和修复录制服务：

#### 检查步骤

1. **检查 HTTP 服务器状态**
   ```bash
   # 检查服务器是否运行
   curl -X POST http://localhost:5000/start_recording
   ```

2. **检查 ffmpeg 是否安装**
   ```bash
   which ffmpeg
   ffmpeg -version
   ```

3. **检查服务器日志**
   查看 `/home/a1/sdb/tzw/AgentFlow/src/utils/desktop_env/server/main.py` 的日志输出

4. **检查是否有残留的录制进程**
   ```bash
   ps aux | grep ffmpeg
   # 如果有，杀死进程
   pkill ffmpeg
   ```

#### 可能的修复

1. **确保 HTTP 服务器正常启动**
   - 检查端口是否被占用
   - 检查服务器日志错误

2. **重启 DesktopEnv**
   - 完全关闭并重新启动环境

3. **清理录制状态**
   - 确保没有遗留的录制进程

## 配置选项说明

### `enable_recording` 参数

- **位置**: `environment_kwargs` 中
- **类型**: `boolean`
- **默认值**: `true` (保持向后兼容)
- **用途**: 控制是否启用屏幕录制

#### 何时设置为 `false`

- ✅ 探索式数据合成（不需要视频）
- ✅ 快速测试和调试
- ✅ 录制服务有问题时的临时方案
- ✅ 节省磁盘空间和性能

#### 何时保持为 `true`

- ✅ 正式任务评估（需要视频记录）
- ✅ 演示和可视化
- ✅ 调试agent行为（需要视频回放）

## 验证修复

运行探索式数据合成，应该看到：

### 禁用录制时（推荐）
```
🔍 步骤 1/3: 探索式Trajectory Sampling
开始在GUI环境中自由探索...
   任务输出目录: exploration_results/osworld/explore_0001/gpt-4.1
   Initializing OSWorld environment for task explore_0001...
   Resetting desktop environment...
   ℹ️  Screen recording disabled (enable_recording=False)
   Getting initial observation...
   ✓ 获得初始观察
```

### 启用但失败时（会继续执行）
```
   Starting screen recording...
   ⚠️  Warning: Screen recording failed: ...
   ℹ️  Continuing without recording...
```

## 受影响的文件

1. `/home/a1/sdb/tzw/AgentFlow/src/envs/osworld_environment.py`
   - `env_task_init()` 方法：添加 `enable_recording` 检查
   - `env_task_end()` 方法：只在启用时停止录制

2. `/home/a1/sdb/tzw/AgentFlow/src/data_synthesis/configs/osworld_exploration_config.json`
   - 添加 `"enable_recording": false`

## 参考资源

- **录制控制器**: `/home/a1/sdb/tzw/AgentFlow/src/utils/desktop_env/controllers/python.py`
- **HTTP 服务器**: `/home/a1/sdb/tzw/AgentFlow/src/utils/desktop_env/server/main.py`
- **环境实现**: `/home/a1/sdb/tzw/AgentFlow/src/envs/osworld_environment.py`

---

**修复时间**: 2025-11-10  
**修复内容**: 添加 `enable_recording` 配置选项，允许禁用屏幕录制  
**影响范围**: OSWorld 环境的探索模式配置

