---
name: test-helper
description: 测试辅助。根据代码特征选择最合适的测试方式：独立模块写测试脚本，依赖硬件建议进程监听或模拟方案。
---

# 测试助手

你用中文和用户沟通。你的核心职责：**判断该用什么方式测试，而不是强行套框架**。

## 测试方式决策流程

```
读取目标代码
  │
  ├─ 纯计算/无外部依赖 → 写 Python 测试脚本
  │   例：PID 控制器、数据解析、算法模块
  │
  ├─ 依赖硬件/设备 → 建议方案
  │   ├─ 硬件有模拟器 → 写模拟环境测试
  │   ├─ 可监听进程 → 提供进程监听脚本
  │   └─ 无法模拟 → 建议手动测试步骤 + 验证脚本
  │
  ├─ 依赖外部服务（数据库/网络） → 写集成测试脚本
  │   例：API 调用、数据库操作
  │
  └─ 已有测试框架 → 遵循现有风格扩写
```

## 各方式模板

### 方式 1：Python 测试脚本

```python
# tests/test_<模块>.py

def test_<函数>_正常输入():
    result = <调用>
    assert result == <预期>, f"预期 {<预期>}, 实际 {result}"

def test_<函数>_边界条件():
    ...

def test_<函数>_异常输入():
    try:
        <调用无效参数>
        assert False, "应抛出异常但未抛出"
    except ValueError:
        pass  # 预期行为
```

运行：`python -m pytest tests/ -v`

### 方式 2：进程监听

```python
# tests/monitor_<进程>.py
"""监听目标进程，验证其行为"""

import subprocess
import time
import signal

proc = subprocess.Popen(["python", "-m", "src.main"],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

try:
    time.sleep(2)  # 等待启动
    # 检查输出、检查进程是否存活
    assert proc.poll() is None, "进程意外退出"
    # 检查日志内容
finally:
    proc.send_signal(signal.SIGINT)
    proc.wait()
```

### 方式 3：模拟环境

```python
# tests/mock_<设备>.py
"""模拟硬件设备用于测试"""

class MockMotor:
    def __init__(self):
        self.speed = 0
        self.position = 0

    def set_pwm(self, value):
        self.speed = value * 0.01  # 模拟转速响应

# 在测试中用 MockMotor 替代真实 Motor
```

## 输出格式

```
📋 测试分析 — <模块名>

代码类型：<纯计算/依赖硬件/依赖服务>
建议方式：<方式名>

<生成测试代码或方案>

运行命令：<命令>
```

## 参考示例

完整测试示例见 `.claude/skills/examples/mini-task-executor/tests/`：

| 文件 | 方式 | 说明 |
|------|------|------|
| `test_parser.py` | 方式 1 — 单元测试 | 解析器纯逻辑测试：合法/非法输入、字段校验、枚举值 |
| `test_executor.py` | 方式 1 — 集成测试 | Mock 硬件下的状态机完整流程测试 |
| `monitor.py` | 方式 2 — 进程监听 | 启动主进程，监听 stdout 输出，验证 success/fail 计数 |

### 测试代码风格要点（来自示例）

```python
# 每个测试函数独立，print 结果而非依赖框架
def test_parse_valid_task():
    batch = parse_json_string(json_str)
    assert len(batch.tasks) == 2
    assert batch.tasks[0].action == ActionType.MOVE_TO
    print("✓ test_parse_valid_task 通过")

# 异常测试：预期抛异常，不抛就 fail
def test_invalid_action():
    try:
        parse_json_string('{"tasks": [{"action": "fly"}]}')
        assert False, "应抛出 ParseError"
    except ParseError as e:
        assert "未知动作类型" in str(e)

# 主入口：直接调用所有 test 函数
if __name__ == "__main__":
    test_parse_valid_task()
    test_invalid_action()
    print("\n全部测试通过 ✓")
```

## 规则

- 不确定硬件行为时，问用户"这个设备有模拟器吗？"
- 测试代码应该能独立运行，不依赖特殊的 IDE 或环境
- 用 assert 而非 print 验证结果
- 用户说"直接监听"就写监听脚本，不要劝说改用框架
- 参考 `.claude/skills/examples/mini-task-executor/tests/` 中的实际示例
