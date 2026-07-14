"""Mock 硬件实现。

仿真机器人：带传感器噪声、运动延迟、随机故障模拟。
无需任何硬件即可运行，用于开发和测试。
"""
from __future__ import annotations

import logging
import random
import time
from typing import Optional

from .interface import RobotHardware

logger = logging.getLogger("hardware.mock")


class MockRobot:
    """模拟机器人。

    使用方式（依赖注入）：
        config = load_config("config.yaml")
        hw = MockRobot(config["hardware"])
        executor = TaskExecutor(hw, ...)
        executor.run()

    切换真实硬件：
        hw = RealRobot(config["hardware"])  # 实现相同接口
    """

    def __init__(self, config: dict):
        self._cfg = config
        self._connected = False

        self._noise_level: float = config.get("noise_level", 0.01)
        self._move_time: float = config.get("move_time", 0.3)
        # 内部状态
        self._position: dict[str, float] = {"x": 0.0, "y": 0.0, "z": 0.0}
        self._gripper_closed: bool = False
        self._step_count: int = 0
        self._move_progress: float = 0.0  # 当前运动进度 0..1
        self._move_target: Optional[dict[str, float]] = None

        # 随机故障概率（可在配置中设置，默认 0 = 不故障）
        self._fail_prob: float = config.get("fail_prob", 0.0)

    def connect(self) -> bool:
        self._connected = True
        logger.info("Mock 硬件已连接")
        return True

    def disconnect(self) -> None:
        self._connected = False
        self._position = {"x": 0.0, "y": 0.0, "z": 0.0}
        logger.info("Mock 硬件已断开")

    def move_to(self, x: float, y: float, z: float) -> bool:
        if not self._connected:
            logger.error("硬件未连接")
            return False

        self._step_count += 1

        # 模拟随机故障
        if self._fail_prob > 0 and random.random() < self._fail_prob:
            logger.warning("Mock: 模拟随机运动故障")
            return False

        # 渐进式移动（每次 tick 靠近一步）
        self._move_target = {"x": x, "y": y, "z": z}
        self._move_progress = 0.0

        # 模拟一步到达（完整到达在 executor 轮询时实现）
        step = min(self._move_time, 0.1)  # 单步最大位移
        px, py, pz = self._position["x"], self._position["y"], self._position["z"]
        dx, dy, dz = x - px, y - py, z - pz
        dist = (dx * dx + dy * dy + dz * dz) ** 0.5

        if dist < step:
            ratio = 1.0
        else:
            ratio = step / dist

        self._position["x"] += dx * ratio + random.gauss(0, self._noise_level)
        self._position["y"] += dy * ratio + random.gauss(0, self._noise_level)
        self._position["z"] += dz * ratio + random.gauss(0, self._noise_level)

        return True

    def get_position(self) -> dict[str, float]:
        return dict(self._position)

    def gripper_close(self) -> bool:
        if not self._connected:
            return False
        self._gripper_closed = True
        logger.info("Mock: 夹爪闭合")
        return True

    def gripper_open(self) -> bool:
        if not self._connected:
            return False
        self._gripper_closed = False
        logger.info("Mock: 夹爪张开")
        return True

    def read_sensor(self) -> dict[str, float]:
        if not self._connected:
            return {"dist": 0.0, "force": 0.0}

        dist = 0.5 + random.gauss(0, self._noise_level * 2)
        force = 1.2 if self._gripper_closed else 0.0
        force += random.gauss(0, self._noise_level * 0.5)

        return {"dist": max(0.0, dist), "force": max(0.0, force)}

    def is_connected(self) -> bool:
        return self._connected

    def emergency_stop(self) -> None:
        self._move_target = None
        self._move_progress = 0.0
        logger.warning("Mock: 紧急停止")
