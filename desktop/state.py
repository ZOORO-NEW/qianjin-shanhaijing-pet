# -*- coding: utf-8 -*-
"""
state.py — 神兽养成本地状态管理

状态存于 ~/.config/shengshou/state.json（见 SKILL.md 7.5）。
养成数值模型（MVP 版，阈值可调）：
  - affection  好感度 0-100，互动增加；达到阈值解锁出行形态
  - level      等级，互动累积经验升级；达到阈值解锁战斗形态
  - energy     精力/灵气 0-100，随时间回复；形态转化消耗
  - exp        经验值，互动累积，满 100 升 1 级
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field, asdict

DEFAULT_STATE_DIR = os.path.join(os.path.expanduser("~"), ".config", "shengshou")
DEFAULT_STATE_PATH = os.path.join(DEFAULT_STATE_DIR, "state.json")

# ---- 养成阈值（实现时可调）----
UNLOCK_TRAVEL_AFFECTION = 30     # 好感≥30 解锁出行形态
UNLOCK_BATTLE_LEVEL = 5          # 等级≥5 解锁战斗形态
TRANSFORM_ENERGY_COST = 20       # 每次形态转化消耗精力
ENERGY_REGEN_PER_SEC = 1 / 60    # 每 60 秒回复 1 点精力
EXP_PER_INTERACT = 12            # 每次互动获得经验
AFFECTION_PER_INTERACT = 6       # 每次互动获得好感
ENERGY_PER_INTERACT = 3          # 每次互动获得精力
LEVEL_UP_EXP = 100               # 升 1 级所需经验


@dataclass
class ShengShouState:
    beast: str = ""                 # 神兽中文名
    name_en: str = ""               # 英文名（生图用）
    level: int = 1
    exp: int = 0
    affection: int = 0
    energy: int = 100
    current_form: str = "companion"
    unlocked_forms: list = field(default_factory=lambda: ["companion"])
    last_seen: float = field(default_factory=time.time)

    # ------------------------------------------------------------------ #
    # 持久化
    # ------------------------------------------------------------------ #
    @classmethod
    def load(cls, path: str = DEFAULT_STATE_PATH) -> "ShengShouState":
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                s = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
                s.tick()  # 载入即按时间回精力
                return s
            except (json.JSONDecodeError, OSError, TypeError):
                pass
        return cls()

    def save(self, path: str = DEFAULT_STATE_PATH) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------ #
    # 养成逻辑
    # ------------------------------------------------------------------ #
    def tick(self) -> None:
        """按真实流逝时间回复精力（每次交互/载入时调用）。"""
        now = time.time()
        elapsed = max(0.0, now - self.last_seen)
        self.last_seen = now
        regen = int(elapsed * ENERGY_REGEN_PER_SEC)
        if regen > 0:
            self.energy = min(100, self.energy + regen)

    def _check_unlock(self) -> list:
        """根据好感/等级解锁形态，返回本次新解锁的形态列表。"""
        newly = []
        if "travel" not in self.unlocked_forms and self.affection >= UNLOCK_TRAVEL_AFFECTION:
            self.unlocked_forms.append("travel")
            newly.append("travel")
        if "battle" not in self.unlocked_forms and self.level >= UNLOCK_BATTLE_LEVEL:
            self.unlocked_forms.append("battle")
            newly.append("battle")
        return newly

    def interact(self, action: str | None = None) -> dict:
        """互动一次：增长好感/经验/精力，可能升级与解锁。"""
        self.tick()
        self.affection = min(100, self.affection + AFFECTION_PER_INTERACT)
        self.energy = min(100, self.energy + ENERGY_PER_INTERACT)
        self.exp += EXP_PER_INTERACT
        leveled = False
        while self.exp >= LEVEL_UP_EXP:
            self.exp -= LEVEL_UP_EXP
            self.level += 1
            leveled = True
        unlocked = self._check_unlock()
        self.save()
        return {"leveled": leveled, "unlocked": unlocked, "action": action}

    def can_transform(self, target: str) -> tuple[bool, str]:
        if target == self.current_form:
            return False, "已是该形态"
        if target not in self.unlocked_forms:
            return False, f"形态未解锁（需好感≥{UNLOCK_TRAVEL_AFFECTION} 或 等级≥{UNLOCK_BATTLE_LEVEL}）"
        if self.energy < TRANSFORM_ENERGY_COST:
            return False, f"精力不足（需 {TRANSFORM_ENERGY_COST}，当前 {self.energy}）"
        return True, "ok"

    def transform(self, target: str) -> tuple[bool, str]:
        ok, reason = self.can_transform(target)
        if not ok:
            return False, reason
        self.tick()
        self.energy = max(0, self.energy - TRANSFORM_ENERGY_COST)
        self.current_form = target
        self.save()
        return True, f"已切换至 {target}"

    def summary(self) -> str:
        return (
            f"🐉 {self.beast}（Lv.{self.level}）\n"
            f"好感 {self.affection}/100  精力 {self.energy}/100  经验 {self.exp}/{LEVEL_UP_EXP}\n"
            f"当前形态 {self.current_form}  已解锁 {', '.join(self.unlocked_forms)}"
        )


if __name__ == "__main__":
    s = ShengShouState.load()
    print("初始:", s.summary())
    for i in range(10):
        r = s.interact()
        if r["leveled"]:
            print("升级! Lv.", s.level)
        if r["unlocked"]:
            print("解锁形态:", r["unlocked"])
    print(s.summary())
    print("转化出行:", s.transform("travel"))
    print("转化战斗:", s.transform("battle"))
