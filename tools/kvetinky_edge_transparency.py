"""
RGB PNG with black (or dark) frame: make transparent via edge flood-fill,
so interior dark details (eyes, lines) that do not touch the border stay opaque.

Usage:
  python tools/kvetinky_edge_transparency.py [--dry-run] [--lum N]
"""
from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

from PIL import Image


def edge_connected_dark_mask(rgb: Image.Image, lum_thresh: float) -> list[list[bool]]:
    rgb = rgb.convert("RGB")
    w, h = rgb.size
    px = rgb.load()

    def lum(x: int, y: int) -> float:
        r, g, b = px[x, y]
        return (r + g + b) / 3.0

    def dark(x: int, y: int) -> bool:
        return lum(x, y) <= lum_thresh

    seen = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()

    for x in range(w):
        for y in (0, h - 1):
            if dark(x, y):
                seen[y][x] = True
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if not seen[y][x] and dark(x, y):
                seen[y][x] = True
                q.append((x, y))

    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and dark(nx, ny):
                seen[ny][nx] = True
                q.append((nx, ny))

    return seen


def apply_mask_to_rgba(rgb: Image.Image, remove: list[list[bool]]) -> Image.Image:
    rgb = rgb.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    out = Image.new("RGBA", (w, h))
    ox = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if remove[y][x]:
                ox[x, y] = (0, 0, 0, 0)
            else:
                ox[x, y] = (r, g, b, 255)
    return out


def process_file(path: Path, lum_thresh: float, dry_run: bool) -> tuple[bool, str]:
    im = Image.open(path)
    if im.mode == "RGBA":
        extrema = im.split()[3].getextrema()
        if extrema[0] < 255:
            return False, "already has alpha variation; skip"

    mask = edge_connected_dark_mask(im, lum_thresh)
    w, h = im.size
    n_rem = sum(mask[y][x] for y in range(h) for x in range(w))
    frac = n_rem / (w * h)
    if frac > 0.985:
        return False, f"would remove {frac:.1%} — likely wrong; skip"
    if frac < 0.05:
        return False, f"would remove only {frac:.1%} — no dark frame; skip"

    out = apply_mask_to_rgba(im, mask)
    if dry_run:
        return True, f"dry-run ok remove {frac:.1%}"
    out.save(path, optimize=True)
    return True, f"wrote alpha edge-remove {frac:.1%}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--lum", type=float, default=22.0, help="max luminance (0-255) considered background")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    kdir = root / "assets" / "kvetinky"
    if not kdir.is_dir():
        raise SystemExit(f"Missing {kdir}")

    for path in sorted(kdir.glob("*.png")):
        ok, msg = process_file(path, args.lum, args.dry_run)
        print(f"{path.name}: {msg}")


if __name__ == "__main__":
    main()
