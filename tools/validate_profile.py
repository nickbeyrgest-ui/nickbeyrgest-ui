#!/usr/bin/env python3
"""Validate the profile media integration without third-party Python packages.

Checks:
- README uses the static studio title with a mobile variant
- README serves the Saltshore loop with a reduced-motion poster
- the approved Saltshore fog assets are byte-identical
- no scheduled workflow or obsolete contribution graphic remains
- the integration guide matches the live README state
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
DOC = ROOT / "docs" / "profile-media.md"
WORKFLOWS = ROOT / ".github" / "workflows"

FOG_SHA256 = "00dbda07161155c31f13a92f67ffd37f4369c9b74ffbc0c4ce64db2d6d3932df"
POSTER_SHA256 = "d183ca23a89b31f3314b219031796480b404707ce429d0fb5d4fa809810f31b3"

errors: list[str] = []
passes: list[str] = []


def check(condition: bool, label: str, detail: str = "") -> None:
    if condition:
        passes.append(label)
    else:
        errors.append(f"{label}{': ' + detail if detail else ''}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_readme() -> None:
    check(README.is_file(), "README.md exists")
    if not README.is_file():
        return
    raw = README.read_text(encoding="utf-8")

    check("assets/branding/studio-hero.png" in raw, "README.md uses the static studio title")
    check(
        'media="(max-width: 600px)"' in raw
        and "assets/branding/studio-hero-mobile.png" in raw,
        "README.md switches to the mobile title plate up to 600 px",
    )
    check(
        'alt="Marvollo Studio — independent game development"' in raw,
        "README.md title has descriptive alt text",
    )
    check("title-animated.svg" not in raw, "README.md does not use an animated title")

    check("hero-fog.gif" in raw, "README.md uses the cinematic Saltshore loop")
    check(
        'media="(prefers-reduced-motion: reduce)"' in raw
        and "hero-fog-poster.png" in raw,
        "README.md serves a reduced-motion Saltshore poster",
    )
    check("snake" not in raw.lower(), "README.md contains no contribution graphic")
    check("divider.svg" in raw, "README.md still uses the approved divider")

    for reference in re.findall(r'(?:src|srcset)="([^"]+)"', raw):
        for candidate in reference.split(","):
            path = candidate.strip().split(" ")[0]
            if path.startswith(("http://", "https://", "//")):
                continue
            check((ROOT / path).is_file(), f"README.md asset exists: {path}")


def validate_workflow_state() -> None:
    workflows = sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml")) if WORKFLOWS.is_dir() else []
    for path in workflows:
        raw = path.read_text(encoding="utf-8")
        check(
            re.search(r"^\s*schedule:", raw, flags=re.MULTILINE) is None,
            f"workflow has no schedule trigger: {path.name}",
        )
        check("snake" not in raw.lower(), f"workflow contains no contribution graphic: {path.name}")

    check(
        not (WORKFLOWS / "contribution-snake.yml").exists(),
        "the contribution workflow is removed",
    )


def validate_docs() -> None:
    check(DOC.is_file(), "integration guide exists", str(DOC))
    if not DOC.is_file():
        return
    raw = DOC.read_text(encoding="utf-8")
    lower = raw.lower()

    check("snake" not in lower, "guide contains no obsolete contribution instructions")
    check("assets/branding/studio-hero.png" in raw, "guide documents the static title")
    check("assets/branding/studio-hero-mobile.png" in raw, "guide documents the mobile title")
    check("max-width: 600px" in raw, "guide documents the mobile title breakpoint")
    check("title-animated.svg" not in raw, "guide does not document an animated title")
    check("hero-fog.gif" in raw and "hero-fog-poster.png" in raw, "guide documents the cinematic hero and poster")
    check("prefers-reduced-motion: reduce" in raw, "guide documents the reduced-motion hero fallback")

    for alt in re.findall(r'alt="([^"]*)"', raw):
        check(bool(alt.strip()), "documented images have non-empty alt text")

    forbidden = ("shields.io", "github-readme-stats", "github-profile-trophy")
    for token in forbidden:
        check(token not in lower, f"guide does not add stats or badge widgets ({token})")


def validate_preserved_assets() -> None:
    for relative in (
        "assets/saltshore/hero-fog.gif",
        "assets/saltshore/hero-fog-poster.png",
        "assets/branding/studio-hero.png",
        "assets/branding/studio-hero-mobile.png",
        "assets/branding/divider.svg",
        "assets/buttons/website.png",
        "assets/buttons/itch.png",
        "assets/buttons/devlog.png",
        "assets/buttons/discover-saltshore.png",
        "assets/saltshore/hero.png",
        "assets/saltshore/screenshot-01.png",
        "assets/saltshore/screenshot-02.png",
    ):
        check((ROOT / relative).is_file(), f"asset present: {relative}")

    hero_gif = ROOT / "assets" / "saltshore" / "hero-fog.gif"
    if hero_gif.is_file():
        header = hero_gif.read_bytes()[:6]
        check(header in {b"GIF87a", b"GIF89a"}, "Saltshore loop is a GIF", repr(header))
        check(hero_gif.stat().st_size < 5_000_000, "Saltshore loop is under 5 MB", f"{hero_gif.stat().st_size} bytes")
        check(sha256(hero_gif) == FOG_SHA256, "Saltshore loop is byte-identical to the approved asset")

    poster = ROOT / "assets" / "saltshore" / "hero-fog-poster.png"
    if poster.is_file():
        check(poster.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n", "Saltshore poster is a PNG")
        check(sha256(poster) == POSTER_SHA256, "Saltshore poster is byte-identical to the approved asset")


def main() -> int:
    validate_readme()
    validate_workflow_state()
    validate_docs()
    validate_preserved_assets()

    for label in passes:
        print(f"PASS  {label}")
    for error in errors:
        print(f"FAIL  {error}")
    print(f"\n{len(passes)} checks passed, {len(errors)} failed")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
