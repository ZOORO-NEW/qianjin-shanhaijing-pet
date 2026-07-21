# -*- coding: utf-8 -*-
"""
generator.py — 文生图 API 客户端（OpenAI 兼容，可插拔）

支持 DALL·E 3（返回图片 URL）与 gpt-image-1（返回 base64）两种返回格式。
未配置 api_key 时 generate() 返回 None，由上层回退到占位图。

配置（desktop/config.json，从 config.example.json 复制填写）：
{
  "api": {
    "base_url": "https://api.openai.com/v1",
    "api_key": "sk-xxx",
    "model": "gpt-image-1"
  },
  "default_beast": "九尾狐",
  "default_name_en": "Nine-Tailed Fox",
  "assets_dir": "assets"
}
"""

from __future__ import annotations

import base64
import json
import os
import urllib.request
import urllib.error

from forms import FORM_SIZE, build_prompt

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(HERE, "config.json")

# gpt-image-1 支持的尺寸集合（DALL·E 3 用 1024x1792 代替 1024x1536）
_ALLOWED_GPT = {"1024x1024", "1536x1024", "1024x1536"}


def load_config(path: str = DEFAULT_CONFIG) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _normalize_size(size: str, model: str) -> str:
    if model == "gpt-image-1":
        return size if size in _ALLOWED_GPT else "1024x1536"
    return size  # DALL·E 3 支持 1024x1792


def _safe_name(s: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in s)


def generate(
    beast: str,
    name_en: str,
    form: str,
    appearance: str,
    action: str | None = None,
    config: dict | None = None,
    assets_dir: str | None = None,
) -> str | None:
    """生成一张神兽形态图，保存到 assets/<beast>/<form>[_<action>].png。

    返回保存路径；未配置 key 或调用失败返回 None。
    """
    config = config or load_config()
    api = config.get("api", {})
    key = api.get("api_key", "")
    if not key or key.startswith("sk-xxx"):
        return None

    base_url = api.get("base_url", "https://api.openai.com/v1").rstrip("/")
    model = api.get("model", "gpt-image-1")
    prompt = build_prompt(form, appearance, name_en, action=action)
    size = _normalize_size(FORM_SIZE.get(form, "1024x1024"), model)

    body = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "n": 1,
    }
    req = urllib.request.Request(
        f"{base_url}/images/generations",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        print(f"[generator] API 错误 {e.code}: {e.read().decode()[:300]}")
        return None
    except Exception as e:  # 网络/超时等
        print(f"[generator] 调用失败: {e}")
        return None

    # 取第一张
    item = (data.get("data") or [{}])[0]
    assets_dir = assets_dir or config.get("assets_dir") or os.path.join(HERE, "assets")
    out_dir = os.path.join(assets_dir, _safe_name(beast))
    os.makedirs(out_dir, exist_ok=True)
    suffix = f"_{_safe_name(action)}" if action else ""
    out_path = os.path.join(out_dir, f"{form}{suffix}.png")

    # 两种返回：url 或 b64_json
    if item.get("url"):
        try:
            with urllib.request.urlopen(item["url"], timeout=60) as r:
                img_bytes = r.read()
            with open(out_path, "wb") as f:
                f.write(img_bytes)
            return out_path
        except Exception as e:
            print(f"[generator] 下载图片失败: {e}")
            return None
    elif item.get("b64_json"):
        try:
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(item["b64_json"]))
            return out_path
        except Exception as e:
            print(f"[generator] 写入图片失败: {e}")
            return None
    print("[generator] 返回中无 url/b64_json")
    return None


if __name__ == "__main__":
    cfg = load_config()
    if not cfg:
        print("未找到 config.json，跳过（上层将用占位图）")
    else:
        p = generate("九尾狐", "Nine-Tailed Fox", "companion",
                     "a fox-like beast with nine lush tails and reddish-yellow stripes", config=cfg)
        print("生成:", p)
