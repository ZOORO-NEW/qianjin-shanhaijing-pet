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
BG_COLOR = "#0a0a0f"  # 纯深黑底（卡片同色，彻底杜绝绿边）

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
    d.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.9], fill=col + (255,))
    d.ellipse([cx - r, cy - r, cx - r // 2, cy - r // 2], fill=col + (255,))
    d.ellipse([cx + r // 2, cy - r, cx + r, cy - r // 2], fill=col + (255,))
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
        self.current_form = self.st.current_form
        if self.current_form not in self.st.unlocked_forms:
            self.current_form = "companion"

        self.root = tk.Tk()
        self.root.title(f"圣兽·{beast}")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.geometry(f"{WIN_W}x{WIN_H}+{(self.root.winfo_screenwidth() - WIN_W)//2}+200")
        self.root.configure(bg=BG_COLOR)

        self.canvas = tk.Canvas(self.root, width=WIN_W, height=WIN_H,
                                bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack()

        self._dx = self._dy = 0
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_click)
        self.canvas.bind("<Button-3>", self._on_right)

        self.photo = None
        self.photo_cache = {}   # key "form|kind|name" -> PhotoImage
        self.pil_cache = {}     # key "form|kind|name" -> PIL Image
        self.pulse_photo = None
        self.bob_t = 0
        self.bubble_until = 0
        self.bubble_text = ""
        self.display_key = None          # 当前应显示的图 key
        self.action_until = 0.0          # 动作图显示截止时间戳（期间 idle_loop 不抢切）
        self.last_emotion = None         # 上次情绪（变化才重生成待机图）

        self._ensure_images()
        self._refresh_idle()
        self._render(scale=1.0)
        self._idle_loop()
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.mainloop()

    def _resolve_appearance(self) -> str:
        rec = forms.get_beast(self.beast)
        if rec and rec.get("appearance_en"):
            return rec["appearance_en"]
        return "a legendary mythical beast from Chinese classical texts"

    def _ensure_images(self) -> None:
        """首次启动：生成三形态 × 当前情绪的待机图（动作/其他情绪懒加载）。"""
        emo = self.st.current_emotion()
        self.last_emotion = emo
        for fm in forms.FORM_ORDER:
            self._cache_image(fm, "idle", emo)

    def _get_image(self, form: str, kind: str = "idle", name: str | None = None) -> str:
        """返回某图的磁盘路径（优先命中缓存文件，否则生成）。

        kind="idle"   name=情绪名 -> 待机情绪图 {form}_{emotion}.png
        kind="action" name=动作名 -> 动作图     {form}_{action}.png
        """
        safe = generator._safe_name(self.beast)
        out_dir = os.path.join(self.assets_dir, safe)
        parts = [form]
        if kind == "action" and name:
            parts.append(generator._safe_name(name))
        elif kind == "idle" and name:
            parts.append(generator._safe_name(name))
        path = os.path.join(out_dir, "_".join(parts) + ".png")
        if os.path.exists(path):
            return path
        p = generator.generate(self.beast, self.name_en, form, self.appearance,
                               action=(name if kind == "action" else None),
                               emotion=(name if kind == "idle" else None),
                               config=self.config, assets_dir=self.assets_dir)
        if p:
            return p
        # 占位图只按 form 生成（无动作/情绪变体）
        return make_placeholder(self.beast, form, self.assets_dir)

    def _make_card(self, src: "Image.Image") -> "Image.Image":
        """时空之门 v11 —— 场景图轻融合。

        提示词已直接生成完整的"暗黑星空 + 发光时空门 + 神兽浮现"场景图，
        App 端不再自行绘制传送门，只做轻微边缘融合，避免与生成的场景冲突。
        """
        import random
        from PIL import ImageFilter

        W, H = WIN_W, WIN_H

        # ═══ 1. 深空背景（仅在场景图边缘露出一小部分）═══
        out = Image.new("RGBA", (W, H), (6, 8, 16, 255))
        od = ImageDraw.Draw(out)
        for y in range(H):
            ratio = y / H
            r = int(6 + ratio * 12)
            g = int(8 + ratio * 20)
            b = int(16 + ratio * 32)
            od.line([(0, y), (W, y)], fill=(r, g, b, 255))

        random.seed(42)
        for _ in range(35):
            sx = random.randint(0, W - 1)
            sy = random.randint(0, int(H * 0.65))
            br = random.randint(70, 200)
            out.putpixel((sx, sy), (br, br, min(255, br + 40), 255))

        # ═══ 2. 放置完整场景图（几乎填满窗口）═══
        src = src.convert("RGBA")
        iw, ih = src.size
        target_h = int(H * 0.90)     # 让场景几乎撑满窗口
        sc = target_h / ih
        nw = max(1, int(iw * sc))
        nh = max(1, int(ih * sc))
        fitted = src.resize((nw, nh), Image.LANCZOS)
        bx = (W - nw) // 2
        by = H - nh - 2              # 底部只留 2px
        by = max(0, by)
        out.paste(fitted, (bx, by), fitted)

        # ═══ 3. 轻微边缘压暗（让场景自然融入桌面）═══
        vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        vp = vig.load()
        for yy in range(H):
            for xx in range(W):
                ex = min(xx, W - 1 - xx)
                ey = min(yy, H - 1 - yy)
                ed = (ex * ex + ey * ey) ** 0.5
                if ed > 15:
                    vp[xx, yy] = (6, 8, 16, min(55, int((ed - 15) * 0.6)))
        out = Image.alpha_composite(out, vig)

        return out

    def _key(self, form: str, kind: str, name: str | None) -> str:
        return f"{form}|{kind}|{name}"

    def _cache_image(self, form: str, kind: str, name: str | None) -> None:
        """生成（命中则跳过）并缓存某张图到 pil_cache / photo_cache。"""
        key = self._key(form, kind, name)
        if key in self.pil_cache:
            return
        path = self._get_image(form, kind, name)
        img = Image.open(path).convert("RGBA")
        img = self._make_card(img)
        self.pil_cache[key] = img
        self.photo_cache[key] = ImageTk.PhotoImage(img)

    def _render(self, scale: float = 1.0):
        self.canvas.delete("all")
        key = self.display_key or self._key(self.current_form, "idle", self.last_emotion or "平静")
        img = self.pil_cache.get(key)
        if img is None:
            img = self.pil_cache.get(self._key(self.current_form, "idle", "平静"))
        if scale != 1.0 and img is not None:
            nw, nh = int(img.width * scale), int(img.height * scale)
            self.pulse_photo = ImageTk.PhotoImage(img.resize((nw, nh), Image.LANCZOS))
            photo = self.pulse_photo
        else:
            photo = self.photo_cache.get(key) or self.photo_cache.get(
                self._key(self.current_form, "idle", "平静"))
        self.photo = photo
        if photo is None:
            return
        bob = int(math.sin(self.bob_t) * 4)
        x = (WIN_W - photo.width()) // 2
        y = bob  # 卡片整窗实心，y 留 bob 微浮动即可，不再 +40
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

    def _play_action(self, action: str | None = None):
        actions = forms.action_names(self.current_form)
        act = action or random.choice(actions)
        res = self.st.interact(act)
        # 切到动作图（懒生成并缓存），1.8s 后回落待机
        self._cache_image(self.current_form, "action", act)
        self.display_key = self._key(self.current_form, "action", act)
        self.action_until = time.time() + 1.8
        self._render(scale=1.08)
        self.root.after(160, lambda: self._render(scale=1.0))
        self.root.after(1800, self._revert_idle)
        msg = act
        if res["leveled"]:
            msg = f"升级！Lv.{self.st.level}"
        elif res["unlocked"]:
            lbl = {"travel": "出行形态", "battle": "战斗形态"}[res["unlocked"][0]]
            msg = f"解锁{lbl}！"
        self._show_bubble(msg)
        self.current_form = self.st.current_form

    def _refresh_idle(self) -> None:
        """根据当前形态+情绪，刷新待机显示 key（情绪变化时懒生成新待机图）。"""
        emo = self.st.current_emotion()
        if emo != self.last_emotion:
            self.last_emotion = emo
            self._cache_image(self.current_form, "idle", emo)
        self.display_key = self._key(self.current_form, "idle", emo)

    def _revert_idle(self) -> None:
        """动作播放结束，回落到待机情绪图。"""
        self.action_until = 0.0
        self._refresh_idle()
        self._render()

    def _transform(self, target: str):
        ok, reason = self.st.transform(target)
        if ok:
            self.current_form = target
            self._refresh_idle()
            self._render()
            self._show_bubble(forms.FORM_LABELS[target])
        else:
            self._show_bubble(reason, ms=2000)

    def _feed(self):
        self.st.interact("进食灵果")
        self._cache_image(self.current_form, "action", "进食灵果")
        self.display_key = self._key(self.current_form, "action", "进食灵果")
        self.action_until = time.time() + 1.8
        self._render(scale=1.08)
        self.root.after(160, lambda: self._render(scale=1.0))
        self.root.after(1800, self._revert_idle)
        self._show_bubble("投喂灵果 +好感", ms=1500)

    def _regenerate(self):
        if not self.config.get("api", {}).get("api_key") or \
           self.config["api"]["api_key"].startswith("sk-xxx"):
            self._show_bubble("未配置 API key", ms=2000)
            return
        self._show_bubble("生成中（含动作/情绪图）…", ms=8000)
        emo = self.st.current_emotion()
        for fm in forms.FORM_ORDER:
            generator.generate(self.beast, self.name_en, fm, self.appearance,
                               emotion=emo, config=self.config, assets_dir=self.assets_dir)
            for act in forms.action_names(fm):
                generator.generate(self.beast, self.name_en, fm, self.appearance,
                                   action=act, config=self.config, assets_dir=self.assets_dir)
        # 清缓存，强制按新图重建
        self.pil_cache.clear()
        self.photo_cache.clear()
        self.last_emotion = None
        self._ensure_images()
        self._refresh_idle()
        self._render()
        self._show_bubble("三形态+动作/情绪图已生成", ms=2000)

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

    def _idle_loop(self):
        self.bob_t += 0.08
        now = time.time()
        if now < self.action_until:
            # 动作图展示中，不抢切
            self._render()
        else:
            emo = self.st.current_emotion()
            if emo != self.last_emotion:
                # 情绪变化：生成新待机图并切换
                self.last_emotion = emo
                self._cache_image(self.current_form, "idle", emo)
                self.display_key = self._key(self.current_form, "idle", emo)
                self._render()
            elif self.display_key != self._key(self.current_form, "idle", emo):
                # 形态已切换但 display_key 未更新（防御）
                self.display_key = self._key(self.current_form, "idle", emo)
                self._render()
            elif random.random() < 0.004:
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
