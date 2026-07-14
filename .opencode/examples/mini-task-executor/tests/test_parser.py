"""任务解析器测试。

演示 test-helper 的方式 1：纯 Python 测试脚本。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from task.parser import ParseError, parse_json_file, parse_json_string
from task.schema import ActionType, TaskStatus


def test_parse_valid_task():
    """解析合法 JSON。"""
    json_str = json.dumps({
        "tasks": [
            {"action": "move_to", "target": {"x": 0.1, "y": 0.2, "z": 0.3}},
            {"action": "grasp", "label": "抓"},
        ]
    })
    batch = parse_json_string(json_str)
    assert len(batch.tasks) == 2
    assert batch.tasks[0].action == ActionType.MOVE_TO
    assert batch.tasks[0].target.x == 0.1
    assert batch.tasks[1].action == ActionType.GRASP
    assert batch.tasks[1].label == "抓"
    print("✓ test_parse_valid_task 通过")


def test_missing_tasks_field():
    """缺少 tasks 字段应报错。"""
    try:
        parse_json_string(json.dumps({"label": "test"}))
        assert False, "应抛出 ParseError"
    except ParseError as e:
        assert "tasks" in str(e)
    print("✓ test_missing_tasks_field 通过")


def test_invalid_action():
    """非法动作类型应报错。"""
    try:
        parse_json_string(json.dumps({
            "tasks": [{"action": "fly"}]
        }))
        assert False, "应抛出 ParseError"
    except ParseError as e:
        assert "未知动作类型" in str(e)
    print("✓ test_invalid_action 通过")


def test_parse_demo_task_file():
    """解析 demo_task.json 文件。"""
    demo_path = Path(__file__).resolve().parent.parent / "demo_task.json"
    batch = parse_json_file(str(demo_path))
    assert len(batch.tasks) == 10
    assert batch.tasks[0].action == ActionType.MOVE_TO
    assert batch.tasks[2].action == ActionType.GRASP
    assert batch.tasks[6].action == ActionType.RELEASE
    print("✓ test_parse_demo_task_file 通过")


def test_task_status_values():
    """验证 TaskStatus 枚举值。"""
    assert TaskStatus.PENDING.value == "pending"
    assert TaskStatus.RUNNING.value == "running"
    assert TaskStatus.DONE.value == "done"
    assert TaskStatus.FAILED.value == "failed"
    print("✓ test_task_status_values 通过")


def test_position_distance():
    """验证位置距离计算。"""
    from task.schema import Position
    a = Position(0, 0, 0)
    b = Position(3, 4, 12)  # 3-4-5 三角形 → 距离 13
    assert abs(a.distance_to(b) - 13.0) < 0.001
    print("✓ test_position_distance 通过")


if __name__ == "__main__":
    test_parse_valid_task()
    test_missing_tasks_field()
    test_invalid_action()
    test_parse_demo_task_file()
    test_task_status_values()
    test_position_distance()
    print("\n全部测试通过 ✓")
