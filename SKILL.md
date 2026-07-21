---
name: qianjin-shanhaijing-pet
description: "神兽宠物提示词生成器：输入一只神兽名称（山海经/搜神记/淮南子/神异经/庄子/列子等古籍），自动生成 3 个不同风格版本的 AI 绘画提示词（国风水墨版 / Q版萌宠版 / 暗黑史诗版），每版含英文提示词+简体中文说明+推荐参数。可扩展为桌面养圣兽。"
version: "1.0"
author: qianjin
tags:
  - prompt
  - shen-shou
  - shanhaijing
  - mythical-beast
  - ai-art
  - character-design
license: MIT
---

# 神兽宠物提示词生成器 · qianjin-shanhaijing-pet

> **输入一只神兽名 → 输出 3 个风格版本的绘画提示词。国风水墨 / Q版萌宠 / 暗黑史诗，一键三连。**

本技能的风格语言继承自 `qianjin-ip-design`（6 大风格 × 8 维设计体系），此处将「IP 角色」替换为「古籍神兽」，并按宠物养成场景做了适配。

---

## 一、技能定位

| 项目 | 说明 |
|------|------|
| 输入 | 任意神兽名称（如「九尾狐」「烛龙」「鲲鹏」「白泽」） |
| 输出 | 同一只神兽的 **3 个风格版本** 提示词，每版含：英文提示词 + 简体中文说明 + 推荐参数 |
| 风格 | 国风水墨版（典籍） · Q版萌宠版（陪伴） · 暗黑史诗版（威严） |
| 数据 | 内置 `references/beasts.json` 神兽名录（山海经为主 + 诸子古籍），查表优先；查不到用模型古籍知识兜底 |
| 适用 | Midjourney / Stable Diffusion / 即梦 / 可灵 等文生图工具 |
| 远期 | 见第七节「桌面养圣兽」路线图 |

**输出语言规则（强制）**：提示词主体用英文（喂给绘图模型），设计说明用**简体中文**，**不使用繁体**。

---

## 二、输入处理流程

收到神兽名后，按以下顺序处理：

```
1. 读 references/beasts.json
2. 按 name / aliases 精确或模糊匹配
   ├─ 命中 → 用该条 appearance（外貌）/ symbolism（象征）特征生成提示词
   └─ 未命中 → 用模型自身古籍知识生成，并在输出顶部标注「[模型推断] 未在名录命中，以下基于古籍常识生成」
3. 套用第三节「三风格生成规则」分别产出 国风 / 萌系 / 暗黑 三版
4. 按第四节「输出格式规范」排版返回
```

> 匹配提示：用户可能用别名（如「青丘狐」= 九尾狐、「狍鸮」= 饕餮、「帝江」= 混沌）。先比 aliases 再比 name。

---

## 三、三风格生成规则

每个风格给出：**定位 · 固定视觉关键词（中英）· 构图镜头 · 色彩 · 细节记忆点 · 负面词 · 推荐参数 · 提示词模板**。生成时把 `beasts.json` 里的外貌特征填入模板 `{appearance}`，把神兽名填入 `{name}`。

### 3.1 国风水墨版（典籍风）

> **定位**：回归山海经原典气质——古籍插图 / 宋元工笔 / 水墨写意的神兽，像从绢本上走下来。气质内敛、有根有源（锚定 qianjin-ip-design 国风系：3-5 头身写意、凤眼留白、传统色、线条流动）。

- **固定视觉关键词**
  - 中文：古籍神兽插图、水墨晕染、工笔重彩、绢本设色、白描线条、留白意境、传统纹样（云纹/海水江崖纹/宝相花）、朱砂石青赭石矿物色
  - EN: classical Chinese bestiary illustration, ink wash painting, gongbi fine brushwork, mineral pigments (azurite, malachite, cinnabar), flowing brushwork, elegant negative space, silk texture, Song/Yuan dynasty aesthetic
- **构图镜头**：中景或全身，竖构图为主，神兽居于留白之中，可有祥云/远山/水波点睛
- **色彩**：传统色系——墨黑、朱砂、石青、黛绿、藤黄、月白；金线勾勒不超过 3%
- **细节记忆点**：依据原典外貌（九尾、独足、人面、多首等）如实呈现，不萌化；可加印章/题跋氛围
- **负面词**：modern, 3d render, chibi, cute, neon, photograph, low quality
- **推荐参数**：`--ar 3:4 --niji 6 --style expressive`（MJ 用 --niji 出东方味）
- **模板**：
  ```
  A traditional Chinese classical bestiary illustration of {name}, {appearance}. Ink-wash and gongbi style, mineral pigments on silk, flowing brushwork, elegant negative space, subtle cloud and wave motifs, mythological creature from Shan Hai Jing, serene and dignified, masterful classical Chinese art --ar 3:4 --niji 6 --style expressive
  ```

