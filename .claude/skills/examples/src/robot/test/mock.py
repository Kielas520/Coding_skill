"""Mock 实现 — 无硬件离线测试。"""
from __future__ import annotations

import random
import time

from ..interface import Robot


class MockRobot(Robot):
    """模拟机械臂，带噪声和延迟。"""

    def __init__(self):
        self.position = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.gripping = False

    def connect(self) -> None:
        print("[mock] 已连接（无硬件）")

    def move_to(self, x: float, y: float, z: float) -> bool:
        time.sleep(0.05)  # 模拟运动时间
        self.position = {"x": x + random.uniform(-0.001, 0.001),
                         "y": y + random.uniform(-0.001, 0.001),
                         "z": z + random.uniform(-0.001, 0.001)}
        return True

    def grasp(self) -> bool:
        self.gripping = True
        return True

    def release(self) -> bool:
        self.gripping = False
        return True

    def read_sensor(self) -> float:
        return random.uniform(20.0, 25.0)  # 模拟温度传感器

    def disconnect(self) -> None:
        pass
