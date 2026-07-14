"""入口程序。

演示完整管线：加载配置 → 创建硬件 → 解析任务 → 状态机执行 → 输出结果。

运行方式：
    python -m src.main --task demo_task.json
    python -m src.main --task demo_task.json --mock   # 强制模拟模式
    python -m src.main --task demo_task.json --real   # 强制真实模式（用户确认）
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .config.loader import load_config
from .hardware.mock import MockRobot
from .hardware.real import RealRobot
from .task.executor import TaskExecutor
from .task.parser import ParseError, parse_json_file

logger = logging.getLogger("main")


def setup_logging(config: dict):
    log_cfg = config.get("logging", {})
    level = getattr(logging, log_cfg.get("level", "INFO").upper(), logging.INFO)
    fmt = log_cfg.get("format",
                       "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
    logging.basicConfig(level=level, format=fmt, datefmt="%H:%M:%S")


def main():
    parser = argparse.ArgumentParser(description="Mini 任务执行器示例")
    parser.add_argument(
        "--config", "-c",
        default="",
        help="配置 YAML 文件路径（默认使用内置 defaults.yaml）",
    )
    parser.add_argument(
        "--task", "-t",
        required=True,
        help="任务 JSON 文件路径",
    )
    parser.add_argument(
        "--mock", action="store_true",
        help="强制使用 Mock 硬件",
    )
    parser.add_argument(
        "--real", action="store_true",
        help="强制使用真实硬件（需要确认）",
    )
    args = parser.parse_args()

    # ── 加载配置 ──
    if args.config:
        config = load_config(args.config)
    else:
        defaults_path = Path(__file__).parent / "config" / "defaults.yaml"
        config = load_config(str(defaults_path))

    setup_logging(config)

    # ── 解析任务 ──
    try:
        batch = parse_json_file(args.task)
    except ParseError as e:
        logger.error(f"任务解析失败: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error(f"文件不存在: {e}")
        sys.exit(1)

    logger.info(
        f"任务批次: {batch.label or '未命名'} "
        f"({len(batch.tasks)} 个任务)"
    )

    # ── 创建硬件 ──
    use_mock = config["hardware"].get("mock", True)
    if args.mock:
        use_mock = True
    if args.real:
        use_mock = False
        if input("确认使用真实硬件？(y/N): ").strip().lower() != "y":
            logger.info("用户取消，改用 Mock 模式")
            use_mock = True

    if use_mock:
        logger.info("硬件模式: Mock（仿真）")
        hw = MockRobot(config["hardware"])
    else:
        logger.info("硬件模式: 真实")
        hw = RealRobot(config["hardware"])

    hw.connect()
    if not hw.is_connected():
        logger.error("硬件连接失败")
        sys.exit(1)

    # ── 创建执行器 ──
    executor = TaskExecutor(hw, config.get("executor", {}))
    executor.submit(batch)

    # ── 运行 ──
    results = executor.run()

    # ── 输出结果 ──
    print("\n" + "=" * 60)
    print("执行结果")
    print("=" * 60)
    for r in results:
        status = "✓" if r.status.value == "done" else "✗"
        print(f"  {status} [{r.task_id}] {r.instruction.action.value}"
              + (f" → {r.instruction.target.to_dict()}"
                 if r.instruction.target else "")
              + f" [{r.elapsed_ms:.0f}ms]"
              + (f" | 错误: {r.error_message}" if r.error_message else ""))
    print("=" * 60)
    print(f"成功: {sum(1 for r in results if r.status.value == 'done')}"
          f" / 失败: {sum(1 for r in results if r.status.value == 'failed')}"
          f" / 总计: {len(results)}")


if __name__ == "__main__":
    main()
