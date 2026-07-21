---
name: qianjin-shanhaijing-pet
description: "神兽宠物提示词生成器：输入一只神兽名称（山海经/搜神记/淮南子/神异经/庄子/列子等古籍），自动生成 3 个不同风格版本的 3D 立体 AI 绘画提示词（国风数字雕塑 / Q版萌宠手办 / 暗黑史诗模型），每版含英文提示词+简体中文说明+推荐参数。形象完整全身、纯色/透明抠图友好背景。可扩展为桌面养圣兽。"
version: "1.3"
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
| 风格 | 国风水墨版（3D 国风雕塑） · Q版萌宠版（3D 盲盒手办） · 暗黑史诗版（3D 游戏模型）——**三版均为 3D 立体渲染、完整全身、纯色/透明抠图背景** |
| 数据 | 内置 `references/beasts.json` 神兽名录（山海经为主 + 诸子古籍），查表优先；查不到用模型古籍知识兜底 |
| 适用 | Midjourney / Stable Diffusion / 即梦 / 可灵 等文生图工具 |
| 远期/已实现 | 见第七、八节「桌面养圣兽」——第八节为可运行的桌面应用模块（desktop/） |

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

> **【全局强制约束（三版通用，必须写入每条提示词）】**
> 1. **3D 立体感**：所有形象必须为 **3D 渲染**，突出体积与立体感（关键词 `3D render` / `volumetric` / `sculpted form`）。
> 2. **完整形象**：必须呈现 **完整全身**（关键词 `full body` / `complete character`），**禁止局部特写或裁剪**（负面词 `partial` / `cropped` / `close-up`）。
> 3. **抠图友好背景**：使用 **纯色背景或透明背景**，主体独立（关键词 `solid color background` / `transparent background` / `isolated subject` / `easy to cutout`）。

### 3.1 国风水墨版（3D 国风数字雕塑）

> **定位**：以 3D 渲染呈现国风神兽——像从绢本走下来的立体摆件 / 数字藏品，保留水墨工笔的纹样与矿物色，但强调体积与立体感。气质内敛、有根有源（锚定 qianjin-ip-design 国风系：传统色、线条流动、留白意境，但立体化）。

- **固定视觉关键词**
  - 中文：3D 国风神兽、立体雕塑感、水墨意象、工笔纹理、朱砂石青赭石矿物色、传统纹样（云纹/海水江崖纹/宝相花）、留白意境、数字藏品/文创摆件质感
  - EN: 3D render of Chinese mythological beast, volumetric sculpted form, ink-wash inspired, gongbi textures, mineral pigment colors (azurite, cinnabar, malachite), traditional patterns (cloud/wave/ruyi), elegant, museum collectible, digital figurine
- **构图镜头**：全身中景，居中，完整形象；主体独立，背景纯净
- **色彩**：传统色系——墨黑、朱砂、石青、黛绿、藤黄、月白；金线勾勒不超过 3%
- **细节记忆点**：依据原典外貌（九尾、独足、人面、多首等）如实呈现，不萌化；立体化后保留衣纹/鳞甲的体积阴影
- **负面词**：2d, flat, painting, sketch, chibi, cartoon, modern, neon, photograph, partial, cropped, close-up, low quality
- **推荐参数**：`--ar 3:4 --v 6 --s 250`（用 MJ 写实/3D 模型，不用 --niji）
- **模板**：
  ```
  3D render of a Chinese mythological beast {name}, {appearance}, ink-wash and gongbi inspired, mineral pigment colors, traditional cloud and wave patterns, volumetric sculpted form, elegant and dignified, museum collectible digital figurine, full body, complete character, solid color background, isolated subject, easy to cutout, highly detailed --ar 3:4 --v 6 --s 250
  ```

### 3.2 Q版萌宠版（3D 盲盒手办）

> **定位**：把神兽「宠物化」——3D 立体 Q 版盲盒手办，大头小身、圆润软萌，适合桌面陪伴/盲盒/贴纸（锚定 qianjin-ip-design 萌系：2-3 头身、马卡龙色、圆润无尖角、大眼高光）。

