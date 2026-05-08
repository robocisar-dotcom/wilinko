import os
from collections import deque

from PIL import Image


DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets", "kvetinky"))
TOL = 18  # tolerance for "near black" in background


def near_black(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    return r <= TOL and g <= TOL and b <= TOL


def process_png(path: str) -> bool:
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()

    visited = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()

    def push(x: int, y: int) -> None:
        if 0 <= x < w and 0 <= y < h and not visited[y][x]:
            visited[y][x] = True
            q.append((x, y))

    # Seeds from edges only
    for x in range(w):
        push(x, 0)
        push(x, h - 1)
    for y in range(h):
        push(0, y)
        push(w - 1, y)

    bg = set()
    while q:
        x, y = q.popleft()
        r, g, b, a = px[x, y]
        if a == 0:
            bg.add((x, y))
            continue
        if near_black((r, g, b)):
            bg.add((x, y))
            push(x + 1, y)
            push(x - 1, y)
            push(x, y + 1)
            push(x, y - 1)

    if not bg:
        return False

    for x, y in bg:
        r, g, b, _a = px[x, y]
        px[x, y] = (r, g, b, 0)

    # soften jaggies: near-black halo pixels next to bg -> transparent
    halo = []
    for x, y in bg:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h:
                    continue
                if (nx, ny) in bg:
                    continue
                r, g, b, a = px[nx, ny]
                if a != 0 and near_black((r, g, b)):
                    halo.append((nx, ny))
    for nx, ny in halo:
        r, g, b, _a = px[nx, ny]
        px[nx, ny] = (r, g, b, 0)

    im.save(path)
    return True


def main() -> int:
    if not os.path.isdir(DIR):
        print(f"Missing directory: {DIR}")
        return 2

    changed = 0
    failed = 0
    for fn in sorted(os.listdir(DIR)):
        if not fn.lower().endswith(".png"):
            continue
        path = os.path.join(DIR, fn)
        try:
            if process_png(path):
                changed += 1
                print("processed", fn)
        except Exception as e:
            failed += 1
            print("FAILED", fn, e)

    print("done. files processed:", changed, "failed:", failed)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

