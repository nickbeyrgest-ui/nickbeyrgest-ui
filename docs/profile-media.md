# Profile media integration

Status: **static studio title and cinematic Saltshore hero integrated.**
`README.md` renders the approved static title plates and the Saltshore fog loop
with a reduced-motion poster. The existing buttons, screenshots, copy and divider
are preserved. Only the Saltshore hero animates.

## 1. Static studio title

Assets:

- `assets/branding/studio-hero.png` — desktop title plate.
- `assets/branding/studio-hero-mobile.png` — mobile title plate.

### Snippet

```html
<div align="center">
  <picture>
    <source media="(max-width: 600px)" srcset="assets/branding/studio-hero-mobile.png">
    <img src="assets/branding/studio-hero.png" alt="Marvollo Studio — independent game development" width="100%">
  </picture>
</div>
```

At viewport widths up to 600 px the `<picture>` element switches to the mobile
plate; above that the desktop plate fills the available width. The title is
static, carries no motion and has descriptive alt text.

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

## 3. Accessibility and validation

- The title plates have descriptive alt text; the mobile plate is selected by
  viewport width, not by motion preference.
- The Saltshore hero is decorative; its meaning is carried by the link and alt
  text. Reduced-motion visitors receive the complete static poster.
- Animation cycles are slower than 1 Hz and do not flash.

Local checks:

```powershell
python tools/validate_profile.py
```

`tools/validate_profile.py` uses only the Python standard library. It checks the
static title integration, the Saltshore loop and poster, asset preservation,
documentation state and the absence of scheduled workflows.

## 4. Known limitations

- GitHub serves README images through its image proxy; local relative paths are
  resolved by GitHub from the repository root.
- The Saltshore loop is a GIF and does not pause on its own; visitors who prefer
  reduced motion receive the static poster through `<picture>`.
- The title plates are raster images and do not adapt their internal typography;
  the mobile plate is used at widths up to 600 px.
