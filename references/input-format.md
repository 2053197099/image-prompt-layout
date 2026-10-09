# 输入和运行

输入为 UTF-8 JSON 对象，`items` 每项对应一张图片与原始提示词。路径相对清单文件。不放入登录凭据或 API 密钥。

```json
{"items":[{"id":"record-001","image":"images/001.png","prompt":"原始提示词 --ar 3:4 --style raw","label":"prompt","title":"可选作品名","description":"可选说明"}]}
```

```bash
python scripts/render_cards.py manifest.json --output outputs/cards
```

可选：`--width 1220`（统一宽度，默认原图宽度）、`--font /path/cjk.ttf`、`--bold-font /path/bold.ttf`。透明原图放在黑底，EXIF 方向按正常观看方向处理。标签默认 prompt，可按条目覆盖；标题、说明和提示词都在图片下面。

输出 `001.png` 等卡片及 `cards.json` 配对清单。存在输出文件时停止，不覆盖。空提示词、图片缺失、非法尺寸或字体不可用时明确报错。文字区按长度增高，不截断；超大素材先确认展示尺寸。

飞书素材整理流程须把用户授权且已选择的记录转换为此结构，图片下载到当前任务可读路径。链接、附件 token 不能直接当图片路径。一行多附件须先确认对应关系，不静默复制或猜测。
