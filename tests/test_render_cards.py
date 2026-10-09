import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageFont

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/render_cards.py"
spec = importlib.util.spec_from_file_location("render_cards", SCRIPT)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class CardTests(unittest.TestCase):
    def test_wrap_keeps_words_parameters_and_chinese(self):
        font = ImageFont.truetype(renderer.discover_font(None), 20)
        text = "月夜山道，一束侧光。 Exact prompt --ar 3:4 --style raw " + "a" * 80
        lines = renderer.wrap_text(text, font, 200)
        self.assertEqual("".join(lines), text)
        self.assertTrue(all(font.getlength(line) <= 200 for line in lines))

    def test_batch_aspect_ratio_and_exact_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            items = []
            for index, size in enumerate(((960, 540), (600, 800))):
                image = root / f"source-{index}.png"
                Image.new("RGB", size, "#153e54").save(image)
                items.append({"id": f"record-{index}", "image": image.name,
                              "prompt": "东方山水，英文参数保留。\n" + "Exact original prompt --ar 3:4 " * 20})
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"items": items}, ensure_ascii=False))
            output = root / "cards"
            command = [sys.executable, str(SCRIPT), str(manifest), "--output", str(output), "--width", "800"]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            cards = json.loads((output / "cards.json").read_text())["cards"]
            for index, card in enumerate(cards):
                self.assertEqual(card["prompt"], items[index]["prompt"])
                self.assertEqual(card["id"], items[index]["id"])
                with Image.open(output / card["card"]) as rendered:
                    self.assertEqual(rendered.width, 800)
                    self.assertGreater(rendered.height, card["image_height"])
                    self.assertEqual(rendered.getpixel((0, 0)), (21, 62, 84))
                    self.assertEqual(rendered.getpixel((0, rendered.height - 1)), (0, 0, 0))
                self.assertEqual(card["image_height"], round(((540 / 960) if index == 0 else (800 / 600)) * 800))
            before = (output / "001.png").read_bytes()
            repeat = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(repeat.returncode, 0)
            self.assertEqual(before, (output / "001.png").read_bytes())

    def test_missing_prompt_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "bad.json"
            source.write_text('{"items":[{"image":"none.png","prompt":""}]}')
            result = subprocess.run([sys.executable, str(SCRIPT), str(source), "--output", str(root / "out")], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / "out").exists())


if __name__ == "__main__":
    unittest.main()
