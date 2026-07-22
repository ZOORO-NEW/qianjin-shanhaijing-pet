# -*- coding: utf-8 -*-
"""
generator.py — 文生图 API 客户端（OpenAI 兼容，可插拔）

支持 DALL·E 3（返回图片 URL）与 gpt-image-1（返回 base64）两种返回格式。
未配置 api_key 时 generate() 返回 None，由上层回退到占位图。
免 key 平台（如 Pollinations.ai）：base_url 含 "pollinations" 时放行空 key，
并自动将 model 切换为自有机型（flux），匿名限速时自动退避重试。

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
import time
import urllib.request
import urllib.error

from forms import FORM_SIZE, build_prompt

try:
    from PIL import Image
except ImportError:
    Image = None  # 去背功能不可用但不阻塞生成

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


def _auto_remove_bg(path: str) -> bool:
    """对生成的图做 AI 智能去背（U²-Net 神经网络），替代手工阈值/flood fill。

    使用 rembg 库（基于 U²-Net 语义分割）识别前景主体 vs 背景，
    边缘干净、无紫边、不伤主体。比任何颜色阈值方法都可靠。

    前置：pip install rembg[cli]
    若未安装 rembg / onnxruntime 无可用后端 / 模型权重缺失，均静默跳过
    （不影响使用，图仍保存为原样，由 app 端 v7 flood fill 兜底去背）。

    :param path: 图片文件路径（原地覆盖为透明 PNG）
    :return: True=处理成功, False=跳过或异常
    """
    try:
        import importlib.util
        # 前置检查：rembg 与 onnxruntime 必须可用，且 onnxruntime 有执行后端
        if importlib.util.find_spec("rembg") is None:
            return False
        if importlib.util.find_spec("onnxruntime") is None:
            print("[generator] onnxruntime 缺失，跳过 AI 去背（app 端 flood fill 兜底）")
            return False
        import onnxruntime as ort
        if not ort.get_available_providers():
            print("[generator] onnxruntime 无可用执行后端，跳过 AI 去背")
            return False
        from rembg import remove
        img = Image.open(path)
        result = remove(img)
        result.save(path, "PNG")
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"[generator] AI 去背跳过（不影响使用，app 端 flood fill 兜底）: {e}")
        return False


def generate(
    beast: str,
    name_en: str,
    form: str,
    appearance: str,
    action: str | None = None,
    emotion: str | None = None,
    config: dict | None = None,
    assets_dir: str | None = None,
) -> str | None:
    """生成一张神兽形态图，保存到 assets/<beast>/<form>[_<action>].png。

    返回保存路径；未配置 key 或调用失败返回 None。
    """
    config = config or load_config()
    api = config.get("api", {})
    base_url = api.get("base_url", "https://api.openai.com/v1").rstrip("/")
    key = api.get("api_key", "")
    is_pollinations = "pollinations" in base_url.lower()
    is_siliconflow = "siliconflow" in base_url.lower()

    # 免 key 平台（Pollinations 等）放行空 key；其余平台仍需有效 key
    if not is_pollinations and (not key or key.startswith("sk-xxx")):
        return None

    model = api.get("model", "gpt-image-1")
    # Pollinations 用自有机型，避免把 gpt-image-1/dall-e 路由到需 key 的后端
    if is_pollinations and (model.startswith("gpt-image") or model.lower().startswith("dall-e")):
        model = "flux"
    prompt = build_prompt(form, appearance, name_en, action=action, emotion=emotion)
    size = _normalize_size(FORM_SIZE.get(form, "1024x1024"), model)
    # 硅基流动 Kolors 不支持 1024x1792 竖图，映射为 SDXL 系支持的竖图比例
    if is_siliconflow and size == "1024x1792":
        size = "864x1152"

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

    data = None
    last_err = None
    for attempt in range(3 if is_pollinations else 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.load(resp)
            break
        except urllib.error.HTTPError as e:
            last_err = f"{e.code}: {e.read().decode()[:300]}"
            # Pollinations 匿名限速（429）时退避重试
            if e.code == 429 and is_pollinations and attempt < 2:
                time.sleep(3 + attempt * 3)
                continue
            break
        except Exception as e:  # 网络/超时等
            last_err = str(e)
            break
    if data is None:
        print(f"[generator] API 错误 {last_err}")
        return None

    # 取第一张
    item = (data.get("data") or [{}])[0]
    assets_dir = assets_dir or config.get("assets_dir") or os.path.join(HERE, "assets")
    out_dir = os.path.join(assets_dir, _safe_name(beast))
    os.makedirs(out_dir, exist_ok=True)
    # 文件名组合：{form}[_{action}][_{emotion}].png
    # 约定：动作图只带 action，待机图只带 emotion，二者不叠加，避免组合爆炸
    suffix = ""
    if action:
        suffix += f"_{_safe_name(action)}"
    if emotion:
        suffix += f"_{_safe_name(emotion)}"
    out_path = os.path.join(out_dir, f"{form}{suffix}.png")

    # 两种返回：url 或 b64_json
    if item.get("url"):
        try:
            with urllib.request.urlopen(item["url"], timeout=60) as r:
                img_bytes = r.read()
            with open(out_path, "wb") as f:
                f.write(img_bytes)
            _auto_remove_bg(out_path)  # 自动去背
            return out_path
        except Exception as e:
            print(f"[generator] 下载图片失败: {e}")
            return None
    elif item.get("b64_json"):
        try:
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(item["b64_json"]))
            _auto_remove_bg(out_path)  # 自动去背
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