### 3.2 Q版萌宠版（陪伴风）

> **定位**：把神兽「宠物化」——大头小身、圆润软萌，适合做桌面陪伴/盲盒/贴纸（锚定 qianjin-ip-design 萌系：2-3 头身、马卡龙色、圆润无尖角、大眼高光）。

- **固定视觉关键词**
  - 中文：Q版、大头身比、圆滚滚、软萌、马卡龙色、蓬松毛发、大眼睛带高光、毛绒玩具质感、可爱表情、纯色/柔和背景、贴纸风
  - EN: chibi, kawaii, big head small body, round fluffy, pastel macaron colors, huge sparkly eyes, plush toy texture, adorable expression, soft background, sticker style, cute pet companion
- **构图镜头**：近景大头特写或全身Q版，居中，背景留白或淡色块
- **色彩**：高明度中低饱和（莫兰迪粉/奶蓝/奶油黄），1 处高饱和点缀（如朱红铃铛）
- **细节记忆点**：保留神兽 1 个可辨识特征（如九尾狐保留蓬松九尾、烛龙保留蜿蜒蛇身轮廓），但整体幼态化；可加配饰（铃铛/蝴蝶结/小窝）
- **负面词**：scary, dark, realistic, gore, sharp, horror
- **推荐参数**：`--ar 1:1 --s 100`（方图适合头像/贴纸）
- **模板**：
  ```
  Chibi kawaii pet version of {name}, {appearance} transformed into a cute companion: oversized head, tiny body, huge sparkly eyes, round fluffy shapes, pastel macaron colors, plush toy texture, adorable expression, white or soft pastel background, sticker style, 3D render pixar-like, soft lighting --ar 1:1 --s 100
  ```

### 3.3 暗黑史诗版（威严风）

> **定位**：放大神兽「凶兽/神性」一面——诡谲、威严、压迫感，适合做收藏级立绘/游戏原画（锚定 qianjin-ip-design 暗黑系：4-7 头身修长、深陷眼窝、尖刺/披风、硬阴影、非对称）。

- **固定视觉关键词**
  - 中文：暗黑奇幻、哥特神话、幽冥辉光（血红/玄黑/鬼绿）、深重阴影、硬光、精密暗纹、威压气场、超自然、电影感
  - EN: dark fantasy, gothic mythological beast, ominous and majestic, deep shadows, eerie glow (crimson, obsidian, ghostly green), intricate dark details, dramatic chiaroscuro lighting, menacing aura, hyper-detailed, cinematic
- **构图镜头**：低角度仰拍或侧面剪影，强光影对比，神兽占据画面主体
- **色彩**：明度 ≤ 30% 的暗调——玄黑、深紫、暗红、墨绿；点缀色荧光/高饱和 ≤ 5%
- **细节记忆点**：强化原典中的「非人感」特征（多首、异瞳、獠牙、鳞甲、焰/雷属性）；披风/锁链/尖刺/骨翼等暗黑记忆点；非对称构图
- **负面词**：cute, chibi, bright, pastel, cartoon, flat
- **推荐参数**：`--ar 3:4 --s 750 --v 6`（高 --s 出精密暗纹）
- **模板**：
  ```
  Dark fantasy epic creature {name}, {appearance}, ominous and majestic, gothic mythological beast, deep shadows, eerie glow, intricate dark details, dramatic chiaroscuro lighting, menacing aura, hyper-detailed, cinematic dark fantasy art --ar 3:4 --s 750 --v 6
  ```

---

## 四、输出格式规范

对每个神兽，按以下结构返回（三版顺序固定：国风 → 萌系 → 暗黑）：

```
## 🐉 {神兽名}（{出处}）
> 外貌特征：{appearance}
> 象征：{symbolism}

### ① 国风水墨版
**英文提示词**
<模板填好后的完整英文 prompt>

**简体中文说明**
<2-3 句：这版如何还原原典气质、用了哪些传统元素>

**推荐参数**：--ar 3:4 --niji 6 --style expressive

### ② Q版萌宠版
**英文提示词**
<...>

**简体中文说明**
<...>

**推荐参数**：--ar 1:1 --s 100

### ③ 暗黑史诗版
**英文提示词**
<...>

**简体中文说明**
<...>

**推荐参数**：--ar 3:4 --s 750 --v 6
```

