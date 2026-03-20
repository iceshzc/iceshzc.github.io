#!/usr/bin/env python3
"""Remove only edge-connected near-white pixels (common logo matting)."""
from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

from PIL import Image


def knockout_edge_rgba(
    im: Image.Image, thr: int = 245, connect_diagonal: bool = False
) -> Image.Image:
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()

    def near_white(x: int, y: int) -> bool:
        r, g, b, a = px[x, y]
        if a < 12:
            return False
        return r >= thr and g >= thr and b >= thr

    visited = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()

    for x in range(w):
        for y in (0, h - 1):
            if near_white(x, y) and not visited[y][x]:
                visited[y][x] = True
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if near_white(x, y) and not visited[y][x]:
                visited[y][x] = True
                q.append((x, y))

    neigh = [
        (0, 1),
        (0, -1),
        (1, 0),
        (-1, 0),
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1),
    ]
    if not connect_diagonal:
        neigh = neigh[:4]

    while q:
        x, y = q.popleft()
        px[x, y] = (0, 0, 0, 0)
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx]:
                if near_white(nx, ny):
                    visited[ny][nx] = True
                    q.append((nx, ny))
    return im


def process_file(src: Path, dest: Path, thr: int) -> None:
    im = Image.open(src)
    out = knockout_edge_rgba(im, thr=thr)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.suffix.lower() in (".jpg", ".jpeg"):
        dest = dest.with_suffix(".png")
    out.save(dest, optimize=True)


def main() -> None:
    base = Path(__file__).resolve().parents[1] / "images"
    out_dir = base / "partners"
    thr = 245
    if len(sys.argv) > 1:
        thr = int(sys.argv[1])

    mapping = [
        "hkbu_logo.png",
        "sztu_logo.png",
        "cityu.png",
        "jinan_logo.png",
        "tiktok.png",
        "jd_logo.webp",
        "hit_logo.jpeg",
    ]
    for name in mapping:
        src = base / name
        if not src.is_file():
            print(f"skip missing: {src}")
            continue
        dest = out_dir / (Path(name).stem + ".png")
        process_file(src, dest, thr)
        print(f"ok {src.name} -> {dest.relative_to(base.parent)}")


if __name__ == "__main__":
    main()
