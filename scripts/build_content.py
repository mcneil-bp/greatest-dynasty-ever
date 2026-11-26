#!/usr/bin/env python3
"""Compile content/art.json and content/story.json into js/data-content.js."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = """\
/* ===== Art and story registries. Empty for now: every missing key renders as a slot. =====
   ART keys:   "w10/cover", "w10/m1".."w10/m5", "w10/film", "team/3"        -> file path beside this page
   STORY keys: "w10/headline", "w10/intro", "w10/m1/title", "w10/m1/recap",
               "team/3/avatar|origin|arc|nemesis", "rivalry/4-5/name"       -> text */
"""


def main() -> int:
    art = json.loads((ROOT / "content" / "art.json").read_text())
    story = json.loads((ROOT / "content" / "story.json").read_text())
    out = (
        HEADER
        + "const ART = "
        + json.dumps(art, ensure_ascii=False, separators=(",", ":"))
        + ";\n\nconst STORY = "
        + json.dumps(story, ensure_ascii=False, separators=(",", ":"))
        + ";\n"
    )
    dest = ROOT / "js" / "data-content.js"
    dest.write_text(out)
    print(f"wrote {dest.relative_to(ROOT)}  ({len(art)} art keys, {len(story)} story keys)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
