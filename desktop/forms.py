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
  - 生成的是「完整场景图」：暗黑星空 + 发光时空门/空间裂缝 + 神兽从门中浮现，
    不再要求纯色/孤立背景。App 端只做轻微边缘融合，不再自行绘制传送门。

动作 / 情绪：
  - FORM_ACTIONS：每形态 8 个互动动作（中文名 → 英文追加关键词），用于生成「动作图」。
  - EMOTIONS：通用情绪维度（开心/平静/委屈/害羞/困倦 → 英文关键词），用于生成「情绪待机图」。
  - build_prompt(form, appearance, name_en, action=None, emotion=None)：
      * action 与 emotion 不同时叠加——动作图只带 action，待机图只带 emotion，避免组合爆炸。
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
    # 新策略：让模型直接输出完整场景。
    # 每个形态都明确包含：暗黑星空背景、发光时空门/裂缝、神兽从门中浮现。
    "companion": (
        "A magical cosmic scene of a cute chibi {name} ({appearance}) emerging from a glowing blue space-time portal. "
        "The cub has fluffy VIBRANT orange-gold fur with warm cream accents, huge sparkling eyes, and multiple fluffy tails. "
        "The lower body and paws are partially hidden inside the bright swirling portal light. "
        "Deep dark cosmic background filled with twinkling stars, soft purple-blue nebula clouds, and floating golden light particles. "
        "The portal glow illuminates the cub from below with dreamy cyan-blue light. "
        "Digital 3D chibi art, glossy vinyl toy texture, adorable and mystical, full body, centered, vertical portrait composition."
    ),
    "travel": (
        "A majestic Chinese mythological {name} ({appearance}) in elegant ink-wash and gongbi inspired style, gracefully stepping out of a luminous celestial space-time rift. "
        "SATURATED vermilion red, cobalt blue, emerald green and flowing gold details on its flowing fur and nine tails. "
        "The lower body dissolves into the glowing blue-white portal light. "
        "Dark starry cosmos background with ethereal Chinese cloud wisps, distant galaxies, and scattered spiritual light particles. "
        "Dignified and serene posture, museum-quality digital sculpture, mystical atmosphere, full body, centered, vertical portrait composition."
    ),
    "battle": (
        "A fierce dark fantasy epic {name} ({appearance}) in an aggressive attacking stance, erupting from a crackling space-time rift. "
        "Glowing molten gold and ember-orange fur, blazing crimson eyes, sharp fangs and extended claws. "
        "The lower body is shrouded in the portal's explosive dark energy and electric sparks. "
        "Deep cosmic void background with distant stars, swirling dark nebula, and crackling energy arcs. "
        "Dramatic cinematic lighting with strong rim light, dynamic full body pose, centered, vertical portrait composition, hyper-detailed dark fantasy digital art."
    ),
}

# 各形态推荐的生图尺寸（均用竖图，适配桌面宠物窗口 240x300 的纵向比例）
FORM_SIZE = {
    "companion": "1024x1792",
    "travel": "1024x1792",
    "battle": "1024x1792",
}

