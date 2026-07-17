"""进程监听测试：启动 app，验证 stdout 输出。"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_app_runs():
    proc = subprocess.Popen(
        [sys.executable, "app/task_app.py"],
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = proc.communicate(timeout=10)
    assert proc.returncode == 0, f"exit={proc.returncode}\n{stderr}"
    assert "结果:" in stdout, f"输出异常:\n{stdout}"
    print("✓ test_app_runs 通过")


if __name__ == "__main__":
    test_app_runs()
    print("\n全部测试通过 ✓")
