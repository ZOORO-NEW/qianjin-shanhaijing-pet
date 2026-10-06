# -*- coding: utf-8 -*-
"""
preview_v9.py — 预览 v9 法阵召唤风格
用法: python preview_v9.py [assets_path]
输出: assets/preview_v9.png
"""
import sys, os, math, random
from PIL import Image, ImageDraw, ImageFilter

WIN_W, WIN_H = 240, 300

# ── 找到神兽图片 ──
HERE = os.path.dirname(os.path.abspath(__file__))
default_assets = os.path.join(HERE, "assets")
assets = sys.argv[1] if len(sys.argv) > 1 else default_assets
# 尝试找 battle 或 companion 图片
beast_dir = None
for d in os.listdir(assets):
    full = os.path.join(assets, d)
    if os.path.isdir(full) and any(f.endswith('.png') for f in os.listdir(full)):
        beast_dir = full
        break
if not beast_dir:
    print("找不到神兽图片")
    sys.exit(1)

src_path = None
for fname in ["battle.png", "companion.png", "travel.png"]:
    p = os.path.join(beast_dir, fname)
    if os.path.exists(p):
        src_path = p
        break
if not src_path:
    print(f"在 {beast_dir} 中找不到 PNG")
    sys.exit(1)

print(f"使用图片: {src_path}")
src = Image.open(src_path).convert("RGBA")


