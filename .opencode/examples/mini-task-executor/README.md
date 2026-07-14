# Mini 任务执行器

开箱即用的任务执行器示例，演示架构至上的模块化设计。

## 快速开始

```bash
cd .opencode/examples/mini-task-executor
pip install -e .
python -m src.main --task demo_task.json
```

## 运行方式

| 模式 | 命令 | 说明 |
|------|------|------|
| Mock 仿真 | `python -m src.main --task demo_task.json` | 无需硬件，默认模式 |
| 强制 Mock | `python -m src.main --task demo_task.json --mock` | 同上 |
| 真实硬件 | `python -m src.main --task demo_task.json --real` | 连接真实设备 |

## 架构

```
用户 JSON 任务
  │
  ▼
parser.py     → 解析 + 校验 → TaskInstruction 列表
  │
  ▼
executor.py   → 状态机执行
  │              IDLE → MOVING → GRASPING → RELEASING → SENSING
  ▼
interface.py  → 硬件抽象接口（Protocol）
  ├─ mock.py     模拟硬件（带噪声 + 延迟）
  └─ real.py     真实硬件（占位）
  │
  ▼
结果输出（TaskResult 列表）
```

## 三层设计

| 层 | 职责 | 切换方式 |
|----|------|---------|
| 配置层 `config/` | YAML 加载 + 环境变量覆盖 | 改 `defaults.yaml` 或设 `TASK_EXEC_*` 环境变量 |
| 任务层 `task/` | 解析 + 状态机执行 | 改任务 JSON 文件 |
| 硬件层 `hardware/` | 抽象接口 + Mock/Real 实现 | 改 `defaults.yaml` 中 `hardware.mock: true/false` |

## 自定义任务

创建 JSON 文件，按以下格式写任务：

```json
{
    "label": "任务名称",
    "tasks": [
        {"action": "move_to", "target": {"x": 0.1, "y": 0.0, "z": 0.05}},
        {"action": "grasp"},
        {"action": "move_to", "target": {"x": 0.2, "y": 0.1, "z": 0.1}},
        {"action": "release"},
        {"action": "read_sensor"},
        {"action": "wait", "duration_ms": 500}
    ]
}
```

支持的动作：`move_to`、`grasp`、`release`、`wait`、`read_sensor`

## 测试

```bash
# 单元测试
python tests/test_parser.py
python tests/test_executor.py

# 进程监听测试
python tests/monitor.py
```

## 开发助手上手指南

1. 把这个 `.opencode/` 目录整体复制到你的项目
2. 告诉 AI：`/init <项目名>` 初始化新项目
3. 开发完成后 `/review <文件>` 审查代码
4. 遇到 Bug `/fix <描述>` 按五步流程修复
5. 代码写好后 `/test <文件>` 自动生成测试
6. 提交前 `/release <版本>` 管理 Git
