---
name: scaffold
description: 项目初始化。创建 Python 项目骨架、配置虚拟环境、初始化 git 仓库、生成 docs/ 目录结构。
---

# 项目脚手架

你用中文交互。快速为新项目生成标准骨架。

## 核心理念

程序开发的本质是数据处理。先画数据链路，定每个节点的输入输出，然后写代码填空。架构不是先画目录树，是先想清楚数据怎么流。

## 生成结构

```
<项目名>/
├── docs/                             # 文档（按用途分类）
│   ├── design/<模块名>/               #   overview / data-flow / interface / pipeline
│   ├── startup/                       #   启动指南
│   ├── env-setup/                     #   环境配置
│   ├── dev-log/                       #   开发日志
│   ├── todo/                          #   current.md + backlog.md
│   ├── bugs/                          #   Bug 记录
│   └── deprecated/                    #   废案记录
├── src/                              # 模块包（每个自包含）
│   └── <package>/
│       ├── lib/                       #   外部二进制依赖：.so、.bin、.whl
│       ├── core/                      #   核心程序（只依赖 interface，不依赖硬件）
│       ├── interface/                 #   Protocol 定义（抽象，不实现）
│       ├── config/                    #   默认配置文件
│       └── test/                      #   模块级测试（mock 替身放这里）
├── app/                              # 应用层（薄入口，只做组装）
│   └── task_app.py                   #   拿 interface → 创建实现 → 注入状态机
├── scripts/                          # 启动脚本（环境 + conda + exec python app）
├── tests/                            # 端到端测试（测 app 组装）
├── tools/                            # 外部辅助工具
├── envs/                             # 环境依赖文件
├── pyproject.toml
├── .gitignore
└── README.md
```

## 生成流程

1. 确认项目名称和技术栈偏好（默认 Python）
2. 创建目录结构
3. 写入 pyproject.toml
4. 写入 .gitignore
5. 写入 README.md（含项目名称和简要说明占位）
6. 写入 docs/ 下的占位文件（标题 + "待补充"）
7. 执行 `git init`
8. 输出项目结构树和后续建议

## pyproject.toml 模板

```toml
[project]
name = "<项目名>"
version = "0.1.0"
description = ""
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = ["pytest"]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.backends._legacy:_Backend"
```

## .gitignore 模板

```gitignore
__pycache__/
*.py[cod]
*.so
.env
.venv/
venv/
dist/
build/
*.egg-info/
.idea/
.vscode/
*.swp
*.swo
```

## 模块包内部结构

每个 `src/<package>/` 自包含，拎到别的项目也能独立跑：

| 目录 | 职责 | 依赖方向 |
|------|------|---------|
| `interface/` | Protocol 定义。这个包对外暴露什么能力 | 不依赖任何人 |
| `core/` | 核心逻辑。只 import interface，不知道硬件是什么 | → interface |
| `config/` | 默认配置。YAML + 环境变量覆盖 | 无 |
| `lib/` | 二进制依赖。.so、.bin、.whl 等无法 pip 安装的东西 | 无 |
| `test/` | 模块级测试。mock 替身放这里 | → interface, core |

核心规则：`core` 只依赖 `interface`，永远不知道 app 和具体硬件存在。app 负责把 interface 和具体实现接起来。

## 对于机器人/硬件项目

每个硬件模块都是一个 package，按上面的结构自包含：

```
src/
├── camera/
│   ├── interface/      Camera Protocol
│   ├── core/           kinect.py（实现）
│   ├── config/         默认 serial/fps
│   └── test/           mock.py
├── robot/
│   ├── interface/      Robot Protocol
│   ├── core/           tron2.py（实现）
│   ├── config/         默认 ip/port
│   └── test/           mock.py
└── vision/
    ├── interface/      Detector Protocol
    ├── core/           vlm.py / yolo.py
    └── test/           mock.py
```

app 负责组装：
```python
# app/grasp_app.py
from src.camera.core.kinect import KinectCamera
from src.robot.core.tron2 import Tron2Robot
from src.vision.core.vlm import VLMDetector

camera = KinectCamera(serial="...")
robot = Tron2Robot(ip="...")
detector = VLMDetector(model="...")
```

## 注意事项

- 如果目录已存在，只创建缺失的部分，不覆盖已有文件
- 如果已有 pyproject.toml，只补充不覆盖
- 创建完成后建议用户创建虚拟环境
