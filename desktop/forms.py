# -*- coding: utf-8 -*-
"""
forms.py — 神兽三形态提示词构建（供桌面养圣兽 app / 文生图 API 使用）

三形态与 qianjin-shanhaijing-pet SKILL.md 第七节一一对应：
  companion = 幼兽陪伴形态 (Q版萌宠版)
  travel    = 出行形态     (国风水墨版 / 3D 国风数字雕塑)
  battle    = 战斗形态     (暗黑史诗版 / 3D 游戏模型)

关键差异（相对 SKILL.md 第三节的 MJ 模板）：
  - 这里输出的提示词是「纯净 API 格式」——去掉 --ar/--v/--s/--niji/--style 等
    Midjourney 专用参数，因为运行时调的是 OpenAI 兼容文生图 API，不认这些参数。
  - 仍保留全局强制约束：3D 立体 / 完整全身 / 纯色或透明抠图背景。
"""

from __future__ import annotations

import json
import os

# ---------------------------------------------------------------------------
# 技能根目录（desktop/ 的上一级）
# ---------------------------------------------------------------------------
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BEASTS_JSON = os.path.join(SKILL_ROOT, "references", "beasts.json")

# 形态顺序（切换循环：companion <-> travel <-> battle）
FORM_ORDER = ["companion", "travel", "battle"]

FORM_LABELS = {
    "companion": "幼兽陪伴形态",
    "travel": "出行形态",
    "battle": "战斗形态",
}

# 各形态的纯净 API 基础提示词（已填入 {name} / {appearance} 占位）
# 注意：不含任何 MJ 参数
FORM_BASE = {
    "companion": (
        "3D chibi blind-box figure of {name}, {appearance} transformed into a cute companion: "
        "oversized head, tiny body, huge sparkly eyes, round fluffy shapes, pastel macaron colors, "
        "vinyl toy texture, adorable expression, full body, complete character, "
        "solid color background or transparent background, isolated subject, easy to cutout, soft lighting"
    ),
    "travel": (
        "3D render of a Chinese mythological beast {name}, {appearance}, ink-wash and gongbi inspired, "
        "mineral pigment colors, traditional cloud and wave patterns, volumetric sculpted form, "
        "elegant and dignified, museum collectible digital figurine, full body, complete character, "
        "solid color background, isolated subject, easy to cutout, highly detailed"
    ),
    "battle": (
        "3D dark fantasy epic creature {name}, {appearance}, ominous and majestic, gothic mythological beast, "
        "deep shadows, eerie glow, intricate dark details, dramatic chiaroscuro lighting, menacing aura, "
        "hyper-detailed, volumetric sculpted form, full body, complete character, "
        "solid color background or transparent background, isolated subject, easy to cutout, cinematic dark fantasy art"
    ),
}

# 各形态推荐的生图尺寸（适配 DALL·E 3 / gpt-image-1 等 API）
FORM_SIZE = {
    "companion": "1024x1024",
    "travel": "1024x1792",
    "battle": "1024x1792",
}

# 每形态 5 个互动动作的「提示词追加关键词」（对应 SKILL.md 7.3）
FORM_ACTIONS = {
    "companion": {
        "蹭蹭撒娇": "nuzzling the screen edge, squinting eyes, affectionate",
        "进食灵果": "holding and nibbling a glowing spirit fruit, puffy cheeks, happy",
        "蜷睡": "curled up sleeping, gentle breathing, peaceful",
        "蹦跳玩耍": "bouncing and chasing its tail, playful, joyful",
        "进化闪光": "glowing with evolution light, hinting transformation",
    },
    "travel": {
        "御云巡游": "riding a cloud, gliding gracefully",
        "探灵扫描": "scanning with swirling spiritual aura",
        "云梢小憩": "resting on a cloud, serene",
        "显形展姿": "striking a dignified pose, traditional ripple effect",
        "引路指津": "pointing toward a direction with tail, guiding",
    },
    "battle": {
        "本命神通": "unleashing its signature elemental power, dynamic",
        "结界防御": "raising a dark barrier shield, defensive",
        "蓄力大招": "charging an ultimate move, intense glow",
        "威压咆哮": "roaring with menacing aura, powerful",
        "归元收势": "reverting form, calming down",
    },
}

# 所有形态共有的负面词（API 一般不支持负面提示，但部分兼容接口可传；此处仅作文档）
NEGATIVE = "2d, flat, sketch, partial, cropped, close-up, low quality, deformed"


def build_prompt(form: str, appearance: str, name_en: str, action: str | None = None) -> str:
    """构建纯净 API 提示词。

    :param form: companion / travel / battle
    :param appearance: 神兽外貌英文描述（来自 beasts.json appearance 的英译或用户给的英文）
    :param name_en: 神兽英文名（如 Nine-Tailed Fox）
    :param action: 可选，FORM_ACTIONS[form] 中的动作中文名；传入则追加动态姿势关键词
    :return: 可直接传给文生图 API 的英文提示词
    """
    if form not in FORM_BASE:
        raise ValueError(f"未知形态: {form}，应为 {FORM_ORDER}")
    base = FORM_BASE[form].format(name=name_en, appearance=appearance)
    if action:
        kw = FORM_ACTIONS.get(form, {}).get(action)
        if kw:
            base = f"{base}, in a dynamic pose, {kw}"
    return base


def action_names(form: str) -> list[str]:
    """返回某形态的全部动作中文名。"""
    return list(FORM_ACTIONS.get(form, {}).keys())


def get_beast(name: str) -> dict | None:
    """从 beasts.json 按 name / aliases 匹配神兽，返回整条记录（含 appearance / source 等）。"""
    if not os.path.exists(BEASTS_JSON):
        return None
    try:
        with open(BEASTS_JSON, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    beasts = data.get("beasts", [])
    # 精确匹配 name
    for b in beasts:
        if b.get("name") == name:
            return b
    # 别名匹配
    for b in beasts:
        if name in (b.get("aliases") or []):
            return b
    # 模糊包含
    for b in beasts:
        if name in b.get("name", "") or b.get("name", "") in name:
            return b
    return None


if __name__ == "__main__":
    # 自测
    b = get_beast("九尾狐")
    print("命中:", b["name"], "|", b["appearance"])
    for fm in FORM_ORDER:
        p = build_prompt(fm, b["appearance"], "Nine-Tailed Fox")
        print(f"\n[{fm}] {FORM_LABELS[fm]}\n{p}\nSIZE={FORM_SIZE[fm]}")
        print("动作:", action_names(fm))
