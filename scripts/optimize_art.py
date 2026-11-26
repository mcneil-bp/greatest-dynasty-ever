#!/usr/bin/env python3
"""Resize official manager portraits to web-ready webp (~100–200 KB).

Usage: python3 scripts/optimize_art.py <source-folder>
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "art" / "managers"


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/optimize_art.py <source-folder>", file=sys.stderr)
        return 2
    src = Path(sys.argv[1])
    if not src.exists():
        print(f"Source folder not found: {src}", file=sys.stderr)
        return 1
    DST.mkdir(parents=True, exist_ok=True)
    files = sorted(src.glob("*.png")) + sorted(src.glob("*.jpg")) + sorted(src.glob("*.jpeg")) + sorted(src.glob("*.webp"))
    if not files:
        print(f"No images in {src}", file=sys.stderr)
        return 1
    for f in files:
        im = Image.open(f).convert("RGB")
        im.thumbnail((720, 960), Image.Resampling.LANCZOS)
        out = DST / (f.stem + ".webp")
        im.save(out, "WEBP", quality=82, method=6)
        print(f"{out.name:40} {im.size[0]}x{im.size[1]}  {out.stat().st_size/1024:.1f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
