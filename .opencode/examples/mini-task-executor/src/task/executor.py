"""状态机任务执行器。

仿 magpie global_planner_node 的设计风格:
- 枚举驱动的状态机
- 单主循环分发
- deque 任务队列
- 配置驱动，无硬编码参数
"""
from __future__ import annotations

import logging
import threading
import time
from collections import deque
from enum import Enum
from typing import Optional

from ..hardware.interface import RobotHardware
from .schema import (
    ActionType,
    Position,
    SensorReading,
    TaskBatch,
    TaskInstruction,
    TaskResult,
    TaskStatus,
)

logger = logging.getLogger("task.executor")


class ExecutorState(Enum):
    """执行器状态。"""
    IDLE      = 0   # 空闲，等待任务
    MOVING    = 1   # 正在移动
    GRASPING  = 2   # 正在抓取
    RELEASING = 3   # 正在释放
    WAITING   = 4   # 等待中
    SENSING   = 5   # 读取传感器
    ERROR     = 6   # 错误状态
    STOPPED   = 7   # 已停止


class TaskExecutor:
    """任务执行器。

    仿 global_planner_node 架构：
    - 单 tick() 循环驱动状态机
    - 内置任务队列（deque）
    - 线程安全的状态管理

    Usage:
        config = load_config("config.yaml")
        hw = MockRobot(config["hardware"])
        executor = TaskExecutor(hw, config["executor"])
        executor.submit(batch)
        executor.run()              # 阻塞直到任务完成
    """

    def __init__(self, hardware: RobotHardware, config: dict):
        self._hw = hardware
        self._cfg = config

        # ── 状态机 ──
        self._state = ExecutorState.IDLE
        self._lock = threading.RLock()

        # ── 任务队列 ──
        self._queue: deque[TaskInstruction] = deque()
        self._max_queue = config.get("max_queue_size", 20)
        self._task_id_counter = 0
        self._current_task: Optional[TaskInstruction] = None

        # ── 当前步内部状态 ──
        self._move_target: Optional[Position] = None
        self._wait_end: float = 0.0
        self._retry_count: int = 0
        self._step_start_time: float = 0.0
        self._step_start_pos: Optional[Position] = None
        self._sensor_before: Optional[SensorReading] = None

        # ── 结果收集 ──
        self.results: list[TaskResult] = []

        # ── 控制 ──
        self._stop_flag = threading.Event()
        self._stop_flag.clear()

        self._tick_rate = config.get("tick_rate", 50)
        self._tick_interval = 1.0 / self._tick_rate
        self._max_retries = config.get("max_retries", 3)
        self._arrival_tol = config.get("arrival_tolerance", 0.005)

    # ═══════════════════════════════════════════════════════════════
    # 公共接口
    # ═══════════════════════════════════════════════════════════════

    def submit(self, batch: TaskBatch) -> int:
        """提交任务批次到执行队列。

        Returns:
            实际入队任务数
        """
        with self._lock:
            for task in batch.tasks:
                if len(self._queue) >= self._max_queue:
                    logger.warning(f"任务队列已满（{self._max_queue}），丢弃后续任务")
                    break
                self._queue.append(task)
            logger.info(
                f"已入队 {min(len(batch.tasks), self._max_queue)} 个任务"
                f"（{batch.label or '未命名'}）"
            )
            return min(len(batch.tasks), self._max_queue)

    def run(self) -> list[TaskResult]:
        """运行主循环，阻塞直到所有任务完成。

        Returns:
            所有任务的执行结果列表
        """
        logger.info("执行器启动")
        self._stop_flag.clear()

        try:
            while not self._stop_flag.is_set():
                self._tick()
                time.sleep(self._tick_interval)
        except KeyboardInterrupt:
            logger.info("收到中断信号，停止执行")
        finally:
            self._hw.disconnect()

        logger.info(f"执行器停止，共完成 {len(self.results)} 个任务")
        return self.results

    def stop(self):
        """停止执行器。"""
        self._stop_flag.set()

    @property
    def state(self) -> ExecutorState:
        return self._state

    # ═══════════════════════════════════════════════════════════════
    # 主循环
    # ═══════════════════════════════════════════════════════════════

    def _tick(self):
        """单步执行，仿 global_planner 的 _state_machine_loop。"""
        with self._lock:
            if self._state == ExecutorState.IDLE:
                self._step_idle()
            elif self._state == ExecutorState.MOVING:
                self._step_moving()
            elif self._state == ExecutorState.GRASPING:
                self._step_grasping()
            elif self._state == ExecutorState.RELEASING:
                self._step_releasing()
            elif self._state == ExecutorState.WAITING:
                self._step_waiting()
            elif self._state == ExecutorState.SENSING:
                self._step_sensing()
            elif self._state == ExecutorState.ERROR:
                self._step_error()

    # ═══════════════════════════════════════════════════════════════
    # 状态处理 — IDLE
    # ═══════════════════════════════════════════════════════════════

    def _step_idle(self):
        if not self._queue:
            self._stop_flag.set()
            return

        self._current_task = self._queue.popleft()
        self._task_id_counter += 1
        tid = self._task_id_counter
        action = self._current_task.action
        self._retry_count = 0
        self._step_start_time = time.time()
        self._step_start_pos = Position(**self._hw.get_position())
        self._sensor_before = self._read_sensor()

        logger.info(
            f"[任务 {tid}] {action.value}"
            + (f" → {self._current_task.target.to_dict()}"
               if self._current_task.target else "")
            + (f" ({self._current_task.label})"
               if self._current_task.label else "")
        )

        if action == ActionType.MOVE_TO:
            self._move_target = self._current_task.target
            self._set_state(ExecutorState.MOVING)
        elif action == ActionType.GRASP:
            self._set_state(ExecutorState.GRASPING)
        elif action == ActionType.RELEASE:
            self._set_state(ExecutorState.RELEASING)
        elif action == ActionType.WAIT:
            self._wait_end = time.time() + self._current_task.duration_ms / 1000.0
            self._set_state(ExecutorState.WAITING)
        elif action == ActionType.READ_SENSOR:
            self._set_state(ExecutorState.SENSING)
        else:
            self._complete_task(TaskStatus.FAILED,
                                f"未知动作: {action}")

    # ═══════════════════════════════════════════════════════════════
    # 状态处理 — MOVING
    # ═══════════════════════════════════════════════════════════════

    def _step_moving(self):
        assert self._move_target is not None
        target = self._move_target

        ok = self._hw.move_to(target.x, target.y, target.z)
        if not ok:
            self._retry_count += 1
            if self._retry_count >= self._max_retries:
                self._complete_task(TaskStatus.FAILED, "运动指令失败")
            return

        current = Position(**self._hw.get_position())
        if current.distance_to(target) < self._arrival_tol:
            self._complete_task(TaskStatus.DONE)

    # ═══════════════════════════════════════════════════════════════
    # 状态处理 — GRASPING
    # ═══════════════════════════════════════════════════════════════

    def _step_grasping(self):
        ok = self._hw.gripper_close()
        if not ok:
            self._retry_count += 1
            if self._retry_count >= self._max_retries:
                self._complete_task(TaskStatus.FAILED, "夹爪闭合失败")
            return
        self._complete_task(TaskStatus.DONE)

    # ═══════════════════════════════════════════════════════════════
    # 状态处理 — RELEASING
    # ═══════════════════════════════════════════════════════════════

    def _step_releasing(self):
        ok = self._hw.gripper_open()
        if not ok:
            self._retry_count += 1
            if self._retry_count >= self._max_retries:
                self._complete_task(TaskStatus.FAILED, "夹爪张开失败")
            return
        self._complete_task(TaskStatus.DONE)

    # ═══════════════════════════════════════════════════════════════
    # 状态处理 — WAITING
    # ═══════════════════════════════════════════════════════════════

    def _step_waiting(self):
        if time.time() >= self._wait_end:
            self._complete_task(TaskStatus.DONE)

    # ═══════════════════════════════════════════════════════════════
    # 状态处理 — SENSING
    # ═══════════════════════════════════════════════════════════════

    def _step_sensing(self):
        reading = self._read_sensor()
        logger.info(f"传感器读数: {reading.to_dict()}")
        self._complete_task(TaskStatus.DONE)

    # ═══════════════════════════════════════════════════════════════
    # 状态处理 — ERROR
    # ═══════════════════════════════════════════════════════════════

    def _step_error(self):
        logger.error("执行器处于错误状态，停止")
        self._stop_flag.set()

    # ═══════════════════════════════════════════════════════════════
    # 内部方法
    # ═══════════════════════════════════════════════════════════════

    def _set_state(self, new_state: ExecutorState):
        old = self._state
        self._state = new_state
        if old != new_state:
            logger.debug(f"状态切换: {old.name} → {new_state.name}")

    def _read_sensor(self) -> SensorReading:
        data = self._hw.read_sensor()
        return SensorReading(
            timestamp=time.time(),
            distance=data.get("dist", 0.0),
            force=data.get("force", 0.0),
            extra={k: v for k, v in data.items()
                   if k not in ("dist", "force")},
        )

    def _complete_task(self, status: TaskStatus, error: str = ""):
        assert self._current_task is not None
        end_time = time.time()
        end_pos = Position(**self._hw.get_position())
        sensor_after = self._read_sensor() if status != TaskStatus.FAILED else None

        result = TaskResult(
            task_id=self._task_id_counter,
            instruction=self._current_task,
            status=status,
            start_time=self._step_start_time,
            end_time=end_time,
            position_start=self._step_start_pos,  # type: ignore[arg-type]
            position_end=end_pos,
            error_message=error,
            sensor_before=self._sensor_before,
            sensor_after=sensor_after,
        )
        self.results.append(result)

        status_icon = "✓" if status == TaskStatus.DONE else "✗"
        logger.info(
            f"[任务 {self._task_id_counter}] {status_icon} "
            f"{self._current_task.action.value} — {status.value}"
            + (f" ({error})" if error else "")
            + f" [{result.elapsed_ms:.0f}ms]"
        )

        self._move_target = None
        self._current_task = None
        self._set_state(ExecutorState.IDLE)
