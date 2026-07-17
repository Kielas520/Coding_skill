---
name: git-workflow
description: Git 工作流。中文 commit、分支策略、版本发布、changelog 生成、tag 管理。
---

# Git 工作流

你用中文和用户沟通。管理项目的提交、分支、版本发布和 changelog。

## 分支策略

```
main                   永远可部署。只接受 merge，不直接 commit
feature/<功能名>        每个新功能从 main 拉分支，做完合回去
fix/<问题>             修 bug 从 main 拉，修完合回去
release/<版本号>        发布前冻结，只修 bug，发版后合回 main 并打 tag
```

## Commit 规范

### 格式

```
<类型>: <模块>/<内容>
```

### 类型

| 类型 | 用途 |
|------|------|
| 改 | 功能变更或 bug 修复（最常用） |
| 新 | 新增文件或模块 |
| 删 | 删除文件或废弃功能 |
| 重构 | 不改变行为的代码整理 |
| 文档 | 纯文档改动 |

### 示例

```
改 grasp/vlm: 修复手眼变换中 R_gripper2base 的求逆逻辑
新 camera: 新增 Kinect 深度 ROI 缩放功能
重构 lib/: 按模块分类整理目录结构
删 ros_ws: 删除 ROS2 工作空间，由 ros2_bridge 替代
文档 project.md: 补充错误处理分类和可观测性规范
```

### 规则

- 第一行不超过 72 个字符
- 说清楚"改了哪个模块的什么内容"
- 别写"fix bug"、"update code"——等于没写
- 不相关的问题分开提交

## 版本号（Semantic Versioning）

```
MAJOR.MINOR.PATCH    例：1.3.2

MAJOR：不兼容的 API 改动（别人升级要改代码）
MINOR：新增功能，向后兼容
PATCH：bug 修复，向后兼容

开发阶段用 0.Y.Z（0.1.0 → 0.2.0），API 稳定后升到 1.0.0
```

## Release 流程

1. 确认 main 分支所有测试通过
2. 运行 `git log --oneline` 获取未 tag 的 commit 列表
3. 按类型分组（新/改/删/重构/文档），生成 changelog
4. 询问版本号确认
5. 更新 pyproject.toml 的 version
6. 用户确认后执行：
   ```bash
   git tag -a v<版本号> -m "<版本描述>"
   git push origin main --tags
   ```

## Changelog 模板

```markdown
# v<版本号> (<日期>)

## 新
- <commit>

## 改
- <commit>

## 删
- <commit>

## 重构
- <commit>

## 文档
- <commit>
```

## 安全规则

- 永远不 force push
- push 前必须用户确认
- 不删除已有 tag
- 不修改远程分支历史
