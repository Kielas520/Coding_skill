# 开发助手 Skill — 输入输出接口

## SKILL.md（主入口）

**输入：** 用户自然语言描述的需求

**触发条件（description 中描述）：**
- 需要代码审查
- 需要初始化项目
- 需要写测试
- 需要生成文档
- 需要修复 bug
- 需要 git 提交/发版
- 项目管理相关操作

**输出：** 加载 system prompt 到上下文，引导后续行为

---

## Agents 接口

### scaffold

```
输入：
  - 项目名称
  - 可选：技术栈偏好（默认 Python）
  - 可选：目录结构偏好

输出：
  - 创建完整的项目目录骨架
  - pyproject.toml / requirements.txt
  - .gitignore
  - docs/ 目录骨架（7 个子目录）
  - git init 完成
  - 输出结构总览
```

### code-reviewer

```
输入：
  - 文件路径或目录路径

输出：
  - 问题列表（问题类型 | 位置 | 严重程度 | 建议修复）
  - 可选：自动修复（用户确认后执行）
```

### bug-fixer

```
输入：
  - 问题描述（自然语言）
  - 可选：复现步骤、日志、截图

输出：
  - 定位分析结果
  - 向用户的澄清问题（question tool）
  - docs/bugs/BUG-XXX.md（记录文件）
  - 修复方案（多选一）
  - 代码修改（用户指令后执行）
```

### test-helper

```
输入：
  - 目标代码文件或模块路径
  - 可选：测试方式偏好

输出：
  - 测试代码文件
  - 或测试方案建议（当无法直接写测试时）
  - 运行测试的命令
```

### doc-generator

```
输入：
  - 文档类型：design | dev-log | todo | bug | deprecated | env-setup | startup
  - 模块名（design 类型需要）
  - 可选：增量更新标记

输出：
  - 对应目录下的 .md 文件
  - 更新 docs/todo/current.md（如涉及新任务）
```

### git-workflow

```
输入：
  - 操作类型：commit | release <版本号>
  - 可选：commit message 手动指定

输出：
  - 中文 commit message
  - changelog（release 时）
  - git tag（release 时，用户确认后）
```

---

## Commands 接口

| 命令 | 参数 | 调用 |
|------|------|------|
| `/init <项目名>` | 项目名（必填） | scaffold agent |
| `/review <路径>` | 文件/目录路径（必填） | code-reviewer agent |
| `/fix <描述>` | 问题描述（必填） | bug-fixer agent |
| `/test <路径>` | 代码路径（必填） | test-helper agent |
| `/docs <类型> [模块名]` | 类型（必填），模块名（design时必填） | doc-generator agent |
| `/release <版本>` | 版本号（必填） | git-workflow agent |
| `/todo <操作> [内容]` | add/done/edit | 通用 agent |

---

## Prompts 接口

### doc-templates.md

被 doc-generator agent 的 prompt 字段引用，提供 7 类文档的 Markdown 模板。

### bug-workflow.md

被 bug-fixer agent 的 prompt 字段引用，提供 5 步流程的详细规范。

---

## opencode.jsonc 接口

```jsonc
{
  "model": "用户自填",
  "permission": {
    "skill": { "*": "allow" }
  },
  "agent": {
    "build": {
      "permission": { "skill": { "*": "allow" } }
    }
  }
}
```

最小配置，其余由 agents 和 commands 的 Markdown 文件自动发现。
