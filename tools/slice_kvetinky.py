from __future__ import annotations

from pathlib import Path
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SPRITE = ASSETS / "kvetinka_moods.png"
ANGRY = ASSETS / "kvetinka_angry.png"
OUT_DIR = ASSETS / "kvetinky"


KEYS = [
    "sunny",
    "partly",
    "cloudy",
    "rainy",
    "stormy",
    "windy",
    "snowy",
    "foggy",
]


def bg_from_corners(im: Image.Image) -> tuple[int, int, int]:
    w, h = im.size
    pts = [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]
    acc = [0, 0, 0]
    for x, y in pts:
        r, g, b, _a = im.getpixel((x, y))
        acc[0] += int(r)
        acc[1] += int(g)
        acc[2] += int(b)
    return (acc[0] // len(pts), acc[1] // len(pts), acc[2] // len(pts))


def chroma_key(im: Image.Image, *, fuzz: float = 26.0, feather: float = 12.0) -> Image.Image:
    im = im.copy().convert("RGBA")
    w, h = im.size
    bg = bg_from_corners(im)
    pix = im.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            dr = float(r) - bg[0]
            dg = float(g) - bg[1]
            db = float(b) - bg[2]
            dist = (dr * dr + dg * dg + db * db) ** 0.5
            if dist <= fuzz:
                pix[x, y] = (r, g, b, 0)
            elif dist <= fuzz + feather:
                t = (dist - fuzz) / feather
                pix[x, y] = (r, g, b, max(0, min(255, int(255 * t))))
            else:
                pix[x, y] = (r, g, b, a)
    return im


def main() -> None:
    if not SPRITE.exists():
        raise SystemExit(f"Missing sprite: {SPRITE}")
    if not ANGRY.exists():
        raise SystemExit(f"Missing angry: {ANGRY}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sprite = Image.open(SPRITE).convert("RGBA")
    W, H = sprite.size
    cols, rows = 4, 2
    tw, th = W // cols, H // rows

    for i, key in enumerate(KEYS):
        col = i % cols
        row = i // cols
        sx, sy = col * tw, row * th
        cut_top = int(th * 0.02)
        cut_bottom = int(th * 0.18)
        tile = sprite.crop((sx, sy + cut_top, sx + tw, sy + th - cut_bottom))
        tile = chroma_key(tile)
        tile.save(OUT_DIR / f"{key}.png")

    angry = chroma_key(Image.open(ANGRY).convert("RGBA"))
    angry.save(OUT_DIR / "angry.png")

    print(f"Wrote {len(KEYS) + 1} files to {OUT_DIR}")


if __name__ == "__main__":
    main()

