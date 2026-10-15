# 图文作品排版 Skill

把已筛选好的原图与对应原始提示词，排成**上方完整图片、下方黑底白字提示词**的 PNG 作品集卡片。每图一张，横图和竖图保持比例；文字区随长度增高。

适合在角色图、场景图完成出图并筛选之后使用。这个 Skill 负责图文排版，使用 Python/Pillow 确定性渲染；不生成替代图片、不改写提示词，也不提供书法标题生成或从画面取色设计文字的功能。

## 能做什么

- 批量处理横图、竖图，一张原图对应一张 PNG。
- 完整展示原图；默认保持原图宽度，指定统一宽度时等比例缩放。
- 中文自然换行，英文优先按词换行；保留原始中英文、标点、参数与显式换行。
- 下方使用黑底、浅白正文、左对齐和细灰分隔线；文字变长时增加高度。
- 自定义输出宽度、提示词标签、标题和说明；标题和说明在用户提供或要求时才加入，放在图下。
- 输出卡片、保留原始提示词与记录 ID 的配对清单，便于核对来源和顺序。

## 先准备什么

| 输入 | 要求 |
| --- | --- |
| 原图 | 上传到当前聊天，或交接当前任务确实可读的图片文件 |
| 原始提示词 | 每张图片明确对应一段文字，完整保留参数 |
| 稳定记录 ID | 建议每项提供独立 ID，例如 `record-001`，交付时保留 |
| 顺序 | 以用户确认的顺序处理，不按画面内容猜测 |
| 可选版式要求 | 宽度、标签、标题、说明；未指定时沿用默认版式 |

云环境不能直接读取你电脑上的 `/Users/...` 路径。其他聊天的附件也不保证迁移，需要重新上传或明确交接可访问的素材包。只有参考截图、缺少原图时，应先补原图；一行多个附件或缺少提示词时先确认配对，不自动复制或猜文本。

## 在 Codex 聊天中怎么用

先确保本 Skill 已安装或当前环境已配置入口，再上传原图与清单。可以直接复制：

```text
使用 $image-prompt-layout，按清单中已确认的顺序和记录 ID，把这些原图与对应提示词排成上图下文的 PNG。保持原图完整，不改写提示词，每图一张。
```

需要统一宽度与标签时：

```text
使用 $image-prompt-layout，输出宽度统一为 1220 像素，标签改为 MJ Prompt。标题和说明只使用清单中提供的文字。保留原图比例和全部原始提示词。
```

只有一张图时，也可以直接上传图片并写明记录 ID、原始提示词和可选标题，无需手工编写 JSON；批量交接建议采用下面的清单格式。

## 批量素材清单

用 UTF-8 JSON 保存，路径相对清单文件；`items` 中的排列顺序就是渲染顺序：

```json
{
  "items": [
    {
      "id": "record-001",
      "image": "images/001.png",
      "prompt": "此处粘贴第一张图片的完整原始提示词 --ar 3:4 --style raw",
      "label": "prompt"
    },
    {
      "id": "record-002",
      "image": "images/002.jpg",
      "prompt": "此处粘贴第二张图片的完整原始提示词",
      "label": "MJ Prompt",
      "title": "用户提供的作品名",
      "description": "用户提供的说明"
    }
  ]
}
```

`image`、`prompt` 必填；`id` 建议提供，`label` 默认是 `prompt`，`title`、`description` 可省略。示例中的文字是占位说明，实际使用时替换为你的原文。`image` 需要本任务可读的文件路径，网页链接、飞书附件 token 不能直接代入。

完整格式见 [输入和运行说明](references/input-format.md)。

## 安装和命令行运行

需要 Python 3.10+、[requirements.txt](requirements.txt) 中的 Pillow，以及中英文字体。推荐安装 Noto Sans CJK；常规和粗体也可以分别指定字体文件。字体参考图片不能代替 TTF、OTF 或 TTC 等可加载字体文件。

项目级安装：在目标项目根目录执行；同名目录已存在时先检查，不覆盖已有安装。

```bash
mkdir -p .agents/skills
git clone https://github.com/2053197099/image-prompt-layout.git .agents/skills/image-prompt-layout
cd .agents/skills/image-prompt-layout
python -m pip install -r requirements.txt
```

