#!/usr/bin/env bash
# 桌面快捷方式入口：同步文档并推送，结束后等待按键，方便查看输出。
cd "$(dirname "$(readlink -f "$0")")/.." || exit 1
python3 scripts/sync_docs.py "$@"
status=$?
echo
if [ "$status" -eq 0 ]; then
  echo "同步完成。"
else
  echo "同步失败（退出码 $status），请查看上方日志。"
fi
read -n 1 -s -r -p "按任意键关闭..."
