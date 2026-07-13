# 开发助手 Skill — 任务实现纵览

## 目标

构建一个可移植的 `.opencode/` 全栈开发助手包，覆盖日常开发的完整生命周期。用户只需将 `.opencode/` 目录复制到任意项目中即可启用全部能力。

## 使用场景

- 机器人应用开发（Python 为主，C++ 提速模块）
- 服务端与客户端全栈开发
- 个人项目，多项目复用

## 核心能力

| 能力 | 负责组件 | 入口 |
|------|---------|------|
| 项目初始化/脚手架 | scaffold agent | `/init` |
| 代码规范检查 | code-reviewer agent | `/review` |
| Bug 修复 | bug-fixer agent | `/fix` |
| 测试 | test-helper agent | `/test` |
| 文档生成 | doc-generator agent | `/docs` |
| Git 工作流 | git-workflow agent | `/release` |
| 任务管理 | 通用 agent | `/todo` |

## 组件架构

```
.opencode/
├── opencode.jsonc          配置入口（权限、模型）
├── skills/
│   └── dev-assistant/
│       └── SKILL.md        主 Skill：描述何时触发、走什么流程
├── agents/                 6 个专用 Agent（含 system prompt 和行为规范）
├── commands/               7 个斜杠命令（触发不同 Agent）
└── prompts/                2 个公共模板（文档结构 + Bug 流程）
```

## 用户交互流程

```
用户说 → SKILL.md 匹配 → 路由到对应 Agent → Agent 按规范执行 → 产出
                              ↑
                        也可用 /command 直接触发
```

## 产出物

| 类别 | 产出 |
|------|------|
| 代码 | 通过 `edit`/`write` 工具直接修改项目文件 |
| 文档 | 7 类文档，写入 `docs/` 目录 |
| Git | 中文 commit，格式："改 <模块> 的 <内容> 解决了 <问题>" |
| 测试 | 灵活的测试方案（脚本/进程监听/模拟），不绑定框架 |
