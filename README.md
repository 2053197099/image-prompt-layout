# 图文作品排版 Skill

把筛选好的角色图、场景图与对应提示词排成 **上图、下提示词** 的 PNG 作品集卡片。图片保持完整比例，下方黑底白字，自动换行并按文字长度增高。

## 使用

在可读取此 Skill 的 Codex 聊天中提供原图与对应提示词，然后说：

> 使用 $image-prompt-layout，按顺序把这些图片与提示词排成上图下文的黑底白字 PNG 卡片，保持原图完整和提示词原文。

支持中英文、长参数、横图与竖图；可指定宽度、标签、标题和说明。不指定宽度时保持原图宽度。不生成图片，不自动改写提示词。

## 文件和安装

`SKILL.md` 定义职责与验证，`scripts/render_cards.py` 执行排版，`references/input-format.md` 定义素材清单，`agents/openai.yaml` 提供调用入口。

需要 Python 3.10+、Pillow（见 requirements.txt）与中英文字体。云端推荐 Noto Sans CJK。把仓库放在 `.agents/skills/image-prompt-layout`，或通过环境安装步骤映射到该位置。

角色、场景和选题项目负责创作；本项目只排版筛选好的素材。飞书素材整理项目负责授权读取表格并交接清单。本 Skill 不自动访问飞书或写回表格。

仓库只保存流程与程序，用户作品、提示词素材和飞书凭据不提交；inputs、outputs 和 .env 已排除。
