# -*- coding: utf-8 -*-
"""
preview_all.py — 用 shengshou_app.py 里真实的 _make_card 渲染三形态，
拼成一张预览图，便于在无 GUI 环境下查看实际效果。
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import shengshou_app as app

BEAST = "九尾狐"
ASSET_DIR = os.path.join(HERE, "assets", BEAST)
OUT = os.path.join(ASSET_DIR, "preview_all_v9.png")

forms = ["companion", "travel", "battle"]
labels = {"companion": "陪伴", "travel": "出行", "battle": "战斗"}

W, H = app.WIN_W, app.WIN_H
pad = 16
gap = 12
label_h = 24

# 加载中文字体（用于标签）
_font = None
for fp in [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\simsun.ttc",
]:
    if os.path.exists(fp):
        try:
            _font = ImageFont.truetype(fp, 14)
            break
        except Exception:
            pass
if _font is None:
    _font = ImageFont.load_default()

# 渲染每张
cards = []
for fm in forms:
    p = os.path.join(ASSET_DIR, f"{fm}.png")
    if not os.path.exists(p):
        print(f"[跳过] 找不到 {p}")
        continue
    src = Image.open(p).convert("RGBA")
    # 直接调用未绑定的方法（无需 tk 实例）
    card = app.PetApp._make_card(None, src)
    cards.append((fm, card))

if not cards:
    print("[错误] 没有任何形态图可渲染")
    sys.exit(1)

# 拼接触觉表
total_w = pad * 2 + len(cards) * W + (len(cards) - 1) * gap
total_h = pad * 2 + H + label_h
sheet = Image.new("RGBA", (total_w, total_h), (20, 20, 28, 255))
d = ImageDraw.Draw(sheet)

for i, (fm, card) in enumerate(cards):
    x = pad + i * (W + gap)
    y = pad
    sheet.paste(card, (x, y), card)
    # 标签
    txt = labels[fm]
    bbox = d.textbbox((0, 0), txt, font=_font)
    tw = bbox[2] - bbox[0]
    d.text((x + W // 2 - tw // 2, y + H + 4), txt,
           fill=(200, 210, 230, 255), font=_font)

sheet.convert("RGB").save(OUT)
print(f"[OK] 已保存预览: {OUT}")
print(f"     尺寸: {total_w}x{total_h}, 形态: {[c[0] for c in cards]}")