- **固定视觉关键词**
  - 中文：3D Q版、盲盒手办、大头身比、圆滚滚、软萌、马卡龙色、蓬松毛发、大眼睛带高光、毛绒/搪胶质感、可爱表情、纯色背景、贴纸风
  - EN: 3D chibi blind-box figure, big head small body, round fluffy, pastel macaron colors, huge sparkly eyes, vinyl/plush toy texture, adorable expression, solid color background, sticker style, cute pet companion
- **构图镜头**：全身 Q 版，居中，完整形象（不裁切）
- **色彩**：高明度中低饱和（莫兰迪粉/奶蓝/奶油黄），1 处高饱和点缀（如朱红铃铛）
- **细节记忆点**：保留神兽 1 个可辨识特征（如九尾狐保留蓬松九尾、烛龙保留蜿蜒蛇身轮廓），但整体幼态化；可加配饰（铃铛/蝴蝶结/小窝）
- **负面词**：scary, dark, realistic, gore, sharp, horror, 2d, flat, partial, cropped, close-up
- **推荐参数**：`--ar 1:1 --s 100`（方图适合头像/贴纸）
- **模板**：
  ```
  3D chibi blind-box figure of {name}, {appearance} transformed into a cute companion: oversized head, tiny body, huge sparkly eyes, round fluffy shapes, pastel macaron colors, vinyl toy texture, adorable expression, full body, complete character, solid color background or transparent background, isolated subject, easy to cutout, soft lighting --ar 1:1 --s 100
  ```

### 3.3 暗黑史诗版（3D 游戏模型）

> **定位**：放大神兽「凶兽/神性」一面——3D 立体暗黑史诗模型，诡谲、威严、压迫感，适合做收藏级立绘/游戏原画（锚定 qianjin-ip-design 暗黑系：修长、深陷眼窝、尖刺/披风、硬阴影、非对称）。

- **固定视觉关键词**
  - 中文：3D 暗黑奇幻、哥特神话、幽冥辉光（血红/玄黑/鬼绿）、深重阴影、硬光、精密暗纹、威压气场、超自然、电影感、立体雕刻感
  - EN: 3D dark fantasy creature, gothic mythological beast, ominous and majestic, deep shadows, eerie glow (crimson, obsidian, ghostly green), intricate dark details, dramatic chiaroscuro lighting, menacing aura, hyper-detailed, volumetric sculpted form, cinematic
