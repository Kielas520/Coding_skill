"""状态机执行器测试。

验证各状态转换和完整流程。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.task.parser import parse_json_string
from src.task.schema import ActionType, TaskStatus
from src.hardware.mock import MockRobot
from src.task.executor import TaskExecutor


def test_executor_basic_flow():
    """完整抓取放置流程测试（Mock 模式）。"""
    config = {
        "tick_rate": 100,
        "max_retries": 3,
        "arrival_tolerance": 0.02,
        "max_queue_size": 20,
    }
    hw_config = {"noise_level": 0.001, "move_time": 0.05}
    hw = MockRobot(hw_config)
    hw.connect()

    executor = TaskExecutor(hw, config)
    batch = parse_json_string("""{
        "label": "测试流程",
        "tasks": [
            {"action": "move_to", "target": {"x": 0.1, "y": 0.0, "z": 0.0}},
            {"action": "grasp"},
            {"action": "move_to", "target": {"x": 0.2, "y": 0.0, "z": 0.0}},
            {"action": "release"},
            {"action": "read_sensor"}
        ]
    }""")
    executor.submit(batch)
    results = executor.run()

    # 验证结果
    assert len(results) == 5, f"预期 5 个结果，实际 {len(results)}"
    for r in results:
        assert r.status == TaskStatus.DONE, f"任务 {r.task_id} 应成功，实际: {r.status}"

    # 验证动作顺序
    expected_actions = [
        ActionType.MOVE_TO, ActionType.GRASP, ActionType.MOVE_TO,
        ActionType.RELEASE, ActionType.READ_SENSOR,
    ]
    for r, expected in zip(results, expected_actions):
        assert r.instruction.action == expected

    # 验证位置
    last_pos = results[-1].position_end
    # 最终位置应接近 (0.2, 0.0, 0.0) 带噪声
    assert abs(last_pos.x - 0.2) < 0.05

    print("✓ test_executor_basic_flow 通过")


def test_executor_empty_queue():
    """空队列应立即停止。"""
    hw = MockRobot({"noise_level": 0.0, "move_time": 0.01})
    hw.connect()
    executor = TaskExecutor(hw, {"tick_rate": 100})
    results = executor.run()
    assert len(results) == 0
    print("✓ test_executor_empty_queue 通过")


def test_executor_state_transitions():
    """验证状态机从 IDLE 出发的各状态转换。"""
    hw = MockRobot({"noise_level": 0.0, "move_time": 0.01})
    hw.connect()
    executor = TaskExecutor(hw, {"tick_rate": 100, "arrival_tolerance": 0.02})

    from src.task.executor import ExecutorState
    assert executor.state == ExecutorState.IDLE

    batch = parse_json_string("""{
        "tasks": [{"action": "wait", "duration_ms": 50}]
    }""")
    executor.submit(batch)
    # 运行 5 个 tick 后应完成
    executor.run()
    results = executor.run()  # 第二次 run 会立即停止

    assert executor.state == ExecutorState.IDLE
    print("✓ test_executor_state_transitions 通过")


if __name__ == "__main__":
    test_executor_basic_flow()
    test_executor_empty_queue()
    test_executor_state_transitions()
    print("\n全部测试通过 ✓")
