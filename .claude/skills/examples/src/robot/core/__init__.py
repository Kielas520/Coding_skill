"""真实硬件实现（占位，需要对接实际驱动）。"""
from __future__ import annotations

from ..interface import Robot


class RealRobot(Robot):
    """对接真实机械臂，需要安装对应 SDK。"""

    def __init__(self, ip: str):
        self.ip = ip
        self._connected = False

    def connect(self) -> None:
        print(f"[robot] 连接 {self.ip} ...")
        self._connected = True

    def move_to(self, x: float, y: float, z: float) -> bool:
        print(f"[robot] MoveP → ({x:.3f}, {y:.3f}, {z:.3f})")
        return True

    def grasp(self) -> bool:
        print("[robot] 闭爪")
        return True

    def release(self) -> bool:
        print("[robot] 开爪")
        return True

    def read_sensor(self) -> float:
        return 0.0

    def disconnect(self) -> None:
        self._connected = False
