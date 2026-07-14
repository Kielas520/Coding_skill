"""进程监听示例。

演示 test-helper 的方式 2：监听主进程运行，验证其行为。

运行方式：
    python tests/monitor.py
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


def monitor_executor(task_file: str, timeout: float = 30.0) -> bool:
    """监听任务执行器进程，验证其行为。"""
    project_root = Path(__file__).resolve().parent.parent
    src_dir = str(project_root / "src")
    task_path = str(project_root / task_file)

    env = {**__import__("os").environ, "PYTHONPATH": src_dir}

    proc = subprocess.Popen(
        [sys.executable, "-m", "src.main", "--task", task_path, "--mock"],
        cwd=str(project_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )

    start = time.time()
    success_count = 0
    fail_count = 0

    try:
        for line in proc.stdout:
            elapsed = time.time() - start
            print(f"[{elapsed:6.1f}s] {line.rstrip()}")

            if "done" in line.lower():
                success_count += 1
            if "failed" in line.lower():
                fail_count += 1

            if elapsed > timeout:
                print(f"超时 ({timeout}s)，终止进程")
                proc.terminate()
                proc.wait()
                return False

        proc.wait(timeout=5)
        returncode = proc.returncode

    except KeyboardInterrupt:
        print("\n收到中断信号")
        proc.terminate()
        proc.wait()
        return False

    print(f"\n监听结果: 成功={success_count}, 失败={fail_count}, "
          f"返回码={returncode}")
    return returncode == 0 and success_count > 0


if __name__ == "__main__":
    ok = monitor_executor("demo_task.json", timeout=30.0)
    if ok:
        print("✓ 进程执行正常")
    else:
        print("✗ 进程执行异常")
        sys.exit(1)
