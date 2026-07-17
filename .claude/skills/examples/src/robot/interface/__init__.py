"""robot 包的对外接口。只定义 Protocol，不实现。"""
from __future__ import annotations

from typing import Protocol


class Robot(Protocol):
    """机械臂抽象接口。core 只依赖这个 Protocol，不知道硬件实现。"""

    def connect(self) -> None:
        ...

    def move_to(self, x: float, y: float, z: float) -> bool:
        ...

    def grasp(self) -> bool:
        ...

    def release(self) -> bool:
        ...

    def read_sensor(self) -> float:
        ...

    def disconnect(self) -> None:
        ...
