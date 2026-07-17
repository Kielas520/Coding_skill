# Mini 任务执行器

演示项目构建范式：模块自包含 + app 组装。

## 快速开始

```bash
cd .claude/skills/examples
pip install -e .
python app/task_app.py               # Mock 模式，无需硬件
python app/task_app.py --real 10.0.0.1  # 真设备
bash scripts/task.sh                  # 脚本启动
```

## 架构

```
demo_task.json（任务描述）
      │
      ▼
app/task_app.py          ← 薄入口：组装 + 状态机 + CLI
      │
      ├── src/robot/interface/   Robot Protocol（抽象）
      ├── src/robot/core/        RealRobot（真硬件，占位）
      └── src/robot/test/mock.py MockRobot（离线测试）

依赖方向：app → interface ← core/mock
         app 负责接线，core 不知道 app 存在
```

## 项目结构

```
examples/
├── src/robot/             一个自包含的模块包
│   ├── interface/          Robot Protocol — 定义"机器人能干什么"
│   ├── core/               核心实现 — 只依赖 interface
│   ├── config/             默认配置
│   └── test/mock.py        Mock 替身 — 离线测试用
├── app/task_app.py         组装层 — 拿 interface，创建实现，注入状态机
├── scripts/task.sh         启动脚本
├── tests/                  端到端测试
├── pyproject.toml
└── demo_task.json          任务定义
```

## 和旧版的区别

旧版（flat 三层）：`src/config/` `src/task/` `src/hardware/` 平铺在一起，模块职责模糊。

新版（模块自包含）：每个 `src/<package>/` 是独立闭环，有 interface/core/config/test。`app/` 拆出来专门做组装。一个包拷到别的项目直接能用。

## 自定义任务

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

## 测试

```bash
python tests/test_task.py    # 单元测试（mock 硬件）
python tests/monitor.py      # 进程监听（验证 app 能跑通）
```
