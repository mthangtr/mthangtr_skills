# Engine contract (plain HTML renderer)

`templates/film.html` implements everything below. Copy it; don't rewrite the helpers.

## The contract

- `window.seek = async (t) => { ... }` draws the frame at `t` seconds. **It is a pure function of `t` and constant data.**
  - Banned inside the film: CSS `transition` and `animation`, `setTimeout`/`setInterval`, `requestAnimationFrame`, `Date.now()`/`performance.now()`, unseeded `Math.random()`, and state carried between calls (no `x += v`).
  - `render.mjs lint` flags these. Preview-only code is allowed when the line carries `// preview-only`.
- `window.ready = true` only after `document.fonts.ready` and every image has been `decode()`d. Declare every constant before the first `seek()`.
- `window.FILM = { duration, fps }` is read by the renderer.
- `?w=&h=` selects the format. Branch layout on aspect in one `layout()` function. Never crop one format into another.
- Use a seeded PRNG (mulberry32) for scatter, noise and particles. Rendering the same second twice must give identical pixels (`render.mjs determinism`).

## Motion primitives

- **Closed-form springs**, `spring(t - t0, k, d)`. Never use linear motion for anything the eye follows. Presets (stiffness/damping):

  | Use | Stiffness/damping |
  |---|---|
  | Snappy UI | 320/30 |
  | Containers and camera | 170/26 |
  | Heavy type and logos | 120/24 |
  | Playful mascots | 180/12 |

- **A value with several targets** is the sum of one spring per change (`springTo`). Put the leading and trailing edges of a stretching tab indicator on *different* springs.
- **Easings must return exactly 0 and 1 at the ends.** A bisection-solved ease that returns 1e-9 at x=0 fires `if (e > 0)` guards early.
- **Camera** is one transform on a container, with keys `[t, zoom, x, y]`.
  - Eased segments; zoom interpolated in **log space**.
  - Never zoom in and out back-to-back.
  - Beat punches: +0.012 zoom per beat with a **~40 ms attack**, then exponential decay. An instant step reads as a one-frame pop (`qa.py pops`).
- **Shared elements carry every handoff.** The button carries its label into the page, and the bubble carries its words into the flood. Content enters *after* its container starts morphing and leaves *before* the next morph, so text never overlaps.
- **Masked text rise:** `translateY(105%)` inside `overflow:hidden`, word stagger ~55 ms, small rotation. Accent words can use a moving gradient (`background-clip:text`). Measure text with canvas `measureText` when a camera scale is applied.
- **Floods** are a circle from the source object. It must clear the farthest corner (`hypot` to all 4 corners ×1.05) in ~0.30–0.35 s, then contract into the next object. Never fade black straight into the accent colour; move an accent element between the states instead.
- **Anticipation and settle:** wind up 3–5 % before a big move, overshoot slightly on landing. Readable target → fast exit → slowing arrival.
- **Holds stay alive:** a slow 3–5 % push, a progress fill, a sheen or a counter. `qa.py frozen` flags stretches over 0.6 s.
- Put `z-index` on every layer. Show and hide with the template's `show(el, on)` (`visibility: inherit | hidden`). A child set to `visible` leaks out of a hidden parent into later scenes.
- **Determinism fails although styles are identical:** this is Chromium compositing. A layer promoted by an earlier transform anti-aliases differently. Set settled transforms to `none` (not identity values), draw dense repeated shapes (waveforms, bars, particles) on one canvas from `t`, and avoid `will-change`.

## Media inside seek(t)

- **Video:** re-encode all-intra (`ffmpeg -i in.mp4 -g 1 -c:v libx264 -crf 14 clip.mp4`). Load it as a blob URL. In `seek`, set `currentTime` and `await` the `seeked` event.
- **Three.js:** call `renderer.render(scene, camera)` inside `seek(t)` with every transform computed from `t`.
  - Use `preserveDrawingBuffer: true`.
  - No `clock.getDelta()`, no physics integration.
  - Position HTML labels each frame from projected 3D anchors.
  - Keep camera pitch at 35–55° (top-down turns objects into slabs).
- **Canvas 2D/WebGL:** draw the whole frame from `t` every call. Never accumulate.
- **Libraries that can be seeked:**
  - GSAP: `timeline({paused:true})` + `tl.seek(t)`.
  - Anime.js: `autoplay:false` + `anim.seek(ms)`.
  - Theatre.js: `sheet.sequence.position = t`.
  - Lottie: `goToAndStop(frame, true)`.

  Never use runtimes that only play in real time (Spline embeds, framer-motion live, CSS keyframes on autoplay).

## Look defaults (override with the brand)

- Use **one** ground (warm off-white `#f5f5f2` or ink `#0b0b0c`), one accent and one secondary accent.
- Use one typeface family with real weights, shipped locally through `@font-face` (woff2 preferred; TTF/OTF is fine). A system fallback is not a brand font. Offline but npm reachable: `npm pack @fontsource/inter` (or another family) and use its woff2 files.
- Type sizes at 1080p, **as seen after the camera zoom**:

  | Text | Size |
  |---|---|
  | Headlines | 110–160 px |
  | UI labels | ≥ 36 px |

  Check readability at 360 px wide (`qa.py sheets` → `_phone.png`). If UI text is still unreadable there, zoom the camera into the part of the UI that carries the beat instead of shrinking type.
- Safe margins: 110 px on 16:9, 80 px on 9:16. Keep every title on one line.
