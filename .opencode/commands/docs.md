---
description: 生成项目文档。design/dev-log/todo/bug/deprecated/env-setup/startup
agent: build
---

请用 task 工具调用 doc-generator agent 来生成文档。

用户参数：$ARGUMENTS

文档类型包括：
- design <模块名> — 为指定模块生成 5 个设计文档
- dev-log — 生成今天的开发日志
- todo — 管理待办事项
- bug — 记录 Bug（通常由 bug-fixer 调用）
- deprecated — 记录废案
- env-setup — 环境配置文档
- startup — 启动文档

如果用户没有指定类型，请先询问要生成哪种文档。
生成时请按 prompts/doc-templates.md 中的模板格式，未知信息标注"待补充"。