# 每形态 8 个互动动作的「提示词追加关键词」（对应 SKILL.md 7.3）
# 用于生成「动作图」——只带 action，不带 emotion。
FORM_ACTIONS = {
    "companion": {
        "蹭蹭撒娇": "nuzzling the screen edge, squinting eyes, affectionate",
        "进食灵果": "holding and nibbling a glowing spirit fruit, puffy cheeks, happy",
        "蜷睡": "curled up sleeping, gentle breathing, peaceful",
        "蹦跳玩耍": "bouncing and chasing its tail, playful, joyful",
        "进化闪光": "glowing with evolution light, hinting transformation",
        "摇尾欢迎": "wagging its tails excitedly, welcoming, cheerful",
        "打滚撒欢": "rolling on its back playfully, belly up, carefree",
        "好奇探头": "leaning forward with head tilted, big curious eyes, peeking",
    },
    "travel": {
        "御云巡游": "riding a cloud, gliding gracefully",
        "探灵扫描": "scanning with swirling spiritual aura",
        "云梢小憩": "resting on a cloud, serene",
        "显形展姿": "striking a dignified pose, traditional ripple effect",
        "引路指津": "pointing toward a direction with tail, guiding",
        "乘风而起": "rising into the wind, flowing scarves, ethereal",
        "抚琴弄乐": "playing a guqin with a tail, musical, elegant",
        "落英环绕": "surrounded by falling petals, dreamy, gentle",
    },
    "battle": {
        "本命神通": "unleashing its signature elemental power, dynamic",
        "结界防御": "raising a dark barrier shield, defensive",
        "蓄力大招": "charging an ultimate move, intense glow",
        "威压咆哮": "roaring with menacing aura, powerful",
        "归元收势": "reverting form, calming down",
        "撕裂斩击": "slashing with claw energy blades, fierce, aggressive",
        "火焰缠身": "engulfed in rising flame, blazing, unstoppable",
        "俯冲突进": "diving forward in a charge, motion blur, ruthless",
    },
}

# 通用情绪维度（用于「情绪待机图」——只带 emotion，不带 action）
# 状态机 ShengShouState.current_emotion() 据此推导当前情绪。
EMOTIONS = {
    "开心": "with a joyful happy expression, bright sparkling eyes, playful smile, cheerful and delighted",
    "平静": "with a calm serene neutral expression, gentle peaceful eyes, dignified and composed",
    "委屈": "with a slightly wronged and lonely look, drooping ears and tails, big watery sad eyes, pitiful",
    "害羞": "looking bashful and shy, faintly blushing, glancing away, slightly hiding behind its tails",
    "困倦": "looking sleepy and drowsy, half-closed heavy eyes, yawning slightly, relaxed and tired",
}

# 所有形态共有的负面词（API 一般不支持负面提示，但部分兼容接口可传；此处仅作文档）
NEGATIVE = "2d, flat, sketch, partial, cropped, close-up, low quality, deformed, plain white background, gray void, solid color background"


def build_prompt(form: str, appearance: str, name_en: str,
                 action: str | None = None, emotion: str | None = None) -> str:
    """构建纯净 API 提示词。

    :param form: companion / travel / battle
    :param appearance: 神兽外貌英文描述（来自 beasts.json appearance 的英译或用户给的英文）
    :param name_en: 神兽英文名（如 Nine-Tailed Fox）
    :param action: 可选，FORM_ACTIONS[form] 中的动作中文名；传入则追加动态姿势关键词（动作图）
    :param emotion: 可选，EMOTIONS 中的情绪中文名；传入则追加情绪关键词（待机图）
    :return: 可直接传给文生图 API 的英文提示词
    """
    if form not in FORM_BASE:
        raise ValueError(f"未知形态: {form}，应为 {FORM_ORDER}")
    base = FORM_BASE[form].format(name=name_en, appearance=appearance)
    # 动作图只带 action，待机图只带 emotion，二者不叠加
    if action:
        kw = FORM_ACTIONS.get(form, {}).get(action)
        if kw:
            base = f"{base}, in a dynamic pose, {kw}"
    elif emotion:
        ek = EMOTIONS.get(emotion)
        if ek:
            base = f"{base}, {ek}"
    return base


def action_names(form: str) -> list[str]:
    """返回某形态的全部动作中文名。"""
    return list(FORM_ACTIONS.get(form, {}).keys())


def emotion_names() -> list[str]:
    """返回全部情绪中文名。"""
    return list(EMOTIONS.keys())


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
    print("\n情绪:", emotion_names())
    # 验证动作图 / 待机图关键词互不叠加
    print("\n[动作图] companion/蹦跳玩耍:",
          build_prompt("companion", b["appearance"], "Nine-Tailed Fox", action="蹦跳玩耍")[-60:])
    print("[待机图] companion/开心:",
          build_prompt("companion", b["appearance"], "Nine-Tailed Fox", emotion="开心")[-60:])
