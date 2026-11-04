import json
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SocialAssetTests(unittest.TestCase):
    def test_og_image_and_metadata(self):
        image = (ROOT / "og-image.png").read_bytes()
        self.assertEqual(image[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", image[16:24]), (1200, 630))

        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('property="og:image" content="https://medi-care-swart.vercel.app/og-image.png"', html)
        self.assertIn('name="twitter:card" content="summary_large_image"', html)

    def test_favicon_and_vercel_allowlist(self):
        icon = (ROOT / "favicon.ico").read_bytes()
        self.assertEqual(struct.unpack("<HHH", icon[:6])[:2], (0, 1))
        self.assertGreaterEqual(struct.unpack("<HHH", icon[:6])[2], 3)

        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/favicon.ico"', html)
        builds = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))["builds"]
        static = {item["src"] for item in builds if item["use"] == "@vercel/static"}
        self.assertTrue({"index.html", "favicon.ico", "og-image.png"}.issubset(static))


if __name__ == "__main__":
    unittest.main()
