#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

MAX_BYTES = 500 * 1024
HERO_WIDTH = 1600
NORMAL_WIDTH = 800

ROOT = Path(__file__).resolve().parent
IMAGES_DIR = ROOT / "images"


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return result.stdout


def get_dimensions(path: Path) -> tuple[int, int]:
    out = run(["/usr/bin/sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)])
    width_match = re.search(r"pixelWidth:\s+(\d+)", out)
    height_match = re.search(r"pixelHeight:\s+(\d+)", out)
    if not width_match or not height_match:
        raise RuntimeError(f"Failed to read dimensions for {path}")
    return int(width_match.group(1)), int(height_match.group(1))


def target_width_for(name: str) -> int:
    return HERO_WIDTH if "hero" in name.lower() else NORMAL_WIDTH


def convert_image(src: Path, dst: Path, target_w: int, target_h: int) -> None:
    quality = 85
    tmp_dir = Path(tempfile.mkdtemp(prefix="imgopt_"))
    tmp_file = tmp_dir / f"{dst.stem}.jpg"
    try:
        while True:
            run(
                [
                    "/usr/bin/sips",
                    "-s",
                    "format",
                    "jpeg",
                    "-s",
                    "formatOptions",
                    str(quality),
                    "-z",
                    str(target_h),
                    str(target_w),
                    str(src),
                    "--out",
                    str(tmp_file),
                ]
            )
            size = tmp_file.stat().st_size
            if size <= MAX_BYTES or quality <= 55:
                break
            quality -= 5
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_file), str(dst))
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def main() -> None:
    if not IMAGES_DIR.exists():
        raise SystemExit(f"Missing images directory: {IMAGES_DIR}")

    for path in sorted(IMAGES_DIR.iterdir()):
        if path.is_dir():
            continue
        if path.name.startswith("."):
            continue

        ext = path.suffix.lower()
        if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue

        name = path.stem
        target_w = target_width_for(path.name)
        width, height = get_dimensions(path)
        if width <= target_w:
            target_w = width
            target_h = height
        else:
            target_h = max(1, round(height * (target_w / width)))

        dst = path.with_suffix(".jpg")
        needs_convert = True
        if ext in {".jpg", ".jpeg"} and dst == path:
            size = path.stat().st_size
            needs_convert = width > target_w or size > MAX_BYTES

        if not needs_convert:
            continue

        convert_image(path, dst, target_w, target_h)

        if path != dst:
            try:
                path.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    main()