- **构图镜头**：全身中景或低角度，神兽占据画面主体，完整形象
- **色彩**：明度 ≤ 30% 的暗调——玄黑、深紫、暗红、墨绿；点缀荧光/高饱和 ≤ 5%
- **细节记忆点**：强化原典中的「非人感」特征（多首、异瞳、獠牙、鳞甲、焰/雷属性）；披风/锁链/尖刺/骨翼等暗黑记忆点；非对称构图
- **负面词**：cute, chibi, bright, pastel, cartoon, 2d, flat, partial, cropped, close-up
- **推荐参数**：`--ar 3:4 --s 750 --v 6`（高 --s 出精密暗纹）
- **模板**：
  ```
  3D dark fantasy epic creature {name}, {appearance}, ominous and majestic, gothic mythological beast, deep shadows, eerie glow, intricate dark details, dramatic chiaroscuro lighting, menacing aura, hyper-detailed, volumetric sculpted form, full body, complete character, solid color background or transparent background, isolated subject, easy to cutout, cinematic dark fantasy art --ar 3:4 --s 750 --v 6
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
3D render of a Chinese mythological beast Nine-Tailed Fox, a fox-like beast with nine lush tails and reddish-yellow stripes, ink-wash and gongbi inspired, mineral pigment colors, traditional cloud and wave patterns, volumetric sculpted form, elegant and dignified, museum collectible digital figurine, full body, complete character, solid color background, isolated subject, easy to cutout, highly detailed --ar 3:4 --v 6 --s 250

**简体中文说明**
以 3D 立体渲染还原青丘九尾狐的原典样貌：九尾与赤黄纹如实呈现、不萌化，体积阴影保留工笔衣纹质感；纯色背景独立主体，方便抠图做数字藏品／文创摆件。

**推荐参数**：--ar 3:4 --v 6 --s 250

### ② Q版萌宠版
**英文提示词**
3D chibi blind-box figure of Nine-Tailed Fox, a fox-like beast with nine lush tails transformed into a cute companion: oversized head, tiny body, huge sparkly eyes, round fluffy shapes, pastel macaron colors, vinyl toy texture, adorable expression, full body, complete character, solid color background or transparent background, isolated subject, easy to cutout, soft lighting --ar 1:1 --s 100

**简体中文说明**
把九尾狐宠物化为 3D 盲盒手办：保留蓬松九尾作为辨识点，整体幼态大头身比、马卡龙暖色、搪胶质感；完整全身、纯色/透明背景，适合做桌面陪伴形象／盲盒／贴纸。

**推荐参数**：--ar 1:1 --s 100

### ③ 暗黑史诗版
**英文提示词**
3D dark fantasy epic creature Nine-Tailed Fox, a fox-like beast with nine lush tails and reddish-yellow stripes, ominous and majestic, gothic mythological beast, deep shadows, eerie glow, intricate dark details, dramatic chiaroscuro lighting, menacing aura, hyper-detailed, volumetric sculpted form, full body, complete character, solid color background or transparent background, isolated subject, easy to cutout, cinematic dark fantasy art --ar 3:4 --s 750 --v 6

**简体中文说明**
放大九尾狐「狐仙／妖异」一面：3D 立体模型，九尾如焰影铺展，幽冥辉光勾勒轮廓，硬阴影塑造威压；完整全身、纯色/透明背景，适合做游戏原画／收藏级立绘，且便于抠图合成。

**推荐参数**：--ar 3:4 --s 750 --v 6

---

## 七、桌面养圣兽 · 三形态系统（设计规格）

第一步已交付「3 版提示词生成」。本技能的三套风格天然对应一个养成产品的核心设定——**三风格 = 一只圣兽的三种可切换形态**。本节把第二步「桌面养圣兽」的系统设计固化，供后续实现（桌面应用 / 状态机 / 文生图调用）直接复用。

### 7.1 核心概念：三只归一

同一只圣兽拥有 **3 种可切换形态**，与三版提示词一一对应。形态切换是「同一只圣兽的三种面貌」，而非进化替代——进化保留三态，只是当前展示哪一态：

| 形态 | 对应风格版 | 场景定位 | 气质锚点 |
|------|-----------|---------|---------|
| **幼兽陪伴形态** | Q版萌宠版 | 日常陪伴、养成、卖萌 | 软萌、安全、黏人 |
| **出行形态** | 国风水墨版 | 探索、出行、展示原典 | 优雅、有根、祥瑞 |
| **战斗形态** | 暗黑史诗版 | 战斗、防御、威压 | 凶悍、神性、压迫 |

### 7.2 形态转化规则

- **循环转化**：陪伴 ↔ 出行 ↔ 战斗，三者可自由往返切换（非线性进化树）
- **转化消耗**：每次切换消耗「灵气 / 精力值（energy）」，或进入冷却（避免滥用）
- **触发方式**
  - 用户主动指令（如「切战斗形态」）
  - 场景自动触发（进入战斗事件自动切战斗形态、闲置返回陪伴形态）
- **解锁条件**（建议阈值，实现时可调）
  - 陪伴形态：初始即解锁
  - 出行形态：好感度（affection）≥ 3
  - 战斗形态：等级（level）≥ 5 或通关「本命试炼」

### 7.3 互动动作表（每形态 5 个，共 15）

每个动作 = 一种动画姿态，需生成对应的 **动作姿态提示词**（见 7.4）。

**幼兽陪伴形态（陪伴 / 卖萌）**
| # | 动作 | 触发 | 动画描述 | 提示词追加关键词（EN） |
|---|------|------|---------|----------------------|
| 1 | 蹭蹭撒娇 | 点击头部 | 抬头蹭屏幕边缘、眯眼 | nuzzling the screen edge, squinting eyes, affectionate |
| 2 | 进食灵果 | 投喂 | 双手捧发光灵果啃、腮鼓 | holding and nibbling a glowing spirit fruit, puffy cheeks, happy |
| 3 | 蜷睡 | 静置 / 夜晚 | 团成球打盹、呼吸起伏 | curled up sleeping, gentle breathing, peaceful |
| 4 | 蹦跳玩耍 | 点击身体 | 追尾巴 / 弹跳、开心 | bouncing and chasing its tail, playful, joyful |
| 5 | 进化闪光 | 满足条件 | 身体发光、提示可转化 | glowing with evolution light, hinting transformation |

**出行形态（探索 / 展示）**
| # | 动作 | 触发 | 动画描述 | 提示词追加关键词（EN） |
|---|------|------|---------|----------------------|
| 1 | 御云巡游 | 常驻移动 | 踏云漂浮滑行 | riding a cloud, gliding gracefully |
| 2 | 探灵扫描 | 点击 | 环绕灵气探查四周 | scanning with swirling spiritual aura |
| 3 | 云梢小憩 | 静置 | 落于云头歇息 | resting on a cloud, serene |
| 4 | 显形展姿 | 双击 | 国风特效展示原典全貌 | striking a dignified pose, traditional ripple effect |
| 5 | 引路指津 | 指令 | 尾 / 爪指向目标方向 | pointing toward a direction with tail, guiding |

**战斗形态（战斗 / 威压）**
| # | 动作 | 触发 | 动画描述 | 提示词追加关键词（EN） |
|---|------|------|---------|----------------------|
| 1 | 本命神通 | 点击 | 释放属性技能（焰 / 雷 / 幻） | unleashing its signature elemental power, dynamic |
| 2 | 结界防御 | 受击 | 展开护盾 | raising a dark barrier shield, defensive |
| 3 | 蓄力大招 | 长按 | 凝聚终结技辉光 | charging an ultimate move, intense glow |
| 4 | 威压咆哮 | 出场 | 仰头发威压气场 | roaring with menacing aura, powerful |
| 5 | 归元收势 | 脱战 | 转回陪伴形态 | reverting form, calming down |

### 7.4 动作姿态提示词生成规则

把「形态基础模板」+「动作关键词」组合，即可生成任意 (形态 × 动作) 的 3D 提示词：

```
1. 取 7.1 对应形态的【模板】（已含 3D / full body / 纯色背景 等全局约束）
2. 在尾部追加该动作的 EN 关键词（见 7.3 表），并补 motion 描述：
   + ", in a dynamic pose, <action EN keywords>"
