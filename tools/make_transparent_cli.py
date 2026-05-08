from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


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


def chroma_key(im: Image.Image, *, fuzz: float, feather: float) -> Image.Image:
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="Source PNG path")
    ap.add_argument("--dst", required=True, help="Destination PNG path")
    ap.add_argument("--fuzz", type=float, default=40.0, help="Color distance threshold")
    ap.add_argument("--feather", type=float, default=18.0, help="Alpha feather range")
    args = ap.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)
    if not src.exists():
        raise SystemExit(f"Missing: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)

    im = Image.open(src)
    out = chroma_key(im, fuzz=float(args.fuzz), feather=float(args.feather))
    out.save(dst)
    print(f"Wrote {dst}")


if __name__ == "__main__":
    main()