**规则**：
- 英文提示词必须可直接复制进绘图工具（不含中文、不含占位符）
- 简体中文说明仅作设计解读，不进入绘图模型
- 若三版都想微调某特征（如统一保留「九尾」），在各自说明里点明
- 全程**不使用繁体**

---

## 五、神兽数据使用

- 数据文件：`references/beasts.json`，结构如下：
  ```json
  {
    "beasts": [
      {
        "name": "九尾狐",
        "aliases": ["青丘狐"],
        "source": "山海经·南山经",
        "appearance": "状如狐而九尾，音如婴儿啼，身有赤黄纹",
        "symbolism": "祥瑞之兽，亦食人；后世视为狐仙始祖",
        "type": "瑞兽"
      }
    ]
  }
  ```
- **查表优先**：能命中就用 `appearance` 填模板，保证「同名同貌」稳定一致
- **兜底**：未命中用模型古籍知识生成，输出标注 `[模型推断]`
- **扩展**：用户可自行往 `beasts.json` 增删神兽；新增字段保持一致即可

---

## 六、示例（九尾狐）

## 🐉 九尾狐（山海经·南山经）
> 外貌特征：状如狐而九尾，音如婴儿啼，身有赤黄纹
> 象征：祥瑞之兽，亦食人；后世视为狐仙始祖

### ① 国风水墨版
**英文提示词**
A traditional Chinese classical bestiary illustration of Nine-Tailed Fox, a fox-like beast with nine lush tails and reddish-yellow stripes. Ink-wash and gongbi style, mineral pigments on silk, flowing brushwork, elegant negative space, subtle cloud and wave motifs, mythological creature from Shan Hai Jing, serene and dignified, masterful classical Chinese art --ar 3:4 --niji 6 --style expressive

**简体中文说明**
还原青丘九尾狐的原典样貌：九尾与赤黄纹如实呈现，不萌化。以宋元工笔花鸟的留白与矿物色（朱砂、石青）营造典籍之气，适合做书封／卷轴风插画。

**推荐参数**：--ar 3:4 --niji 6 --style expressive

### ② Q版萌宠版
**英文提示词**
Chibi kawaii pet version of Nine-Tailed Fox, a fox-like beast with nine lush tails transformed into a cute companion: oversized head, tiny body, huge sparkly eyes, round fluffy shapes, pastel macaron colors, plush toy texture, adorable expression, white or soft pastel background, sticker style, 3D render pixar-like, soft lighting --ar 1:1 --s 100

**简体中文说明**
把九尾狐宠物化：保留蓬松九尾作为辨识点，整体幼态大头身比、马卡龙暖色、毛绒玩具质感。适合做桌面陪伴形象／盲盒／贴纸。

**推荐参数**：--ar 1:1 --s 100

### ③ 暗黑史诗版
**英文提示词**
Dark fantasy epic creature Nine-Tailed Fox, a fox-like beast with nine lush tails and reddish-yellow stripes, ominous and majestic, gothic mythological beast, deep shadows, eerie glow, intricate dark details, dramatic chiaroscuro lighting, menacing aura, hyper-detailed, cinematic dark fantasy art --ar 3:4 --s 750 --v 6

**简体中文说明**
放大九尾狐「狐仙／妖异」一面：九尾如焰影铺展，幽冥辉光勾勒轮廓，硬阴影塑造威压。适合做游戏原画／收藏级立绘。

**推荐参数**：--ar 3:4 --s 750 --v 6

---

## 七、路线图：桌面养圣兽（远期）

第一步已交付「3 版提示词生成」。后续演进方向：

1. **生成即预览**：调用文生图 API，直接把三版渲染出来给用户挑
2. **养成系统**：选一只作为「本命圣兽」，记到本地状态文件（等级/好感/进化）
3. **桌面陪伴**：常驻桌面角落的小窗，圣兽随好感变化姿态/动作（参考 萌系情绪公式）
4. **跨风格进化**：高等级解锁风格变异（如萌系→国风→暗黑形态进化）

本技能第一步不实现上述，仅预留 `type` 字段（瑞兽/凶兽/神兽）供后续养成逻辑使用。

---

## 八、版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-07-21 | 初始版本：国风/萌系/暗黑三风格提示词生成 + 神兽名录（山海经为主+诸子古籍） |
