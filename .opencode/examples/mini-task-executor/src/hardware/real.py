"""真实硬件实现（占位）。

接口与 MockRobot 完全一致，替换时只需改 main.py 中的 import。
"""
from __future__ import annotations

import logging

from .interface import RobotHardware

logger = logging.getLogger("hardware.real")


class RealRobot:
    """真实硬件控制。

    注意：这是占位实现。实际使用时需根据你的硬件协议
    （串口/CAN/EtherCAT 等）填充具体逻辑。
    """

    def __init__(self, config: dict):
        self._cfg = config
        self._connected = False

    def connect(self) -> bool:
        logger.info("真实硬件连接中...")
        logger.warning("RealRobot 为占位实现，请根据实际硬件协议填充")
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False
        logger.info("真实硬件已断开")

    def move_to(self, x: float, y: float, z: float) -> bool:
        if not self._connected:
            return False
        # TODO: 发送运动指令到真实硬件
        raise NotImplementedError("RealRobot.move_to 未实现")

    def get_position(self) -> dict[str, float]:
        # TODO: 从真实硬件读取位置
        raise NotImplementedError("RealRobot.get_position 未实现")

    def gripper_close(self) -> bool:
        # TODO: 发送夹爪闭合指令
        raise NotImplementedError("RealRobot.gripper_close 未实现")

    def gripper_open(self) -> bool:
        # TODO: 发送夹爪张开指令
        raise NotImplementedError("RealRobot.gripper_open 未实现")

    def read_sensor(self) -> dict[str, float]:
        # TODO: 从真实传感器读取数据
        raise NotImplementedError("RealRobot.read_sensor 未实现")

    def is_connected(self) -> bool:
        return self._connected

    def emergency_stop(self) -> None:
        # TODO: 发送急停指令
        logger.warning("真实硬件紧急停止")