安装后在新聊天中确认 Skill 可用，再调用 `$image-prompt-layout`；也可明确让 Codex 读取安装位置的 `SKILL.md`。已有入口的云环境可以直接使用。更新 GitHub 文档不会自动重新发布云环境。

以下命令在仓库根目录运行；`/path/to/input/manifest.json` 和输出目录均应替换为实际路径：

```bash
python scripts/render_cards.py /path/to/input/manifest.json --output /path/to/output/cards
```

指定统一宽度与字体的示例：

```bash
python scripts/render_cards.py /path/to/input/manifest.json \
  --output /path/to/output/cards-1220 \
  --width 1220 \
  --font /path/to/NotoSansCJK-Regular.ttc \
  --bold-font /path/to/NotoSansCJK-Bold.ttc
```

未传 `--width` 时保持每张原图宽度；标签、标题与说明写在清单各项中。透明图片铺在黑底上，EXIF 方向按正常观看方向处理。

## 输出和检查

输出目录包含：

```text
cards/
├── 001.png       第一项的上图下文卡片
├── 002.png       第二项的上图下文卡片
└── cards.json    图片路径、原始提示词、记录 ID 与卡片信息
```

输出文件已存在时停止，不覆盖。缺提示词、图片不可读、字体不可用或尺寸非法时明确报错。长文本自动增高；超大素材需要先确认展示尺寸，不通过删字、裁图或压小字体强行塞进固定高度。

首次使用或更改版式时，检查代表性横图、竖图和长文本成品；每批核对顺序、配对、参数、字形、原图比例、边距及溢出。仓库现有三项测试覆盖文字与参数保留、横竖比例及配对、缺提示词拒绝输出，并验证不覆盖已有卡片：

```bash
python -m unittest discover -s tests -v
```

交付时逐张提供 PNG、配对清单和可复制原文；批量可另打 ZIP。**生成成功和聊天可下载是两件事**：实际附件或下载链接取决于所用客户端和云环境的导出能力。没有导出能力时要如实说明，不能把云端文件路径当作用户可下载链接；图片预览的保存按钮以客户端实际提供为准。

## 在东方图库流程中的位置

| 你现在要做什么 | 使用的 Skill | 得到什么 |
| --- | --- | --- |
| 还没确定题材，先找方向 | [东方风格选题](https://github.com/2053197099/oriental-style-topic-selection) | 候选题材；选定后给出简短世界观、角色与场景方向 |
| 已有题材，要设计角色 | [东方题材角色](https://github.com/2053197099/midjourney-oriental-game-characters) | 原创角色的中英文 Midjourney 提示词 |
| 已有题材，要设计环境 | [东方题材场景](https://github.com/2053197099/midjourney-wuxia-environments) | 纯环境场景的中英文 Midjourney 提示词 |
| 已有筛选好的原图和提示词 | [图文作品排版](https://github.com/2053197099/image-prompt-layout) | 每张原图一张上图下文 PNG，以及图片与提示词配对清单 |

四个 Skill 可以单独使用，不必从选题开始。角色与场景 Skill 的交付是提示词文本；实际出图需在你使用的图像生成工具中完成。跨聊天继续时，请主动复制已确认的世界观、方向或提示词，并上传对应原图与清单；共用环境不表示任务素材自动共享。飞书整理需另行授权与连接，这四个 Skill 不会自动访问飞书或向其他聊天发消息。

## 职责边界与项目文件

不自动裁图、变形、去水印、调色、补写提示词或把参考截图当作原图；不默认增加封面、总览长图、标题、说明或书法字效果。飞书整理属于独立流程，需要授权读取和显式交接图片及清单；本 Skill 不连接飞书、不写回表格、不发布外部网页。

| 文件 | 用途 |
| --- | --- |
| [SKILL.md](SKILL.md) | 运行时职责、版式、验证和交付规则 |
| [agents/openai.yaml](agents/openai.yaml) | 展示名称、简介和默认调用语 |
| [references/input-format.md](references/input-format.md) | 素材清单与运行格式 |
| [scripts/render_cards.py](scripts/render_cards.py) | PNG 排版程序 |
| [tests/test_render_cards.py](tests/test_render_cards.py) | 三项自动测试 |
| [requirements.txt](requirements.txt) | Python 依赖 |

仓库保存流程、程序与文档。用户原图、原始提示词素材、参考包和凭据应保存在任务目录中，不提交到仓库。普通排版不执行 Git 操作；只有明确维护或同步仓库时才更新项目。
