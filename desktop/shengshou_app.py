# -*- coding: utf-8 -*-
"""
shengshou_app.py — 桌面养圣兽（MVP 可养版）

透明置顶、可拖拽的桌面宠物：
  - 三形态切换（陪伴/出行/战斗），对应 SKILL.md 第七节
  - 左键点击 → 随机互动动作 + 好感/精力增长 + 气泡
  - 右键菜单 → 切形态 / 投喂 / 生成三形态图 / 查看状态 / 退出
  - 首次运行自动调用生图 API（若已配置 key）生成三形态图；否则用占位图
  - 状态存 ~/.config/shengshou/state.json

运行：
  python shengshou_app.py            # 用 config.json 默认神兽
  python shengshou_app.py --beast 白泽
"""

from __future__ import annotations

import argparse
import os
import math
import random
import sys
import time

import tkinter as tk
from tkinter import messagebox

try:
    from PIL import Image, ImageTk, ImageDraw
except ImportError:
    print("[错误] 缺少 Pillow，请先安装：pip install Pillow")
    sys.exit(1)

import forms
import state as state_mod
import generator

HERE = os.path.dirname(os.path.abspath(__file__))
TRANSPARENT = "magenta"  # 窗口透明色（图片外区域）

WIN_W, WIN_H = 240, 300
IMG_MAX_W = 200

FORM_COLORS = {
    "companion": (255, 192, 203),   # 马卡龙粉
    "travel": (70, 110, 180),       # 石青
    "battle": (120, 30, 40),        # 暗红
}


