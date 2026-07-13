# 开发助手 Skill — 数据流

## 总体流向

```
用户输入
  │
  ├─→ opencode 匹配 SKILL.md 描述 → 自动加载 skill → Agent 执行
  │
  └─→ /command 触发 → commands/<name>.md → Agent 执行
                              │
                              ▼
                    Agent 按 system prompt 执行
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
                  文件操作   提问用户   调用子Agent
                  (edit/    (question   (task tool →
                   write)    tool)      更细粒度)
                    │
                    ▼
                 项目文件 / docs/ / git
```

## 各 Agent 数据流

### scaffold

```
/init <项目名>
  → 读取现有项目结构
  → 生成目录树
  → 配置 pyproject.toml / requirements.txt
  → 初始化 git repo
  → 创建 docs/ 目录骨架
  → 输出项目结构报告
```

### code-reviewer

```
/review <文件或目录>
  → 读取目标代码
  → 按规范检查（命名、风格、性能、潜在bug）
  → 输出审查报告（问题列表 + 建议）
  → 询问用户是否需要自动修复
```

### bug-fixer（5 步流程）

```
/fix <问题描述>
  │
  ├─ ① 定位：读取相关代码 → 分析可能原因
  ├─ ② 讨论：向用户提问澄清 → 确认理解
  ├─ ③ 记录：写入 docs/bugs/BUG-XXX.md
  ├─ ④ 方案：输出修复方案（多选一供用户选择）
  └─ ⑤ 执行：收到用户指令后 edit/write 修改代码
```

### test-helper

```
/test <目标代码>
  → 分析代码结构和依赖
  → 判断测试方式：
      - 可独立运行 → 写 Python 测试脚本
      - 依赖硬件/进程 → 建议监听进程或模拟方案
  → 询问用户偏好
  → 生成测试代码
```

### doc-generator

```
/docs <文档类型> <模块名>
  → 读取目标代码/项目状态
  → 按 doc-templates.md 模板生成文档
  → 写入 docs/ 对应目录
  → 可增量更新已有文档
```

### git-workflow

```
/release <版本号>
  → 读取 git log 收集变更
  → 生成中文 commit 列表
  → 询问版本号确认
  → 执行 tag + push（需用户确认）
```

## 数据存储位置

| 数据类型 | 位置 | 格式 |
|---------|------|------|
| 设计文档 | `docs/design/<module>/` | 5 个 .md 文件 |
| 开发日志 | `docs/dev-log/YYYY-MM-DD.md` | 按日期 |
| 待办 | `docs/todo/` | current.md + backlog.md |
| Bug 记录 | `docs/bugs/BUG-XXX.md` | 按编号 |
| 废案 | `docs/deprecated/` | 按方案名 |
| 环境配置 | `docs/env-setup/` | python.md + dependencies.md |
| 启动文档 | `docs/startup/debug.md` + `production.md` | 两份 |
