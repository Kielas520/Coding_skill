"""任务数据模型。

定义整个任务执行链路的数据结构。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ActionType(str, Enum):
    """任务动作类型。"""
    MOVE_TO     = "move_to"        # 移动到目标位置
    GRASP       = "grasp"          # 抓取
    RELEASE     = "release"        # 释放
    WAIT        = "wait"           # 等待
    READ_SENSOR = "read_sensor"    # 读取传感器


@dataclass
class Position:
    """三维位置。"""
    x: float
    y: float
    z: float

    def distance_to(self, other: "Position") -> float:
        return ((self.x - other.x) ** 2
                + (self.y - other.y) ** 2
                + (self.z - other.z) ** 2) ** 0.5

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def from_dict(cls, d: dict) -> "Position":
        return cls(x=float(d["x"]), y=float(d["y"]), z=float(d["z"]))


class TaskStatus(str, Enum):
    """任务执行状态。"""
    PENDING   = "pending"    # 等待执行
    RUNNING   = "running"    # 执行中
    DONE      = "done"       # 成功完成
    FAILED    = "failed"     # 失败
    CANCELLED = "cancelled"  # 已取消


@dataclass
class TaskInstruction:
    """单条任务指令。"""
    action: ActionType
    target: Optional[Position] = None    # move_to 的目标位置
    duration_ms: int = 0                 # wait 的等待时长
    label: str = ""                      # 人类可读标签

    def to_dict(self) -> dict:
        d: dict = {"action": self.action.value}
        if self.target is not None:
            d["target"] = self.target.to_dict()
        if self.duration_ms:
            d["duration_ms"] = self.duration_ms
        if self.label:
            d["label"] = self.label
        return d


@dataclass
class SensorReading:
    """传感器读数。"""
    timestamp: float
    # 距离传感器（m）
    distance: float = 0.0
    # 力/扭矩传感器
    force: float = 0.0
    # 自定义键值对
    extra: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, float]:
        d = {"ts": self.timestamp, "dist": self.distance, "force": self.force}
        d.update(self.extra)
        return d


@dataclass
class TaskResult:
    """任务执行结果。"""
    task_id: int
    instruction: TaskInstruction
    status: TaskStatus
    start_time: float
    end_time: float
    position_start: Position
    position_end: Position
    error_message: str = ""
    sensor_before: Optional[SensorReading] = None
    sensor_after: Optional[SensorReading] = None

    @property
    def elapsed_ms(self) -> float:
        return (self.end_time - self.start_time) * 1000

    def to_dict(self) -> dict:
        d = {
            "task_id": self.task_id,
            "action": self.instruction.action.value,
            "label": self.instruction.label,
            "status": self.status.value,
            "elapsed_ms": round(self.elapsed_ms, 1),
            "pos_start": self.position_start.to_dict(),
            "pos_end": self.position_end.to_dict(),
        }
        if self.error_message:
            d["error"] = self.error_message
        if self.sensor_before:
            d["sensor_before"] = self.sensor_before.to_dict()
        if self.sensor_after:
            d["sensor_after"] = self.sensor_after.to_dict()
        return d


@dataclass
class TaskBatch:
    """一组任务指令。"""
    tasks: list[TaskInstruction]
    label: str = ""

    @classmethod
    def from_json(cls, data: dict) -> "TaskBatch":
        tasks = [TaskInstruction.from_dict(t) for t in data["tasks"]]
        return cls(tasks=tasks, label=data.get("label", ""))