# --------------------------------------------------------------------------- #
# 占位图（无 API key 时使用，保证 app 立即可跑）
# --------------------------------------------------------------------------- #
def make_placeholder(beast: str, form: str, assets_dir: str) -> str:
    out_dir = os.path.join(assets_dir, generator._safe_name(beast))
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{form}.png")
    if os.path.exists(out):
        return out
    size = (IMG_MAX_W, int(IMG_MAX_W * 1.25))
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = FORM_COLORS.get(form, (200, 200, 200))
    cx, cy = size[0] // 2, size[1] // 2
    r = size[0] // 2 - 12
    # 身体椭圆
    d.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.9], fill=col + (255,))
    # 耳朵
    d.ellipse([cx - r, cy - r, cx - r // 2, cy - r // 2], fill=col + (255,))
    d.ellipse([cx + r // 2, cy - r, cx + r, cy - r // 2], fill=col + (255,))
    # 眼睛
    d.ellipse([cx - r // 2 - 6, cy - 6, cx - r // 2 + 6, cy + 6], fill=(255, 255, 255, 255))
    d.ellipse([cx + r // 2 - 6, cy - 6, cx + r // 2 + 6, cy + 6], fill=(255, 255, 255, 255))
    d.ellipse([cx - r // 2 - 2, cy - 2, cx - r // 2 + 2, cy + 2], fill=(20, 20, 20, 255))
    d.ellipse([cx + r // 2 - 2, cy - 2, cx + r // 2 + 2, cy + 2], fill=(20, 20, 20, 255))
    img.save(out)
    return out


# --------------------------------------------------------------------------- #
# 主程序
# --------------------------------------------------------------------------- #
class PetApp:
    def __init__(self, beast: str, name_en: str, assets_dir: str, config: dict):
        self.beast = beast
        self.name_en = name_en
        self.assets_dir = assets_dir
        self.config = config
        self.appearance = self._resolve_appearance()
        self.st = state_mod.ShengShouState.load()
        if not self.st.beast:
            self.st.beast = beast
            self.st.name_en = name_en
            self.st.save()
        # 同步当前展示形态
        self.current_form = self.st.current_form
        if self.current_form not in self.st.unlocked_forms:
            self.current_form = "companion"

        self.root = tk.Tk()
        self.root.title(f"圣兽·{beast}")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", TRANSPARENT)
        self.root.geometry(f"{WIN_W}x{WIN_H}+{(self.root.winfo_screenwidth() - WIN_W)//2}+200")
        self.root.configure(bg=TRANSPARENT)

        self.canvas = tk.Canvas(self.root, width=WIN_W, height=WIN_H,
                                bg=TRANSPARENT, highlightthickness=0)
        self.canvas.pack()

        # 拖拽
        self._dx = self._dy = 0
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_click)  # 点击（无拖动）触发互动
        self.canvas.bind("<Button-3>", self._on_right)

        self.photo = None
        self.base_img = None
        self.photo_cache = {}   # form -> PhotoImage (scale 1.0)
        self.pil_cache = {}     # form -> PIL.Image (用于脉冲缩放)
        self.pulse_photo = None
        self.bob_t = 0
        self.bubble_until = 0
        self.bubble_text = ""

        self._ensure_images()
        self._render(scale=1.0)
        self._idle_loop()
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.mainloop()

    # ---- 数据 ----
    def _resolve_appearance(self) -> str:
        rec = forms.get_beast(self.beast)
        if rec and rec.get("appearance_en"):
            return rec["appearance_en"]
        return "a legendary mythical beast from Chinese classical texts"

    def _ensure_images(self) -> None:
        for fm in forms.FORM_ORDER:
            self._cache_form(fm)

    def _get_image(self, form: str, action: str | None = None) -> str:
        safe = generator._safe_name(self.beast)
        path = os.path.join(self.assets_dir, safe, f"{form}.png")
        if os.path.exists(path):
            return path
        # 尝试生图
        p = generator.generate(self.beast, self.name_en, form, self.appearance,
                               action=action, config=self.config, assets_dir=self.assets_dir)
        if p:
            return p
        return make_placeholder(self.beast, form, self.assets_dir)

    def _cache_form(self, form: str) -> None:
        path = self._get_image(form)
        img = Image.open(path).convert("RGBA")
        w, h = img.size
        ratio = min(IMG_MAX_W / w, (WIN_H - 60) / h, 1.0)
        nw, nh = int(w * ratio), int(h * ratio)
        img = img.resize((nw, nh), Image.LANCZOS)
        self.pil_cache[form] = img
        self.photo_cache[form] = ImageTk.PhotoImage(img)

    # ---- 渲染 ----
    def _render(self, scale: float = 1.0):
        self.canvas.delete("all")
        img = self.pil_cache.get(self.current_form)
        if scale != 1.0 and img is not None:
            nw, nh = int(img.width * scale), int(img.height * scale)
            self.pulse_photo = ImageTk.PhotoImage(img.resize((nw, nh), Image.LANCZOS))
            photo = self.pulse_photo
        else:
            photo = self.photo_cache.get(self.current_form)
        self.photo = photo
        if photo is None:
            return
        bob = int(math.sin(self.bob_t) * 4)
        x = (WIN_W - photo.width()) // 2
        y = 40 + bob
        self.canvas.create_image(x, y, image=photo, anchor="nw")
        if time.time() < self.bubble_until and self.bubble_text:
            self._draw_bubble(self.bubble_text)

    def _draw_bubble(self, text: str):
        bx, by = WIN_W // 2, 14
        self.canvas.create_rectangle(bx - 70, by - 2, bx + 70, by + 24,
                                     fill="white", outline="#ccc", width=1)
        self.canvas.create_text(bx, by + 11, text=text, font=("Microsoft YaHei", 12), fill="#333")

    def _show_bubble(self, text: str, ms: int = 1500):
        self.bubble_text = text
        self.bubble_until = time.time() + ms / 1000
        self._render()

    # ---- 互动 ----
    def _play_action(self, action: str | None = None):
        actions = forms.action_names(self.current_form)
        act = action or random.choice(actions)
        res = self.st.interact(act)
        # 反应：短暂放大
        self._render(scale=1.08)
        self.root.after(160, lambda: self._render(scale=1.0))
        msg = act
        if res["leveled"]:
            msg = f"升级！Lv.{self.st.level}"
        elif res["unlocked"]:
            lbl = {"travel": "出行形态", "battle": "战斗形态"}[res["unlocked"][0]]
            msg = f"解锁{lbl}！"
        self._show_bubble(msg)
        self.current_form = self.st.current_form

    def _transform(self, target: str):
        ok, reason = self.st.transform(target)
        if ok:
            self.current_form = target
            self._render()
            self._show_bubble(forms.FORM_LABELS[target])
        else:
            self._show_bubble(reason, ms=2000)

    def _feed(self):
        res = self.st.interact("进食灵果")
        self._render(scale=1.08)
        self.root.after(160, lambda: self._render(scale=1.0))
        self._show_bubble("投喂灵果 +好感", ms=1500)

    def _regenerate(self):
        if not self.config.get("api", {}).get("api_key") or \
           self.config["api"]["api_key"].startswith("sk-xxx"):
            self._show_bubble("未配置 API key", ms=2000)
            return
        self._show_bubble("生成中…", ms=4000)
        for fm in forms.FORM_ORDER:
            generator.generate(self.beast, self.name_en, fm, self.appearance,
                               config=self.config, assets_dir=self.assets_dir)
        self._ensure_images()  # 重新缓存
        self._render()
        self._show_bubble("三形态已生成", ms=2000)

    # ---- 事件 ----
    def _on_press(self, e):
        self._dx = e.x
        self._dy = e.y
        self._drag_moved = False

    def _on_drag(self, e):
        self._drag_moved = True
        x = self.root.winfo_x() + e.x - self._dx
        y = self.root.winfo_y() + e.y - self._dy
        self.root.geometry(f"+{x}+{y}")

    def _on_click(self, e):
        if getattr(self, "_drag_moved", False):
            return
        self._play_action()

    def _on_right(self, e):
        m = tk.Menu(self.root, tearoff=0)
        m.add_command(label="📊 状态", command=lambda: messagebox.showinfo("圣兽状态", self.st.summary()))
        m.add_separator()
        for fm in forms.FORM_ORDER:
            lbl = forms.FORM_LABELS[fm]
            if fm in self.st.unlocked_forms:
                mark = "✓" if fm == self.current_form else "  "
                m.add_command(label=f"{mark} 切到{lbl}", command=lambda f=fm: self._transform(f))
            else:
                m.add_command(label=f"🔒 {lbl}（未解锁）", state="disabled")
        m.add_separator()
        m.add_command(label="🍎 投喂灵果", command=self._feed)
        m.add_command(label="🎨 生成三形态图", command=self._regenerate)
        m.add_separator()
        m.add_command(label="❌ 退出", command=self.quit)
        m.tk_popup(e.x_root, e.y_root)

    # ---- 循环 ----
    def _idle_loop(self):
        self.bob_t += 0.08
        # 偶发自动动作
        if random.random() < 0.004:
            self._play_action()
        else:
            self._render()
        self.root.after(50, self._idle_loop)

    def quit(self):
        self.st.save()
        self.root.destroy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--beast", default=None, help="神兽中文名，覆盖 config 默认")
    args = ap.parse_args()

    config = generator.load_config()
    beast = args.beast or config.get("default_beast", "九尾狐")
    name_en = config.get("default_name_en", beast)
    # 若 beasts.json 有英文外观，优先用记录里的英文名（如有）
    rec = forms.get_beast(beast)
    if rec:
        name_en = rec.get("name_en", name_en)
    assets_dir = os.path.join(HERE, config.get("assets_dir", "assets"))

    try:
        PetApp(beast, name_en, assets_dir, config)
    except tk.TclError as e:
        if "display" in str(e).lower() or "no display" in str(e).lower():
            print("当前环境无图形显示（headless），无法启动桌面窗口。请在 Windows 桌面环境运行。")
            sys.exit(0)
        raise


if __name__ == "__main__":
    main()
