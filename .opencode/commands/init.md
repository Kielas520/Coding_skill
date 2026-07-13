---
description: 初始化新项目，生成 Python 项目骨架和目录结构
agent: build
---

请用 task 工具调用 scaffold agent 来初始化项目。

项目名称：$ARGUMENTS

如果用户没有指定项目名称，请先询问。
请确保：
1. 创建标准 Python 项目目录结构
2. 生成 pyproject.toml 和 .gitignore
3. 创建 docs/ 目录骨架（7 个子目录）
4. 执行 git init
5. 输出项目结构树和后续建议
