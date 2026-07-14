"""配置加载器。

仿 magpie_srv 的 src/common/config.py 设计：
- YAML 文件加载
- 环境变量覆盖（MAGPIE_* 前缀）
- 路径展开（~ 展开为 $HOME）
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml


def _expand_env(value: str) -> str:
    """展开字符串中的 ${VAR} 和 $VAR 环境变量。"""
    pattern = re.compile(r"\$\{(\w+)\}|\$(\w+)")
    def _replace(m: re.Match) -> str:
        var_name = m.group(1) or m.group(2)
        return os.environ.get(var_name, m.group(0))
    return pattern.sub(_replace, value)


def _expand_dict(obj: Any) -> Any:
    """递归展开 dict 中的环境变量。"""
    if isinstance(obj, str):
        return _expand_env(obj)
    if isinstance(obj, dict):
        return {k: _expand_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_dict(v) for v in obj]
    return obj


def _apply_env_overrides(config: dict, prefix: str = "TASK_EXEC_") -> dict:
    """用环境变量覆盖配置值。

    环境变量命名规则：TASK_EXEC_<SECTION>_<KEY>
    例如：TASK_EXEC_HARDWARE_MOCK=false → config["hardware"]["mock"] = "false"
    支持嵌套两层（section.key）。
    """
    for env_key, env_val in os.environ.items():
        if not env_key.startswith(prefix):
            continue
        parts = env_key[len(prefix):].lower().split("_", 1)
        if len(parts) != 2:
            continue
        section, key = parts
        if section in config and isinstance(config[section], dict):
            config[section][key] = env_val
    return config


def load_config(yaml_path: str) -> dict:
    """加载 YAML 配置并应用环境变量覆盖。

    Args:
        yaml_path: YAML 配置文件路径

    Returns:
        展开环境变量后的配置字典
    """
    path = Path(yaml_path).expanduser().resolve()
    with open(path) as f:
        config: dict = yaml.safe_load(f)

    config = _expand_dict(config)
    config = _apply_env_overrides(config)
    return config
