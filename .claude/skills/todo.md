---
name: todo
description: 任务管理，维护当前待办和积压任务列表。支持 add/done/backlog/list/move 操作。
---

# 任务管理

请管理项目的待办事项。

## 操作类型

- add <内容> — 添加到 docs/todo/current.md
- done <内容> — 从 current.md 移到完成记录
- backlog <内容> — 添加到 docs/todo/backlog.md
- list — 显示当前待办列表
- move <内容> — 从 backlog 移到 current

## 操作流程

1. 先读取 docs/todo/current.md 和 docs/todo/backlog.md
2. 按指令修改对应文件
3. 输出更新后的待办状态

## 文件格式

### docs/todo/current.md

```markdown
# 当前待办

## 进行中

- [ ] 

## 等待中（阻塞）

- [ ] 

## 近期计划（本周）

- [ ] 
- [ ] 
```

### docs/todo/backlog.md

```markdown
# 积压任务

## 高优先级

- [ ] 

## 中优先级

- [ ] 

## 低优先级

- [ ] 

## 想法/探索

- [ ] 
```

## 规则

- 操作前必须先读取当前文件状态
- 完成的任务从列表中移除并记录日期
- backlog 移到 current 时保留原始描述
- 不确定优先级时询问用户
