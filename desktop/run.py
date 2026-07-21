# -*- coding: utf-8 -*-
"""
run.py — 桌面养圣兽 启动入口

用法：
  python run.py                 # 用 config.json 默认神兽
  python run.py --beast 白泽     # 指定神兽

依赖：pip install Pillow requests
首次运行把 config.example.json 复制为 config.json 并填写 api_key 即可自动生图；
不填也能跑（使用内置占位图）。
"""

import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "config.json")
EXAMPLE = os.path.join(HERE, "config.example.json")


def main():
    if not os.path.exists(CONFIG):
        shutil.copy(EXAMPLE, CONFIG)
        print("[提示] 已生成 config.json（从 config.example.json）。")
        print("        如需自动生成三形态图，请编辑 config.json 填入 api_key；")
        print("        不填也能直接运行（将使用占位图）。")

    # 依赖检查
    try:
        import PIL  # noqa
        import requests  # noqa
    except ImportError:
        print("[安装依赖] Pillow / requests 缺失，正在尝试安装…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "requests"])

    # 启动主程序
    from shengshou_app import main as app_main
    app_main()


if __name__ == "__main__":
    main()
