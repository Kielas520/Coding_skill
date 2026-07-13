---
description: 生成测试，根据代码特征自动选择测试方式
agent: build
---

请用 task 工具调用 test-helper agent 来生成测试。

目标代码：$ARGUMENTS

如果没有指定文件，请先询问用户要测试什么。

请判断代码类型并选择最合适的测试方式：
- 纯计算模块 → Python 测试脚本
- 依赖硬件的 → 监听脚本或模拟方案
- 依赖外部服务的 → 集成测试
