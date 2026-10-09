"""Compose existing images and exact prompt text into black-footer PNG cards."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


def discover_font(explicit):
    candidates = [explicit] if explicit else [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
    ]
    for name in candidates:
        if name and Path(name).is_file():
            return name
    raise ValueError("缺少中英文字体：安装 Noto Sans CJK 或使用 --font 指定字体")


def wrap_text(text, font, width):
    """Preserve every character, including explicit newlines and parameters."""
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for token in re.findall(r"[A-Za-z0-9_\-]+|[^A-Za-z0-9_\-]", paragraph):
            if current and font.getlength(current + token) > width:
                lines.append(current)
                current = ""
            for char in token:
                if current and font.getlength(current + char) > width:
                    lines.append(current)
                    current = ""
                if font.getlength(char) > width:
                    raise ValueError("文字区过窄，请增大输出宽度")
                current += char
        lines.append(current)
    return lines


def text_block(text, font, width, line_height):
    lines = wrap_text(text, font, width)
    return lines, len(lines) * line_height


def render(item, base, target, width_override, font_name, bold_name):
    path = Path(item["image"])
    path = path if path.is_absolute() else base / path
    if not path.is_file():
        raise ValueError(f"图片不存在：{path}")
    with Image.open(path) as original:
        source = ImageOps.exif_transpose(original).convert("RGBA")
    width = width_override or source.width
    if not 240 <= width <= 8192:
        raise ValueError("输出宽度须在 240–8192 之间；请确认合适的展示尺寸")
    height = max(1, round(source.height * width / source.width))
    if height > 20000:
        raise ValueError("原图过高，请先确认合适的展示宽度")
    if source.size != (width, height):
        source = source.resize((width, height), Image.Resampling.LANCZOS)
    size = max(14, round(width * 0.017))
    heading_size = max(18, round(width * 0.022))
    padding = max(18, round(width * 0.057))
    font = ImageFont.truetype(font_name, size)
    heading = ImageFont.truetype(bold_name or font_name, heading_size)
    line_height = math.ceil(max(size * 1.55, sum(font.getmetrics())))
    heading_height = math.ceil(max(heading_size * 1.5, sum(heading.getmetrics())))
    usable = width - 2 * padding
    blocks = []
    for name in ("title", "description"):
        if item.get(name):
            chosen = heading if name == "title" else font
            lh = heading_height if name == "title" else line_height
            lines, bh = text_block(item[name], chosen, usable, lh)
            blocks.append((lines, chosen, lh, bh))
    label = item.get("label", "prompt")
    label_lines, label_height = text_block(label, heading, usable, heading_height)
    lines, prompt_height = text_block(item["prompt"], font, usable, line_height)
    gap = max(12, round(width * 0.018))
    divider_gap = max(14, round(width * 0.02))
    footer = 2 * padding + sum(b[3] + gap for b in blocks)
    footer += label_height + 2 * divider_gap + prompt_height
    if height + footer > 40000:
        raise ValueError("成品过高，请与用户确认分卡或尺寸，不截断文字")
    canvas = Image.new("RGB", (width, height + footer), "#000000")
    canvas.paste(source, (0, 0), source)
    draw = ImageDraw.Draw(canvas)
    y = height + padding

    def draw_lines(content, chosen, lh):
        nonlocal y
        for line in content:
            draw.text((padding, y), line, fill="#eeeeee", font=chosen, anchor="lt")
            y += lh

    for content, chosen, lh, _ in blocks:
        draw_lines(content, chosen, lh)
        y += gap
    draw_lines(label_lines, heading, heading_height)
    y += divider_gap
    draw.line((padding, y, width - padding, y), fill="#3c3c3c", width=1)
    y += divider_gap
    draw_lines(lines, font, line_height)
    if y > canvas.height - padding:
        raise ValueError("文字超出预期布局，停止输出")
    # Pixel extents can differ from advances: check each line as well.
    for content, chosen in [(lines, font), (label_lines, heading)] + [(b[0], b[1]) for b in blocks]:
        for line in content:
            bbox = chosen.getbbox(line)
            if bbox[2] - bbox[0] > usable + 2:
                raise ValueError("字体字形超出文字区，需调整宽度")
    canvas.save(target, "PNG")
    return {"id": item.get("id"), "image": str(path), "card": target.name,
            "prompt": item["prompt"], "label": label,
            "title": item.get("title"), "description": item.get("description"),
            "width": canvas.width, "height": canvas.height,
            "image_height": height, "prompt_lines": lines,
            "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--width", type=int)
    parser.add_argument("--font")
    parser.add_argument("--bold-font")
    args = parser.parse_args()
    if args.width is not None and not 240 <= args.width <= 8192:
        raise ValueError("输出宽度须在 240–8192 之间")
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items, list) or not items:
        raise ValueError("清单需要非空 items 数组")
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict):
            raise ValueError(f"第 {index} 项必须是对象")
        for field in ("image", "prompt"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"第 {index} 项缺少 {field}")
        for field in ("label", "title", "description"):
            if field in item and not isinstance(item[field], str):
                raise ValueError(f"第 {index} 项的 {field} 必须是字符串")
    font_name = discover_font(args.font)
    if args.bold_font:
        discover_font(args.bold_font)
    targets = [args.output / f"{i:03d}.png" for i in range(1, len(items) + 1)]
    report = args.output / "cards.json"
    if any(p.exists() for p in targets + [report]):
        raise ValueError("输出已存在，请指定新的目录，不覆盖原文件")
    args.output.mkdir(parents=True, exist_ok=True)
    results = [render(item, args.manifest.parent, target, args.width,
                      font_name, args.bold_font) for item, target in zip(items, targets)]
    report.write_text(json.dumps({"cards": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"count": len(results), "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        raise SystemExit(str(error))
