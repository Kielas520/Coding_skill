---
description: Bug 修复，五步流程：定位→讨论→记录→方案→执行
agent: build
---

请用 task 工具调用 bug-fixer agent 来修复 Bug。

问题描述：$ARGUMENTS

如果没有描述，请先询问用户遇到了什么问题。

请严格遵守五步流程：
① 定位根因 → ② 和用户讨论澄清 → ③ 记录到 docs/bugs/ → ④ 提供修复方案 → ⑤ 等用户指令后执行修改
在用户明确指令之前不要修改任何代码。
