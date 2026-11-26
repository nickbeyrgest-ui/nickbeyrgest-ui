# Profile media integration

Status: **title, Saltshore hero and contribution snake integrated and
published**. `README.md` uses `assets/branding/title-animated.svg` as the single
profile title, serves the cinematic Saltshore loop with a reduced-motion poster,
and references the published light/dark snake SVGs. The existing buttons,
screenshots, copy and divider are preserved.

Publishing record:

| Step | Reference |
|---|---|
| Integration PR | #5, merged as `5ce53a7` with a history-preserving merge commit |
| Dry run | run `45819665287`, success, artifacts inspected, no branch created |
| Publish run | run `45819921938`, success |
| Output commit | `2722269` on `snake-output`, one normal commit, no force |
| Raw checks | `snake-light.svg` and `snake-dark.svg` returned HTTP 200 |

The snake output was published before the README referenced it, so the profile
never linked to a missing image.

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

It replaces the previous static hero `<picture>` block at the top of
`README.md`. Do **not** restore both blocks: the profile would show the wordmark
twice. Keep `assets/branding/studio-hero.png` and
`assets/branding/studio-hero-mobile.png` in the repository for rollback.

## 2. Cinematic Saltshore hero

Assets:

- `assets/saltshore/hero-fog.gif` — 1200 × 400, 72 frames at 80 ms, 5.76 s,
  seamless loop (first and last frame match). Subtle fog, sea shimmer and wind
  over the approved key art; Mira, the wordmark and the composition are
  unchanged, and the source `assets/saltshore/hero.png` is untouched.
- `assets/saltshore/hero-fog-poster.png` — 1920 × 640 static poster used when the
  visitor prefers reduced motion.

The README keeps the existing itch.io link and alt text and wraps the loop in
`<picture>`:

```html
<p align="center">
  <a href="https://marvollostudio.itch.io/saltshore">
    <picture>
      <source media="(prefers-reduced-motion: reduce)" srcset="assets/saltshore/hero-fog-poster.png">
      <img src="assets/saltshore/hero-fog.gif" alt="Saltshore — a dark fantasy RPG by Marvollo Studio" width="100%">
    </picture>
  </a>
</p>
```

The motion is decorative atmosphere, carries no information, stays well below
1 Hz and never flashes. The poster keeps the complete composition for
reduced-motion visitors.

## 3. Contribution snake

Workflow: `.github/workflows/contribution-snake.yml`.

| Control | Value |
|---|---|
| Generator | `Platane/snk/svg-only` v3.5.0, pinned to `d8f6715049803e982ee5ff501b6b9b7d5deeb09b` |
| Publisher | `crazy-max/ghaction-github-pages` v5.0.0, pinned to `1d6ee9b181a81033a16bd707a1401afa978daab4` |
| Artifact | `actions/upload-artifact` v7.0.2, pinned to `cf430e030ddbb5b0abf93d22962f4752f3646cd9` |
| Token | Built-in `GITHUB_TOKEN` only. No PAT, no repository secret. |
| Permissions | `permissions: {}` at workflow level; job gets `contents: write` only |
| Output | Isolated `snake-output` branch; appends normal commits, never force-pushes; never `main` |
| Triggers | Daily `schedule` plus `workflow_dispatch` |
| Manual safety | `dry_run` defaults to `true`, so a manual run uploads artifacts without publishing |
| Palette | `github-light` and `github-dark`, with muted cold dots and copper/gold snake |

The workflow has no `push` or `pull_request` trigger. It cannot run until it is
on the default branch: scheduled workflows run only from the default branch, and
manual dispatch is available only after the workflow exists there.

### Snippet

Applied to `README.md` only after both raw URLs returned HTTP 200:

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

### Publishing runbook

1. Owner reviews the branch diff and the SVG preview (done for PR #5).
2. Merge the branch to `main` with a merge commit (done).
3. Run a non-publishing check:
   `gh workflow run contribution-snake.yml --ref main -f dry_run=true`
4. Download the `contribution-snake` artifact and inspect both SVGs in a light
   and a dark GitHub theme.
5. Publish deliberately:
   `gh workflow run contribution-snake.yml --ref main -f dry_run=false`
6. Confirm `snake-output` contains exactly `snake-light.svg` and
   `snake-dark.svg`.
7. Apply the README snippet and verify desktop, 390 px mobile, light and dark.

The `schedule` trigger is active, so the snake refreshes daily at 04:17 UTC.
Manual runs default to `dry_run=true`; publishing requires the explicit boolean
input `false`.

## 4. Accessibility and validation

- The SVG has `role="img"`, `aria-labelledby` pointing at its `<title>` and
  `<desc>`, and a descriptive `alt` in the README snippet.
- The snake uses `<picture>` with explicit light and dark sources and a
  descriptive `alt`; the light SVG is the fallback. The generated SVGs carry a
  `<desc>` fallback, but their accessible name in the README comes from `alt`,
  because GitHub renders them as images.
- The title and Saltshore hero animations are decorative; no information exists
  only in motion. Reduced-motion users receive the complete static title plate
  and the static Saltshore poster.
- The generated snake SVG animates continuously on a 14.5 s loop. snk v3.5.0
  does not expose a reduced-motion variant, so that graphic cannot honor the
  preference. It is decorative, does not flash, and its meaning is carried by
  the README alt text; the title and hero do honor `prefers-reduced-motion`.
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
wiring and the expected README integration state. `actionlint` 1.7.12 is
optional and validates the workflow expression and YAML layer.

## 5. Known limitations

- GitHub serves README SVGs through its image proxy. Animations are preserved,
  but scripts and external assets are not; this SVG deliberately needs neither.
- Raw output URLs are cached by the image proxy. A refreshed snake can take a
  short time to appear after a workflow run.
- The `snake-output` branch receives normal commits and grows one commit per
  day when contributions change. No force push is used.
- The wordmark falls back to a system serif on GitHub. That is expected and
  allowed by the brand fallback rule.
- Scheduled publication begins only after merge. Before that, the workflow is
  inert and the `snake-output` URLs in the snippet return 404.
