# -*- coding: utf-8 -*-
"""
regenerate_all.py — 用新提示词重新生成三形态
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import generator, forms

BEAST = "九尾狐"
NAME_EN = "Nine-Tailed Fox"

config = generator.load_config()
rec = forms.get_beast(BEAST)
appearance = rec.get("appearance", "a legendary mythical beast") if rec else "a legendary mythical beast"

assets_dir = os.path.join(HERE, "assets")

for FORM in forms.FORM_ORDER:
    print(f"\n重新生成 {BEAST} - {FORM} ...")
    path = generator.generate(BEAST, NAME_EN, FORM, appearance, config=config, assets_dir=assets_dir)
    if path:
        print(f"[OK] {path}")
    else:
        print(f"[失败] {FORM}")
