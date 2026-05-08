import os
from collections import deque

from PIL import Image, ImageDraw, ImageFont


ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "assets", "kvetinky")


def color_dist(a, b) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def flood_clear_to_transparent(path: str, tol: int = 40) -> None:
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()

    # Estimate background color from corners (average)
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    bg = [0, 0, 0]
    for x, y in corners:
        r, g, b, _a = px[x, y]
        bg[0] += r
        bg[1] += g
        bg[2] += b
    bg = (bg[0] // 4, bg[1] // 4, bg[2] // 4)

    visited = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()

    def push(x: int, y: int) -> None:
        if 0 <= x < w and 0 <= y < h and not visited[y][x]:
            visited[y][x] = True
            q.append((x, y))

    # seed from borders
    for x in range(w):
        push(x, 0)
        push(x, h - 1)
    for y in range(h):
        push(0, y)
        push(w - 1, y)

    clear = set()
    while q:
        x, y = q.popleft()
        r, g, b, a = px[x, y]
        if a == 0:
            clear.add((x, y))
            continue
        if color_dist((r, g, b), bg) <= tol:
            clear.add((x, y))
            push(x + 1, y)
            push(x - 1, y)
            push(x, y + 1)
            push(x, y - 1)

    for x, y in clear:
        r, g, b, _a = px[x, y]
        px[x, y] = (r, g, b, 0)

    im.save(path)


def make_attention_icon(out_path: str, base_path: str) -> None:
    base = Image.open(base_path).convert("RGBA")
    # crop around center to square
    w, h = base.size
    s = min(w, h)
    left = (w - s) // 2
    top = (h - s) // 2
    base_sq = base.crop((left, top, left + s, top + s))

    canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    flower = base_sq.resize((420, 420), Image.LANCZOS)
    canvas.alpha_composite(flower, (46, 72))

    # badge
    draw = ImageDraw.Draw(canvas)
    bx, by, br = 400, 82, 56
    draw.ellipse((bx - br, by - br, bx + br, by + br), fill=(251, 191, 36, 255), outline=(255, 255, 255, 220), width=6)
    draw.ellipse((bx - br + 10, by - br + 10, bx + br - 10, by + br - 10), fill=(245, 158, 11, 255))

    # exclamation mark
    try:
        font = ImageFont.truetype("arialbd.ttf", 72)
    except Exception:
        font = ImageFont.load_default()
    text = "!"
    tw, th = draw.textbbox((0, 0), text, font=font)[2:]
    draw.text((bx - tw / 2, by - th / 2 - 6), text, fill=(15, 23, 42, 255), font=font)

    canvas.save(out_path)


def main() -> int:
    angry = os.path.join(DIR, "nahnevany.png")
    if os.path.isfile(angry):
        flood_clear_to_transparent(angry, tol=55)
        print("fixed nahnevany.png background")

    # rebuild flora-pozornost as a clean transparent icon
    out = os.path.join(DIR, "flora-pozornost.png")
    if os.path.isfile(angry):
        make_attention_icon(out, angry)
        print("rebuilt flora-pozornost.png icon")
    else:
        print("missing nahnevany.png, cannot rebuild flora-pozornost.png")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

