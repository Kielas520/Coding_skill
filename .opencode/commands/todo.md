---
description: 任务管理，维护当前待办和积压任务列表
agent: build
---

请管理项目的待办事项。

用户指令：$ARGUMENTS

操作类型：
- add <内容> — 添加到 docs/todo/current.md
- done <内容> — 从 current.md 移到完成记录
- backlog <内容> — 添加到 docs/todo/backlog.md
- list — 显示当前待办列表
- move <内容> — 从 backlog 移到 current

操作时：
1. 先读取 docs/todo/current.md 和 docs/todo/backlog.md
2. 按指令修改对应文件
3. 输出更新后的待办状态