3. 保留全局约束不变（3D 立体 / 完整全身 / 抠图友好背景）
4. 输出：英文提示词（直接喂绘图模型）+ 中文说明（动作演绎）
```

> 例：九尾狐「幼兽陪伴形态 · 进食灵果」
> `3D chibi blind-box figure of Nine-Tailed Fox, a fox-like beast with nine lush tails transformed into a cute companion: oversized head, tiny body, huge sparkly eyes, round fluffy shapes, pastel macaron colors, vinyl toy texture, adorable expression, full body, complete character, solid color background or transparent background, isolated subject, easy to cutout, soft lighting, in a dynamic pose, holding and nibbling a glowing spirit fruit, puffy cheeks, happy --ar 1:1 --s 100`

### 7.5 本地状态文件（养成数据）

实现桌面养成时，状态建议存于 `~/.config/shengshou/state.json`：

```json
{
  "beast": "九尾狐",
  "level": 5,
  "affection": 80,
  "current_form": "battle",
  "energy": 60,
  "unlocked_forms": ["companion", "travel", "battle"]
}
```

字段说明：`current_form` 决定桌面常驻展示哪一态；`unlocked_forms` 控制可切换范围；`energy` 控制转化消耗。

### 7.6 实现路线图（远期，仍非本技能功能）

1. **生成即预览**：输入神兽名 → 调文生图 API，渲染三形态 + 动作姿态供挑选
2. **养成系统**：选本命圣兽，写 `state.json`（等级 / 好感 / 形态 / 精力）
3. **桌面陪伴**：常驻桌面角落的小窗，按 `current_form` 展示形态、随动作切换姿态
4. **形态转化**：按 7.2 规则实现 陪伴 ↔ 出行 ↔ 战斗 循环切换
5. **跨风格进化**：高等级解锁更多动作 / 形态变异

本技能当前已交付可运行的桌面应用模块 **`desktop/`**（自 v1.3 起），把 7.1–7.5 的设计真正落地为一只可在桌面养的圣兽。详见第八节。

---

## 八、桌面养圣兽应用（desktop/ 模块）

把第七节的设计变成真正能跑的桌宠。模块自包含，基于 Python + tkinter（无需额外 GUI 框架）。

### 8.1 目录结构

```
desktop/
├── forms.py            # 三形态纯净 API 提示词构建（build_prompt / 动作关键词）
├── state.py            # 养成本地状态（好感/等级/精力/形态，存 state.json）
├── generator.py        # OpenAI 兼容文生图客户端（可插拔，无 key 优雅降级）
├── shengshou_app.py    # 桌宠主程序（透明置顶/可拖拽/互动/三形态切换）
├── run.py              # 启动入口（自动生成 config.json、检查依赖）
├── config.example.json # API 配置模板
└── assets/             # 运行时生成的神兽图（不入库）
```

### 8.2 安装与运行

```bash
cd desktop
pip install Pillow requests          # 依赖
cp config.example.json config.json   # 首次配置（run.py 也会自动拷贝）
# 按需编辑 config.json：填 api_key 即可自动生图；不填用占位图
python run.py                        # 启动（默认神兽见 config.json）
python run.py --beast 白泽            # 指定神兽
```

### 8.3 操作

| 操作 | 效果 |
|------|------|
| 左键点击 | 随机触发当前形态的一个互动动作，增长好感/精力，弹气泡 |
| 拖拽窗口 | 移动圣兽 |
| 右键菜单「切形态」 | 在已解锁形态间切换（陪伴↔出行↔战斗，消耗精力） |
| 右键菜单「投喂灵果」 | 额外增长好感 |
| 右键菜单「生成三形态图」 | 调 API 补生成三形态图（需已配 key） |
| 右键菜单「状态 / 退出」 | 查看养成数值 / 存档并退出 |

### 8.4 养成规则（MVP 阈值，见 state.py 可调）

- **好感 ≥ 30** 解锁出行形态；**等级 ≥ 5** 解锁战斗形态
- 每次互动 +6 好感 +3 精力 +12 经验；经验满 100 升 1 级
- 形态转化消耗 **20 精力**；精力随真实时间自动回复（约 1 点/分钟）
- 状态存档：`~/.config/shengshou/state.json`

### 8.5 生图 API 配置

`config.json` 的 `api` 段为 OpenAI 兼容接口，支持 `gpt-image-1`（返回 b64）与 `DALL·E 3`（返回 URL）两种返回格式。替换 `base_url` 即可接国内的兼容网关（如通义/硅基等 OpenAI 兼容端点）。未填 key 时 app 用占位图，仍可完整体验养成与互动。

> 注意：运行时 API 用的是「纯净格式」提示词（无 `--ar/--v/--s` 等 MJ 参数），由 `forms.py` 生成；与第四节给人工复制进 MJ 的提示词是两套输出，互不冲突。

## 九、版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-07-21 | 初始版本：国风/萌系/暗黑三风格提示词生成 + 神兽名录（山海经为主+诸子古籍） |
| v1.1 | 2026-07-21 | 细节调整：三版统一为 3D 立体渲染、完整全身（禁局部/裁剪）、纯色/透明抠图友好背景；国风版由 2D 水墨改为 3D 国风数字雕塑 |
| v1.2 | 2026-07-21 | 第二步设计固化：新增第七节「三形态系统」——Q版萌宠=幼兽陪伴 / 国风水墨=出行 / 暗黑史诗=战斗，定义三态循环转化规则与每形态 5 个互动动作（共 15），及动作姿态提示词生成规则、本地状态文件结构 |
| v1.3 | 2026-07-21 | 第三步落地：新增 desktop/ 模块——可运行的桌面养圣兽应用（透明置顶可拖拽、三形态切换、点击互动、基础养成 state.json），首版支持自动调 OpenAI 兼容生图 API（无 key 用占位图）。beasts.json 给九尾狐补 appearance_en |
| v1.4 | 2026-07-21 | 神兽名录 68→108：补貔貅/麒麟/獬豸/龙生九子等 40 只常见神兽；并为全部 108 条补齐 name_en 与 appearance_en，确保桌面养圣兽生图提示词精准对应各神兽外貌 |
| v1.5 | 2026-07-21 | 神兽名录 108→134：补九色鹿/年兽/夕/螭龙/虬龙/蟠龙/蛟/谛听/朝天吼/金翅大鹏/白象/青狮/哮天犬/孰湖/兕/钦原/鹑鸟/冉遗鱼/何罗鱼/鯥/猾褢/獓因/讙/太岁/当扈/鳛鳛鱼 共 26 只（节日文化兽、龙族分支、佛教坐骑与神兽、山海经剩余经典）；全部字段完整、英文名无中文混入 |
