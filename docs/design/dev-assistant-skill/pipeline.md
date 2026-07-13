# 开发助手 Skill — 数据管线总览

## 管线 1：新项目初始化

```
用户: /init my-robot
  │
  ▼
scaffold agent
  ├─ 创建目录结构
  ├─ 写入 pyproject.toml（Python 项目配置）
  ├─ 写入 .gitignore
  ├─ git init
  ├─ 创建 docs/ 骨架（7 个子目录）
  └─ 输出项目结构树
```

## 管线 2：日常开发 → 提交

```
用户编写代码
  │
  ▼
用户: /review src/motor.py
  │
  ▼
code-reviewer agent
  ├─ 读取代码 → 检查 → 输出报告
  └─ 询问是否自动修复
      ├─ 是 → edit 修改
      └─ 否 → 用户手动改
  │
  ▼
用户: /test src/motor.py
  │
  ▼
test-helper agent
  ├─ 分析代码 → 判断测试方式
  ├─ 写测试脚本 或 建议监听方案
  └─ 运行测试验证
  │
  ▼
用户: /release v0.1.0
  │
  ▼
git-workflow agent
  ├─ 收集变更 → 生成中文 commit message
  ├─ git add + git commit
  ├─ 生成 changelog
  ├─ git tag v0.1.0
  └─ 询问是否 push
```

## 管线 3：Bug 修复（5 步）

```
用户: /fix 电机启动时有几率丢步
  │
  ▼
bug-fixer agent
  │
  ├─ ① 定位
  │   ├─ 读取相关代码（电机驱动、定时器、中断处理）
  │   ├─ 搜索日志/错误信息
  │   └─ 输出：可能原因列表
  │
  ├─ ② 讨论
  │   ├─ 向用户提问（question tool）
  │   │   - 丢步频率？
  │   │   - 哪个电机？
  │   │   - 负载情况？
  │   └─ 确认理解无误
  │
  ├─ ③ 记录
  │   ├─ 创建 docs/bugs/BUG-003.md
  │   ├─ 写入：问题描述、复现步骤、定位分析
  │   └─ 更新 docs/todo/current.md
  │
  ├─ ④ 方案
  │   ├─ 输出 2-3 个修复方案
  │   ├─ 分析每个方案的优缺点
  │   └─ 建议一个推荐方案
  │
  └─ ⑤ 执行
      ├─ 等待用户指令（"用方案B"）
      ├─ edit 目标代码
      └─ 输出修改摘要
```

## 管线 4：文档生成

```
用户: /docs design sensor-module
  │
  ▼
doc-generator agent
  ├─ 读取 src/sensor/ 下代码
  ├─ 分析模块结构
  ├─ 按模板生成 5 个文件：
  │   ├─ docs/design/sensor-module/overview.md
  │   ├─ docs/design/sensor-module/data-flow.md
  │   ├─ docs/design/sensor-module/interface.md
  │   ├─ docs/design/sensor-module/design-rationale.md
  │   └─ docs/design/sensor-module/pipeline.md
  └─ 输出生成摘要

用户: /docs dev-log
  ├─ 读取今日 git log
  ├─ 生成 docs/dev-log/2026-07-13.md
  └─ 内容包含今日提交摘要 + 开发心得

用户: /docs env-setup
  ├─ 分析 requirements.txt / pyproject.toml
  ├─ 生成 docs/env-setup/python.md
  └─ 生成 docs/env-setup/dependencies.md
```

## 管线 5：任务管理

```
用户: /todo add 重构通信层，改用 zmq
  ├─ 读取 docs/todo/current.md
  ├─ 追加任务项
  └─ 输出当前待办列表

用户: /todo done 重构通信层
  ├─ 从 current.md 删除该项
  ├─ 追加到今日 dev-log 作为完成事项
  └─ 输出剩余待办

用户: /todo backlog 添加 Web 控制面板
  ├─ 读取 docs/todo/backlog.md
  ├─ 追加到 backlog
  └─ 输出"已加入 backlog"
```

## 管线总图

```
                    ┌──────────┐
                    │  用户需求  │
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
         /init       /review     /fix
         /test       /docs      /release
         /todo
              │          │          │
              ▼          ▼          ▼
        ┌─────────────────────────────────┐
        │        6 个 Agent + 技能         │
        │   scaffold / reviewer / fixer   │
        │    tester / doc-gen / git-wf    │
        └─────────────────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │       产出物          │
    ├──────────┬──────────┤
    │ 代码修改  │ 文档生成  │
    │ (edit/   │ (docs/)  │
    │  write)  │          │
    ├──────────┴──────────┤
    │     Git 操作          │
    │  commit / tag / push │
    └─────────────────────┘
```
