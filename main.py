#!/usr/bin/env python3
"""Entry point: write the passport spread image to /output/entry.png.

The image is a pre-rendered asset (entry.png, built by build_spread.py
from a generated ID portrait composited into a code-drawn two-page
passport spread for the invented Republic of Velmora). This program
copies it byte-for-byte: deterministic, no network, no randomness.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET = os.path.join(HERE, "entry.png")
OUT = "/output/entry.png"


def main():
    if not os.path.isfile(ASSET):
        sys.exit("missing asset: entry.png")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    shutil.copyfile(ASSET, OUT)
    size = os.path.getsize(OUT)
    if size > 1_048_576:
        sys.exit(f"entry.png too large: {size} bytes")
    print(f"wrote {OUT} ({size} bytes)")


if __name__ == "__main__":
    main()
