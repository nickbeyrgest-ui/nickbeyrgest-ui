#!/usr/bin/env python3
"""Validate the profile media additions without third-party Python packages.

Checks:
- animated title SVG is well formed, self-contained, accessible and reduced-motion aware
- brand text contrasts meet WCAG AA for normal text
- contribution-snake workflow is pinned, least-privilege, token-safe and branch-isolated
- integration documentation keeps README.md untouched and avoids badges/stats
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "assets" / "branding" / "title-animated.svg"
WORKFLOW = ROOT / ".github" / "workflows" / "contribution-snake.yml"
DOC = ROOT / "docs" / "profile-media.md"
README = ROOT / "README.md"

SVG_NS = "{http://www.w3.org/2000/svg}"
ALLOWED_ACTIONS = {
    "Platane/snk/svg-only": "d8f6715049803e982ee5ff501b6b9b7d5deeb09b",  # v3.5.0
    "actions/upload-artifact": "cf430e030ddbb5b0abf93d22962f4752f3646cd9",  # v7.0.2
    "crazy-max/ghaction-github-pages": "1d6ee9b181a81033a16bd707a1401afa978daab4",  # v5.0.0
}
FORBIDDEN_ELEMENTS = {
    "script",
    "foreignobject",
    "iframe",
    "object",
    "embed",
    "audio",
    "video",
    "canvas",
}
BRAND = {
    "background": "#151211",
    "surface": "#211B18",
    "text": "#DDD3C5",
    "link": "#C4A477",
    "accent": "#A97155",
    "heading": "#D5B58A",
}

errors: list[str] = []
passes: list[str] = []


def check(condition: bool, label: str, detail: str = "") -> None:
    if condition:
        passes.append(label)
    else:
        errors.append(f"{label}{': ' + detail if detail else ''}")


def srgb(channel: int) -> float:
    value = channel / 255
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def luminance(hex_color: str) -> float:
    value = hex_color.lstrip("#")
    red, green, blue = (int(value[index : index + 2], 16) for index in (0, 2, 4))
    return 0.2126 * srgb(red) + 0.7152 * srgb(green) + 0.0722 * srgb(blue)


def contrast(foreground: str, background: str) -> float:
    first, second = luminance(foreground), luminance(background)
    lighter, darker = max(first, second), min(first, second)
    return (lighter + 0.05) / (darker + 0.05)


def blend(foreground: str, background: str, alpha: float) -> str:
    fg = [int(foreground.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)]
    bg = [int(background.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(alpha * f + (1 - alpha) * b):02x}" for f, b in zip(fg, bg))


def validate_svg() -> None:
    check(SVG.is_file(), "animated title exists", str(SVG))
    if not SVG.is_file():
        return
    raw = SVG.read_text(encoding="utf-8")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        errors.append(f"animated title is well-formed XML: {exc}")
        return
    passes.append("animated title is well-formed XML")

    check(root.tag == f"{SVG_NS}svg", "SVG root is an <svg> element")
    check(bool(root.get("viewBox")), "SVG declares a viewBox")
    check(root.get("role") == "img", "SVG exposes role=img")
    labelled_by = root.get("aria-labelledby", "").split()
    check(len(labelled_by) >= 1, "SVG references aria-labelledby")

    elements = list(root.iter())
    by_id = {element.get("id"): element for element in elements if element.get("id")}
    for element_id in labelled_by:
        element = by_id.get(element_id)
        check(element is not None, f"aria-labelledby target #{element_id} exists")
        if element is not None:
            check((element.text or "").strip() != "", f"#{element_id} has non-empty text")
    check(any(element.tag == f"{SVG_NS}title" for element in elements), "SVG has a <title>")
    check(any(element.tag == f"{SVG_NS}desc" for element in elements), "SVG has a <desc>")
    check(
        sum(1 for element in elements if element.tag == f"{SVG_NS}text") >= 3,
        "SVG title copy is real text, not outlines",
    )

    forbidden_found: list[str] = []
    external_refs: list[str] = []
    event_attributes: list[str] = []
    for element in elements:
        local = element.tag.rsplit("}", 1)[-1].lower()
        if local in FORBIDDEN_ELEMENTS:
            forbidden_found.append(local)
        for attribute, value in element.attrib.items():
            local_attribute = attribute.rsplit("}", 1)[-1].lower()
            if local_attribute.startswith("on"):
                event_attributes.append(local_attribute)
            if local_attribute in {"href", "src"} and not (
                value.startswith("#") or value.startswith("data:")
            ):
                external_refs.append(value[:60])
    check(not forbidden_found, "SVG excludes scripts and embedded documents", ", ".join(forbidden_found))
    check(not event_attributes, "SVG excludes event handler attributes", ", ".join(event_attributes))
    check(not external_refs, "SVG references are local", ", ".join(external_refs))

    check("<style>" in raw, "SVG uses an internal stylesheet")
    check("@keyframes" in raw, "SVG defines animation keyframes")
    check("@import" not in raw, "SVG has no CSS imports")
    check("url(http" not in raw.replace(" ", ""), "SVG has no remote CSS resources")
    check(
        "prefers-reduced-motion: reduce" in raw and "animation: none" in raw,
        "SVG disables motion under prefers-reduced-motion",
    )

    durations = [
        (float(value), unit)
        for value, unit in re.findall(r"animation-duration:\s*(\d+(?:\.\d+)?)(ms|s)", raw)
        + re.findall(r"animation:\s*[A-Za-z-]+\s+(\d+(?:\.\d+)?)(ms|s)", raw)
    ]
    too_fast = []
    for value, unit in durations:
        seconds = value / 1000 if unit == "ms" else value
        if 0 < seconds < 1:
            too_fast.append(f"{value}{unit}")
    check(not too_fast, "SVG animations stay at or below 1 Hz", ", ".join(too_fast))

    check(SVG.stat().st_size < 100_000, "SVG is under 100 KB", f"{SVG.stat().st_size} bytes")
    check(BRAND["heading"] in raw, "SVG uses the brand heading colour")
    check(BRAND["link"] in raw, "SVG uses the brand link colour")
    check(BRAND["text"] in raw, "SVG uses the brand text colour")
    check(BRAND["background"] in raw, "SVG uses the brand background colour")

    pairs = [
        ("wordmark", BRAND["heading"], 4.5),
        ("subtitle", BRAND["link"], 4.5),
        ("body/tagline", BRAND["text"], 4.5),
        ("tagline at 78%", blend(BRAND["text"], BRAND["background"], 0.78), 4.5),
        ("ornament", BRAND["accent"], 3.0),
    ]
    for label, foreground, threshold in pairs:
        ratio = contrast(foreground, BRAND["background"])
        check(ratio >= threshold, f"{label} contrast >= {threshold}:1", f"{ratio:.2f}:1")


def validate_workflow() -> None:
    check(WORKFLOW.is_file(), "contribution snake workflow exists", str(WORKFLOW))
    if not WORKFLOW.is_file():
        return
    raw = WORKFLOW.read_text(encoding="utf-8")
    lines = raw.splitlines()

    uses = re.findall(r"^\s*-?\s*uses:\s*(\S+)", raw, flags=re.MULTILINE)
    check(bool(uses), "workflow declares actions")
    for reference in uses:
        action, _, version = reference.partition("@")
        check(bool(re.fullmatch(r"[0-9a-f]{40}", version)), f"{action} is pinned to a full commit SHA", version)
        check(action in ALLOWED_ACTIONS, f"{action} is an allow-listed trusted action")
        if action in ALLOWED_ACTIONS:
            check(version == ALLOWED_ACTIONS[action], f"{action} matches the reviewed SHA", version)

    check("write-all" not in raw, "workflow does not request write-all")
    check("pull_request_target" not in raw, "workflow does not use pull_request_target")
    check(not re.search(r"^\s*(push|pull_request):", raw, flags=re.MULTILINE), "workflow does not publish on arbitrary pushes")
    check(re.search(r"^\s*workflow_dispatch:", raw, flags=re.MULTILINE) is not None, "workflow supports manual dispatch")
    check(re.search(r"^\s*schedule:", raw, flags=re.MULTILINE) is not None, "workflow supports a scheduled refresh")
    check(re.search(r"^\s*concurrency:", raw, flags=re.MULTILINE) is not None, "workflow serialises runs")
    check(re.search(r"^\s*timeout-minutes:\s*\d+", raw, flags=re.MULTILINE) is not None, "workflow sets a job timeout")
    check("runs-on: ubuntu-latest" in raw, "workflow uses a GitHub-hosted Ubuntu runner")
    check("target_branch: snake-output" in raw, "workflow publishes to the isolated snake-output branch")
    check(not re.search(r"target_branch:\s*(main|master|gh-pages)\b", raw), "workflow never targets a primary branch")
    check("keep_history: false" in raw, "output branch is rebuilt, not appended")
    check("allow_empty_commit: false" in raw, "workflow avoids empty commits")
    check("dry_run: ${{ inputs.dry_run == true }}" in raw, "manual runs default to a non-publishing dry run")
    check("default: true" in raw, "manual dispatch defaults to dry_run=true")
    check("contents: write" in raw, "workflow requests only contents: write")
    check(not re.search(r"^\s+(actions|checks|deployments|id-token|issues|packages|pages|security-events|statuses):\s*write", raw, flags=re.MULTILINE), "workflow does not request unrelated write scopes")

    secret_refs = set(re.findall(r"secrets\.([A-Za-z0-9_]+)", raw))
    check(secret_refs <= {"GITHUB_TOKEN"}, "workflow uses only the built-in GITHUB_TOKEN", ", ".join(sorted(secret_refs)))
    check(not re.search(r"\b(PAT|GH_PAT|PERSONAL_ACCESS_TOKEN|WORKFLOW_TOKEN)\b", raw), "workflow does not reference a PAT")

    check("palette=github-light" in raw and "palette=github-dark" in raw, "workflow generates light and dark palettes")
    check("snake-light.svg" in raw and "snake-dark.svg" in raw, "workflow generates two theme-specific SVGs")
    check("%23A97155" in raw and "%23C4A477" in raw, "snake colours are brand-encoded in the query string")

    check(raw.count("${{") == raw.count("}}"), "workflow expressions are balanced")
    check(not any(line.lstrip().startswith("\t") for line in lines), "workflow indentation uses spaces")


def validate_docs() -> None:
    check(DOC.is_file(), "integration guide exists", str(DOC))
    if not DOC.is_file():
        return
    raw = DOC.read_text(encoding="utf-8")
    check("<picture>" in raw and "</picture>" in raw, "guide provides a responsive snake snippet")
    check("prefers-color-scheme: dark" in raw and "prefers-color-scheme: light" in raw, "guide selects a snake per colour scheme")
    check("title-animated.svg" in raw, "guide references the animated title")
    check("assets/branding/studio-hero.png" in raw, "guide preserves the existing approved hero")
    check("snake-output" in raw, "guide uses the isolated output branch")
    check("dry_run" in raw, "guide documents the non-publishing run")
    check("GITHUB_TOKEN" in raw, "guide documents the built-in token")
    check("no pat" in raw.lower() or "without a pat" in raw.lower(), "guide states that no PAT is used")
    for alt in re.findall(r"alt=\"([^\"]*)\"", raw):
        check(bool(alt.strip()), "documented images have non-empty alt text")
    forbidden = ("shields.io", "github-readme-stats", "github-profile-trophy")
    for token in forbidden:
        check(token not in raw.lower(), f"guide does not add stats or badge widgets ({token})")

    check(README.is_file(), "README.md exists")
    if README.is_file():
        readme = README.read_text(encoding="utf-8")
        check("title-animated.svg" not in readme, "README.md is not integrated yet")
        check("snake-output" not in readme, "README.md does not reference the snake output branch yet")
        check("assets/branding/studio-hero.png" in readme, "README.md still uses the approved hero")
        check("divider.svg" in readme, "README.md still uses the approved divider")


def validate_preserved_assets() -> None:
    for relative in (
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
        check((ROOT / relative).is_file(), f"existing asset preserved: {relative}")


def main() -> int:
    validate_svg()
    validate_workflow()
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
