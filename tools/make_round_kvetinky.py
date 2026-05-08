from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageChops, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "assets" / "kvetinky"


def bbox_nontransparent(im: Image.Image) -> tuple[int, int, int, int] | None:
    im = im.convert("RGBA")
    a = im.split()[-1]
    # anything with alpha>0
    mask = a.point(lambda v: 255 if v > 0 else 0, mode="L")
    return mask.getbbox()


def make_round_icon(src: Path, dst: Path, *, size: int = 256, pad: float = 0.08) -> None:
    im = Image.open(src).convert("RGBA")
    bb = bbox_nontransparent(im)
    if bb:
        im = im.crop(bb)

    # Square canvas with padding; then fit
    s = max(im.size[0], im.size[1])
    pad_px = int(s * pad)
    canvas = Image.new("RGBA", (s + 2 * pad_px, s + 2 * pad_px), (0, 0, 0, 0))
    x = (canvas.size[0] - im.size[0]) // 2
    y = (canvas.size[1] - im.size[1]) // 2
    canvas.alpha_composite(im, (x, y))

    # Resize to target size
    canvas = canvas.resize((size, size), Image.Resampling.LANCZOS)

    # Circle mask
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size - 1, size - 1), fill=255)

    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(canvas, (0, 0), mask=mask)
    out.save(dst)


def main() -> None:
    if not DIR.exists():
        raise SystemExit(f"Missing directory: {DIR}")

    # Only ones we already generated / replaced
    names: Iterable[str] = [
        "sunny",
        "partly",
        "cloudy",
        "rainy",
        "windy",
        "angry",
    ]
    for n in names:
        p = DIR / f"{n}.png"
        if not p.exists():
            continue
        make_round_icon(p, p, size=256, pad=0.06)
        print("Rounded:", p.name)


if __name__ == "__main__":
    main()