def make_card_v9(src):
    """v9 灵兽召唤法阵 —— 明亮能量漩涡，神兽从光芒中浮现"""
    W, H = WIN_W, WIN_H

    # ═══ 1. 深空渐变背景 ═══
    out = Image.new("RGBA", (W, H), (6, 8, 16, 255))
    od = ImageDraw.Draw(out)
    for y in range(H):
        ratio = y / H
        r = int(6 + ratio * 18)
        g = int(8 + ratio * 28)
        b = int(16 + ratio * 45)
        od.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # 星点（上半部）
    random.seed(42)
    for _ in range(45):
        sx = random.randint(0, W-1)
        sy = random.randint(0, int(H*0.55))
        br = random.randint(90, 230)
        out.putpixel((sx, sy), (br, br, min(255, br+35), 255))

    # ═══ 2. 传送门参数 ═══
    pcx = W // 2
    pcy = int(H * 0.66)
    prx = int(W * 0.46)
    pry = int(H * 0.38)

    # ═══ 3. 环境光（大范围柔光漫反射）═══
    ambient = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(ambient)
    for off in range(90, 0, -3):
        a = int(22 * (1 - off/90) ** 0.6)
        ad.ellipse([pcx-prx-off*2, pcy-pry-off*2,
                    pcx+prx+off*2, pcy+pry+off*1.5],
                   fill=(50, 120, 200, a))
    ambient = ambient.filter(ImageFilter.GaussianBlur(radius=18))
    out = Image.alpha_composite(out, ambient)

    # ═══ 4. 法阵核心（5层径向渐变 = 明亮能量场）═══
    portal = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(portal)

    # 外层：深海蓝
    pd.ellipse([pcx-prx, pcy-pry, pcx+prx, pcy+pry],
               fill=(18, 45, 110, 170))

    # 中外层：靛蓝
    pd.ellipse([pcx-int(prx*0.76), pcy-int(pry*0.76),
                pcx+int(prx*0.76), pcy+int(pry*0.76)],
               fill=(35, 25, 140, 195))

    # 中层：紫罗兰
    pd.ellipse([pcx-int(prx*0.52), pcy-int(pry*0.52),
                pcx+int(prx*0.52), pcy+int(pry*0.52)],
               fill=(80, 35, 170, 215))

    # 内层：亮青
    pd.ellipse([pcx-int(prx*0.28), pcy-int(pry*0.28),
                pcx+int(prx*0.28), pcy+int(pry*0.28)],
               fill=(60, 190, 255, 230))

    # 核心：白青高光
    pd.ellipse([pcx-int(prx*0.11), pcy-int(pry*0.11),
                pcx+int(prx*0.11), pcy+int(pry*0.11)],
               fill=(200, 245, 255, 250))

    portal = portal.filter(ImageFilter.GaussianBlur(radius=9))
    out = Image.alpha_composite(out, portal)

    # ═══ 5. 能量漩涡弧线 ═══
    swirl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(swirl)
    swirl_arcs = [
        (0.88,  20, 210, (140, 200, 255, 80),  2),
        (0.72,  60, 250, (170, 220, 255, 70),  2),
        (0.52, 100, 290, (200, 235, 255, 55),  1),
        (0.32, 150, 340, (220, 245, 255, 40),  1),
    ]
    for sc, sa, ea, col, sw in swirl_arcs:
        srx = int(prx * sc); sry = int(pry * sc)
        sd.arc([pcx-srx, pcy-sry, pcx+srx, pcy+sry],
               start=sa, end=ea, fill=col, width=sw)
    swirl = swirl.filter(ImageFilter.GaussianBlur(radius=2))
    out = Image.alpha_composite(out, swirl)

    # ═══ 6. 放射光线 ═══
    rays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rays)
    random.seed(99)
    for i in range(10):
        angle = random.uniform(math.pi * 0.9, math.pi * 2.1)
        r0 = prx * random.uniform(0.15, 0.4)
        r1 = r0 + random.randint(35, 85)
        x0 = pcx + int(r0 * math.cos(angle))
        y0 = pcy + int(r0 * pry/prx * math.sin(angle))
        x1 = pcx + int(r1 * math.cos(angle))
        y1 = y0 - int((r1-r0) * 0.7)  # 向上偏
        a = random.randint(18, 45)
        rd.line([(x0, y0), (x1, y1)], fill=(180, 225, 255, a), width=2)
    rays = rays.filter(ImageFilter.GaussianBlur(radius=3))
    out = Image.alpha_composite(out, rays)

    # ═══ 7. 能量粒子 ═══
    parts = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pp = parts.load()
    random.seed(2024)
    for _ in range(70):
        ang = random.uniform(0, math.pi * 2)
        dist = random.uniform(0.08, 0.92)
        px = pcx + int(prx * dist * math.cos(ang))
        py = pcy + int(pry * dist * math.sin(ang))
        if 0 <= px < W and 0 <= py < H:
            br = random.randint(140, 255)
            pa = random.randint(90, 220)
            sz = 1 if random.random() > 0.2 else 2
            for dx in range(sz):
                for dy in range(sz):
                    npx, npy = px+dx, py+dy
                    if 0 <= npx < W and 0 <= npy < H:
                        pp[npx, npy] = (br, min(255, br+25), 255, pa)
    out = Image.alpha_composite(out, parts)

    # ═══ 8. 神兽（从光芒中浮现）═══
    iw, ih = src.size
    target_h = int(H * 0.70)
    sc = target_h / ih
    nw = max(1, int(iw * sc))
    nh = max(1, int(ih * sc))
    fitted = src.resize((nw, nh), Image.LANCZOS)
    bx = (W - nw) // 2
    by = pcy - int(nh * 0.42)
    by = max(0, by)

    # 神兽底部融入光晕
    glow = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
    gp = glow.load()
    fp = fitted.load()
    for yy in range(nh):
        for xx in range(nw):
            aa = fp[xx, yy][3]
            if aa > 25:
                # 越靠近底部，光晕越强
                bottom_factor = (yy / nh) ** 1.5
                gp[xx, yy] = (80, 170, 255, min(55, int(aa * 0.18 * bottom_factor)))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=5))
    out.paste(glow, (bx, by), glow)

    # 神兽本体
    out.paste(fitted, (bx, by), fitted)

    # ═══ 9. 前景柔光弧（增强纵深）═══
    front = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(front)
    for gw in range(10, 0, -1):
        ga = int(30 * (1 - gw/10) ** 0.7)
        fd.arc([pcx-prx+gw, pcy-pry+gw//2,
                pcx+prx-gw, pcy+pry-gw//2],
               start=165, end=385, fill=(160, 215, 255, ga), width=2)
    front = front.filter(ImageFilter.GaussianBlur(radius=2))
    out = Image.alpha_composite(out, front)

    # ═══ 10. 边缘极轻压暗 ═══
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vp = vig.load()
    for yy in range(H):
        for xx in range(W):
            ex = min(xx, W-1-xx)
            ey = min(yy, H-1-yy)
            ed = (ex*ex + ey*ey) ** 0.5
            if ed > 25:
                vp[xx, yy] = (6, 8, 16, min(65, int((ed-25)*0.45)))
    out = Image.alpha_composite(out, vig)

    return out


# ── 生成预览 ──
print("渲染 v9 预览...")
result = make_card_v9(src)
out_path = os.path.join(beast_dir, "preview_v9.png")
result.save(out_path)
print(f"已保存: {out_path}")
