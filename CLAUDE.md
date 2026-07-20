# CLAUDE.md

## 默认行为：始终使用技能系统

本项目在 `.claude/skills/` 下有一套完整的技能体系。**每次对话必须默认加载 `dev-assistant` 技能**作为入口，由其根据用户意图路由到对应的子技能。

### 技能文件位置

- 主入口：`.claude/skills/dev-assistant.md`
- 子技能：
  - `.claude/skills/scaffold.md` — 项目初始化
  - `.claude/skills/code-reviewer.md` — 代码审查
  - `.claude/skills/bug-fixer.md` — Bug 修复
  - `.claude/skills/test-helper.md` — 测试辅助
  - `.claude/skills/doc-generator.md` — 文档生成
  - `.claude/skills/git-workflow.md` — Git 工作流
  - `.claude/skills/todo.md` — 任务管理

### 工作流程

1. 收到用户请求后，首先读取 `.claude/skills/dev-assistant.md` 确定匹配的子技能
2. 根据匹配结果加载对应的子技能文件
3. 严格按照技能文件中定义的流程和规范执行
4. 所有输出和交互使用中文

### 参考实现：examples/

在写任何代码前，**必须先阅读 `.claude/skills/examples/` 中的参考实现**，确保风格、结构和架构与示例一致。

examples/ 展示了标准的模块结构：
- `src/<package>/interface/` — Protocol 定义（抽象，不依赖任何人）
- `src/<package>/core/` — 核心实现（只依赖 interface）
- `src/<package>/config/` — 默认配置
- `src/<package>/test/mock.py` — Mock 替身
- `app/` — 薄入口，只组装不写业务逻辑
- `tests/` — 端到端测试

每次开发新模块时，以 examples/ 为模板对照：
1. 接口是否定义在 interface/ 里？
2. 依赖方向是否正确（app → interface ← core）？
3. 是否有 mock 实现可以离线测试？
4. 测试是否分层（单元测试 + 进程监听）？

### 核心约定

- 主要语言：Python
- 文档语言：中文
- Commit 格式：<类型>: <模块>/<内容>（类型：改/新/删/重构/文档）
- 先读再改：修改代码前必须先用 Read 工具读取文件
- **先读 examples/ 再写新模块**：确保结构、风格与参考实现一致
- 不猜测：不确定时向用户确认
- 架构原则：数据流优先，依赖指向内层（app → interface ← core）
