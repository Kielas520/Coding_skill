---
description: 版本发布，生成 changelog 并打 tag
agent: build
---

请用 task 工具调用 git-workflow agent 来执行发布。

版本号：$ARGUMENTS

如果没有指定版本号，请先询问用户。

流程：
1. 收集未 tag 的 commit
2. 生成中文 changelog
3. 确认版本号
4. 用户确认后打 tag 并询问是否 push
不要 force push，不要删除已有 tag。
