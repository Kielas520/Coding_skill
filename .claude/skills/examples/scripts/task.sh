#!/usr/bin/env bash
# 任务执行器 — 一键参数化启动
set -euo pipefail
cd "$(dirname "$0")/.."
exec python app/task_app.py "$@"
