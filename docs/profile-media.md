# Profile media integration

Status: **prepared, not integrated**. `README.md` is intentionally unchanged. The
existing approved hero, buttons, screenshots and divider are preserved. The
contribution-snake workflow is committed but has not been run, and the
`snake-output` branch does not exist yet.

Owner approval is required before the first non-dry workflow run and before the
README snippets below are applied.

## 1. Animated studio title

Asset: `assets/branding/title-animated.svg` (1600 × 400, under 8 KB).

The plate uses the approved studio palette: heading `#D5B58A`, link `#C4A477`,
text `#DDD3C5` and background `#151211`. The cold moon, sea haze and drifting
mist are supporting neutrals in the Saltshore direction. The wordmark is real
text, not outlines. Cinzel and Lora are used when installed; Georgia/Times/serif
is the documented fallback because a GitHub README cannot load webfonts.

Motion is restrained: a single pale-gold sweep across the wordmark, drawn corner
rules, a slow moon pulse and drifting mist. `prefers-reduced-motion: reduce`
removes every animation and leaves a complete static plate. At viewport widths
up to 600 px the SVG hides the small tagline inside the image; the README copy
below the title already carries that line, so the wordmark and STUDIO stay
legible on a phone.

### Snippet

```html
<div align="center">
  <img src="assets/branding/title-animated.svg" alt="Marvollo Studio — independent game development" width="100%">
</div>
```

### Where it goes

Use it as the single profile title, replacing the static hero `<picture>` block
only after owner approval:

```html
<!-- Current block in README.md, kept until integration is approved. -->
<picture>
  <source media="(max-width: 600px)" srcset="assets/branding/studio-hero-mobile.png">
  <img src="assets/branding/studio-hero.png" alt="Marvollo Studio - independent game development" width="100%">
</picture>
```

Do **not** keep both the animated title and the static hero: the profile would
show the wordmark twice. Keep `assets/branding/studio-hero.png` and
`assets/branding/studio-hero-mobile.png` in the repository for rollback.

## 2. Contribution snake

Workflow: `.github/workflows/contribution-snake.yml`.

| Control | Value |
|---|---|
| Generator | `Platane/snk/svg-only` v3.5.0, pinned to `d8f6715049803e982ee5ff501b6b9b7d5deeb09b` |
| Publisher | `crazy-max/ghaction-github-pages` v5.0.0, pinned to `1d6ee9b181a81033a16bd707a1401afa978daab4` |
| Artifact | `actions/upload-artifact` v7.0.2, pinned to `cf430e030ddbb5b0abf93d22962f4752f3646cd9` |
| Token | Built-in `GITHUB_TOKEN` only. No PAT, no repository secret. |
| Permissions | `permissions: {}` at workflow level; job gets `contents: write` only |
| Output | Isolated `snake-output` branch, force-rebuilt; never `main` |
| Triggers | Daily `schedule` plus `workflow_dispatch` |
| Manual safety | `dry_run` defaults to `true`, so a manual run uploads artifacts without publishing |
| Palette | `github-light` and `github-dark`, with muted cold dots and copper/gold snake |

The workflow has no `push` or `pull_request` trigger. It cannot run from this
feature branch: scheduled workflows run only from the default branch, and manual
dispatch is available only after the workflow exists on the default branch.

### Snippet

```html
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/nickbeyrgest-ui/nickbeyrgest-ui/snake-output/snake-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/nickbeyrgest-ui/nickbeyrgest-ui/snake-output/snake-light.svg">
    <img src="https://raw.githubusercontent.com/nickbeyrgest-ui/nickbeyrgest-ui/snake-output/snake-light.svg" alt="Animated snake crossing the contribution graph" width="100%">
  </picture>
</p>
```

Place it after the **Development Focus** list or immediately before the footer
divider. It is a single activity graphic, not a statistics card, badge row or
repository index.

### Approval runbook

1. Owner reviews the branch diff and the SVG preview.
2. Merge the branch to `main` (this is the publishing approval).
3. Run a non-publishing check:
   `gh workflow run contribution-snake.yml --ref main -f dry_run=true`
4. Download the `contribution-snake` artifact and inspect both SVGs in a light
   and a dark GitHub theme.
5. Publish deliberately:
   `gh workflow run contribution-snake.yml --ref main -f dry_run=false`
6. Confirm `snake-output` contains exactly `snake-light.svg` and
   `snake-dark.svg`.
7. Apply the README snippet and verify desktop, 390 px mobile, light and dark.

If the owner wants to hold publication after merge, remove the `schedule` block
before merging. With the schedule present, the first automatic run happens on the
next 04:17 UTC after merge.

## 3. Accessibility and validation

- The SVG has `role="img"`, `aria-labelledby` pointing at its `<title>` and
  `<desc>`, and a descriptive `alt` in the README snippet.
- The snake uses `<picture>` with explicit light and dark sources and a
  descriptive `alt`; the light SVG is the fallback. The generated SVGs carry a
  `<desc>` fallback, but their accessible name in the README comes from `alt`,
  because GitHub renders them as images.
- The title animation is decorative; no information exists only in motion.
  Reduced-motion users receive the complete static composition.
- Animation cycles are slower than 1 Hz and do not flash.
- Contrast on `#151211`: wordmark `#D5B58A` 9.59:1, subtitle `#C4A477` 7.92:1,
  body `#DDD3C5` 12.60:1, 78% tagline 8.02:1, copper ornament 4.60:1.
- The SVG contains no script, event handler, remote reference or embedded
  document, so it remains safe when rendered as a README image.

Local checks:

```powershell
python tools/validate_profile.py
actionlint .github/workflows/contribution-snake.yml
```

`tools/validate_profile.py` uses only the Python standard library. It validates
SVG well-formedness, accessibility attributes, reduced motion, contrast, asset
preservation, action pinning, token scope, output-branch isolation, `dry_run`
wiring and the absence of README integration. `actionlint` 1.7.12 is optional and
validates the workflow expression and YAML layer.

## 4. Known limitations

- GitHub serves README SVGs through its image proxy. Animations are preserved,
  but scripts and external assets are not; this SVG deliberately needs neither.
- Raw output URLs are cached by the image proxy. A refreshed snake can take a
  short time to appear after a workflow run.
- The `snake-output` branch must not be protected against force pushes; the
  publisher rebuilds it on every run.
- The wordmark falls back to a system serif on GitHub. That is expected and
  allowed by the brand fallback rule.
- Scheduled publication begins only after merge. Before that, the workflow is
  inert and the `snake-output` URLs in the snippet return 404.
