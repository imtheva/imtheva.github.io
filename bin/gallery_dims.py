#!/usr/bin/env python3
"""Fill in width/height for every entry in _data/gallery.yml.

The gallery page uses each photo's aspect ratio to build justified rows,
so portrait and landscape photos line up without cropping.
Run from the repo root after adding photos:  python3 bin/gallery_dims.py
Needs Pillow (pip install pillow). Respects EXIF rotation.
"""
import re
import sys
from pathlib import Path

from PIL import Image

DATA = Path("_data/gallery.yml")


def display_size(path):
    with Image.open(path) as im:
        w, h = im.size
        if im.getexif().get(274, 1) in (5, 6, 7, 8):  # rotated 90/270
            w, h = h, w
    return w, h


def main():
    out, missing = [], []
    for line in DATA.read_text().splitlines(keepends=True):
        if re.match(r"\s+(width|height):", line):
            continue  # drop old values; regenerated below
        out.append(line)
        m = re.match(r"(\s+)path:\s*['\"]?([^'\"\n#]+?)['\"]?\s*(#.*)?$", line)
        if m:
            indent, img = m.group(1), m.group(2).strip()
            if Path(img).exists():
                w, h = display_size(img)
                out.append(f"{indent}width: {w}\n{indent}height: {h}\n")
            else:
                missing.append(img)
    DATA.write_text("".join(out))
    if missing:
        print("Missing images:", *missing, sep="\n  ")
        sys.exit(1)
    print("gallery.yml updated")


if __name__ == "__main__":
    main()
