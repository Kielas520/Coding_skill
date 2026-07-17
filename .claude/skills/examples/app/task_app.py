"""演示 app 层：只组装，不写业务逻辑。

运行：
    python app/task_app.py                    # mock 模式
    python app/task_app.py --real 10.0.0.1    # 真设备
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# ── 组装：拿 interface，创建实现 ──
from src.robot.interface import Robot
from src.robot.test.mock import MockRobot

logger = logging.getLogger("task_app")


def load_config() -> dict:
    import yaml

    path = Path(__file__).parent.parent / "src" / "robot" / "config" / "defaults.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def parse_task(path: str) -> list[dict]:
    with open(path) as f:
        data = json.load(f)
    return data["tasks"]


def run_state_machine(robot: Robot, tasks: list[dict]) -> list[dict]:
    """简单的状态机执行。这是 app 层唯一的"业务"——编排顺序。"""
    results = []
    for i, task in enumerate(tasks):
        action = task["action"]
        ok = False

        if action == "move_to":
            t = task["target"]
            ok = robot.move_to(t["x"], t["y"], t["z"])
        elif action == "grasp":
            ok = robot.grasp()
        elif action == "release":
            ok = robot.release()
        elif action == "read_sensor":
            val = robot.read_sensor()
            ok = True
            task["sensor_value"] = val
        elif action == "wait":
            import time
            time.sleep(task.get("duration_ms", 500) / 1000)
            ok = True

        results.append({"index": i, "action": action, "ok": ok})
        logger.info(f"[{i}] {action} → {'OK' if ok else 'FAIL'}")
    return results


def main():
    parser = argparse.ArgumentParser(description="Mini 任务执行器")
    parser.add_argument("--task", "-t", default="demo_task.json")
    parser.add_argument("--real", type=str, metavar="IP", help="使用真实硬件")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[%(name)s] %(message)s")

    # ── 选择硬件 ──
    if args.real:
        from src.robot.core import RealRobot
        robot = RealRobot(args.real)
        logger.info(f"硬件模式: 真实 ({args.real})")
    else:
        robot = MockRobot()
        logger.info("硬件模式: Mock")

    robot.connect()
    tasks = parse_task(args.task)
    results = run_state_machine(robot, tasks)

    ok = sum(1 for r in results if r["ok"])
    print(f"\n{'='*40}\n结果: {ok}/{len(results)} 成功\n{'='*40}")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
