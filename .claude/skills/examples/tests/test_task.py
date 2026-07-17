"""端到端测试：mock 模式下跑完整任务。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.robot.test.mock import MockRobot
from app.task_app import parse_task, run_state_machine


def test_all_actions_ok():
    robot = MockRobot()
    robot.connect()
    tasks = parse_task(str(ROOT / "demo_task.json"))
    results = run_state_machine(robot, tasks)
    assert all(r["ok"] for r in results), f"有任务失败: {results}"
    print("✓ test_all_actions_ok 通过")


def test_empty_tasks():
    robot = MockRobot()
    results = run_state_machine(robot, [])
    assert len(results) == 0
    print("✓ test_empty_tasks 通过")


if __name__ == "__main__":
    test_all_actions_ok()
    test_empty_tasks()
    print("\n全部测试通过 ✓")
