# -*- coding: utf-8 -*-
"""预览完整版效果：每形态生成 1 张情绪待机图(平静) + 1 张代表动作图，拼成大图。
生成的图直接落盘到 assets/<beast>/，等于为桌宠预生成了一部分图。"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = r"C:\Users\ZQJ\.workbuddy\skills\qianjin-shanhaijing-pet\desktop"
sys.path.insert(0, HERE)

import forms
import generator
import shengshou_app as app

BEAST = "九尾狐"
rec = forms.get_beast(BEAST)
APPEARANCE = rec.get("appearance_en") or rec.get("appearance", "")
NAME_EN = rec.get("name_en", "Nine-Tailed Fox")
ASSETS = os.path.join(HERE, "assets")
CFG = generator.load_config()

OUT_DIR = os.path.join(ASSETS, generator._safe_name(BEAST))
os.makedirs(OUT_DIR, exist_ok=True)


def load_font(size):
    for f in ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/msyhbd.ttc",
              "C:/Windows/Fonts/simhei.ttf"]:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()


def render_card(src_path):
    img = Image.open(src_path).convert("RGBA")
    return app.PetApp._make_card(None, img)


# (form, 待机情绪, 代表动作)
PLAN = [
    ("companion", "平静", "蹦跳玩耍"),
    ("travel", "平静", "御云巡游"),
    ("battle", "平静", "蓄力大招"),
]

cells = []  # (形态标签, 子标签, PIL)
for fm, emo, act in PLAN:
    p_idle = generator.generate(BEAST, NAME_EN, fm, APPEARANCE,
                                emotion=emo, config=CFG, assets_dir=ASSETS)
    if not p_idle:
        p_idle = app.make_placeholder(BEAST, fm, ASSETS)
    cells.append((forms.FORM_LABELS[fm], f"待机·{emo}", render_card(p_idle)))

    p_act = generator.generate(BEAST, NAME_EN, fm, APPEARANCE,
                               action=act, config=CFG, assets_dir=ASSETS)
    if not p_act:
        p_act = app.make_placeholder(BEAST, fm, ASSETS)
    cells.append((forms.FORM_LABELS[fm], f"动作·{act}", render_card(p_act)))

# 拼图 3 行 × 2 列（列0=待机，列1=动作）
PAD = 16
LABEL_H = 22
CW, CH = app.WIN_W, app.WIN_H
COLS, ROWS = 2, 3
W = COLS * CW + (COLS + 1) * PAD
H = ROWS * (CH + LABEL_H) + (ROWS + 1) * PAD
canvas = Image.new("RGBA", (W, H), (20, 20, 28, 255))
d = ImageDraw.Draw(canvas)
fnt = load_font(14)
for idx, (fl, sl, img) in enumerate(cells):
    r, c = divmod(idx, COLS)
    x = PAD + c * (CW + PAD)
    y = PAD + r * (CH + LABEL_H + PAD)
    canvas.paste(img, (x, y), img)
    d.text((x + 4, y + CH + 4), f"{fl} · {sl}", font=fnt, fill=(220, 225, 235, 255))

OUT = os.path.join(OUT_DIR, "preview_full_v11.png")
canvas.save(OUT)
print("预览图已保存:", OUT)
print("已落盘图:", sorted(os.listdir(OUT_DIR)))
