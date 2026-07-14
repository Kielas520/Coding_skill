"""硬件抽象接口。

定义所有硬件操作的协议。真实硬件和 Mock 实现都遵循此接口。
仿 magpie 风格：每个方法都有明确的输入输出类型注解。
"""
from __future__ import annotations

from typing import Any, Protocol


class RobotHardware(Protocol):
    """机器人硬件抽象接口。

    所有硬件实现（Mock / 真实）必须实现此协议。
    调用方只需依赖此接口，无需关心底层是模拟还是真实设备。
    """

    def connect(self) -> bool:
        """建立硬件连接。

        Returns:
            True 连接成功，False 失败
        """
        ...

    def disconnect(self) -> None:
        """断开硬件连接，释放资源。"""
        ...

    def move_to(self, x: float, y: float, z: float) -> bool:
        """移动到目标位置（绝对坐标）。

        Args:
            x, y, z: 目标位置（单位：m）

        Returns:
            True 指令发送成功，False 失败
        """
        ...

    def get_position(self) -> dict[str, float]:
        """获取当前末端位置。

        Returns:
            {"x": float, "y": float, "z": float}
        """
        ...

    def gripper_close(self) -> bool:
        """闭合夹爪。

        Returns:
            True 指令发送成功，False 失败
        """
        ...

    def gripper_open(self) -> bool:
        """张开夹爪。

        Returns:
            True 指令发送成功，False 失败
        """
        ...

    def read_sensor(self) -> dict[str, float]:
        """读取传感器数据。

        Returns:
            {"dist": 距离(m), "force": 力(N), ...}
        """
        ...

    def is_connected(self) -> bool:
        """检查硬件连接状态。"""
        ...

    def emergency_stop(self) -> None:
        """紧急停止。"""
        ...
