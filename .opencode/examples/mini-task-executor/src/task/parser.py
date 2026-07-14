"""任务解析器。

将 JSON 格式的任务描述解析为 TaskBatch。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .schema import ActionType, Position, TaskBatch, TaskInstruction


class ParseError(Exception):
    """任务解析错误。"""
    pass


def _require_string(obj: dict, key: str) -> str:
    val = obj.get(key)
    if not isinstance(val, str):
        raise ParseError(f"字段 '{key}' 必须是字符串，收到: {type(val).__name__}")
    return val


def _require_number(obj: dict, key: str) -> float:
    val = obj.get(key)
    if not isinstance(val, (int, float)):
        raise ParseError(f"字段 '{key}' 必须是数字，收到: {type(val).__name__}")
    return float(val)


def _parse_target(step: dict) -> Position:
    target = step.get("target", {})
    if not isinstance(target, dict):
        raise ParseError(f"'target' 必须是对象，收到: {type(target).__name__}")
    return Position(
        x=_require_number(target, "x"),
        y=_require_number(target, "y"),
        z=_require_number(target, "z"),
    )


def _parse_instruction(step: dict) -> TaskInstruction:
    action_str = _require_string(step, "action")
    try:
        action = ActionType(action_str)
    except ValueError:
        raise ParseError(
            f"未知动作类型 '{action_str}'，合法值: "
            f"{[a.value for a in ActionType]}"
        )

    target: Optional[Position] = None
    if action == ActionType.MOVE_TO:
        target = _parse_target(step)

    return TaskInstruction(
        action=action,
        target=target,
        duration_ms=int(step.get("duration_ms", 0)),
        label=step.get("label", ""),
    )


def parse_json_file(filepath: str) -> TaskBatch:
    """从 JSON 文件解析任务批次。

    JSON 格式示例:
    {
        "label": "demo-任务",
        "tasks": [
            {"action": "move_to", "target": {"x": 0.1, "y": 0.0, "z": 0.05}},
            {"action": "grasp", "label": "抓取物体"},
            {"action": "move_to", "target": {"x": 0.2, "y": 0.1, "z": 0.1}},
            {"action": "release", "label": "放置物体"}
        ]
    }

    Args:
        filepath: JSON 文件路径

    Returns:
        TaskBatch 对象

    Raises:
        ParseError: JSON 格式或字段值不合法
        FileNotFoundError: 文件不存在
    """
    path = Path(filepath).expanduser().resolve()
    with open(path) as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ParseError("JSON 根元素必须是对象")
    if "tasks" not in data:
        raise ParseError("缺少 'tasks' 字段")
    if not isinstance(data["tasks"], list):
        raise ParseError("'tasks' 必须是数组")

    tasks: list[TaskInstruction] = []
    for i, step in enumerate(data["tasks"]):
        if not isinstance(step, dict):
            raise ParseError(f"tasks[{i}] 必须是对象")
        try:
            tasks.append(_parse_instruction(step))
        except ParseError as e:
            raise ParseError(f"tasks[{i}]: {e}")

    return TaskBatch(
        tasks=tasks,
        label=data.get("label", ""),
    )


def parse_json_string(json_str: str) -> TaskBatch:
    """从 JSON 字符串解析任务批次。

    Args:
        json_str: JSON 字符串

    Returns:
        TaskBatch 对象
    """
    data = json.loads(json_str)
    if not isinstance(data, dict):
        raise ParseError("JSON 根元素必须是对象")
    if "tasks" not in data:
        raise ParseError("缺少 'tasks' 字段")
    if not isinstance(data["tasks"], list):
        raise ParseError("'tasks' 必须是数组")

    tasks: list[TaskInstruction] = []
    for i, step in enumerate(data["tasks"]):
        if not isinstance(step, dict):
            raise ParseError(f"tasks[{i}] 必须是对象")
        tasks.append(_parse_instruction(step))

    return TaskBatch(
        tasks=tasks,
        label=data.get("label", ""),
    )
