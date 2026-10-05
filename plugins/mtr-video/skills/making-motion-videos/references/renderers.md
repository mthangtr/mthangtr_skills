# Renderers

## Plain HTML + Playwright + ffmpeg (default)

`scripts/render.mjs` serves the page's folder over a local HTTP server, opens headless Chromium at the target viewport, waits for `window.ready`, then for each frame calls `seek(t)`, waits two paints and pipes a PNG screenshot into ffmpeg.

- **Motion blur:** `--sub N` captures N subframes per frame over `--shutter` (default 0.5 = 180°). Blending uses `tmix`.
  - 6–8 for fast moves.
  - 4 shows ghosting.
  - 1 is only for drafts.
- **Speed:**
  - `--workers K` splits the range across pages and concatenates the parts.
  - `--from/--to` re-renders only the seconds you changed; `render.mjs splice <film.mp4> <part.mp4> --at <s>` puts them back (one re-encode), then check the seams with `qa.py sheets --strip`.
  - Expect ~1–1.5 min of wall time per second of 1080p60 film at 8 subframes. Run long renders in the background.
- **Encode:** libx264 crf 16, BT.709 TV range tagged, yuv420p. With `--audio`, it muxes AAC 256k with faststart into `<out>.final.mp4`.
- **Rendering in parallel:** give each version its own output folder so renders don't clash.
- **Chromium raster caching:** a frame reached after a scaled or blurred state can come out softer than the same frame rendered fresh. Check with `determinism`. Avoid `will-change` and prefer 2D transforms on text that must stay sharp.
- **Grain/noise:** add it in ffmpeg *after* QA (`noise=alls=6:allf=t`), or measure `qa.py frozen` on a grain-free render. Grain hides holds.

## HyperFrames

Use it when the project already depends on it or the user asks. It is an open-source HTML→MP4 framework (HeyGen, Apache-2.0) with its own agent skills.

- **Install its skills first** and follow its composition contract. That contract wins on mechanics:
  - Plugin: `claude plugin marketplace add heygen-com/hyperframes`, then `claude plugin install hyperframes@hyperframes`.
  - Standalone: `npx hyperframes skills update` (non-interactive core set).
- **Contract essentials:**
  - Root `<div data-composition-id data-width data-height data-duration>`.
  - Timed elements carry `data-start` plus a duration.
  - Exactly one `gsap.timeline({ paused: true })` registered at `window.__timelines["<composition-id>"]`.
  - No render-time clocks, no unseeded `Math.random`, no `repeat: -1`.
  - Never tween `visibility`/`autoAlpha` on a `.clip` (animate a child).
  - Every `<audio>` has an `id`.
  - Named font families need a local `@font-face`.
- **Dev loop:**
  - `npx hyperframes lint` and `check`. 0 findings is required. A lint error disables the layout and contrast audits, so "0 samples" means nothing ran.
  - `npx hyperframes snapshot --at <t1,t2,…>` gives the stills. Look at them.
  - `npx hyperframes preview`.
  - `npx hyperframes render`.
- **What this skill still adds:** storyboard columns, frame 0, subject fill, persistent actor, truth rules, `qa.py report` on the rendered MP4, and the independent critic loop.

## Remotion

Use it when the project is a Remotion (React) app. Official agent skills install with `npx skills add remotion-dev/skills`.

- **Determinism:** derive everything from `const frame = useCurrentFrame()`.
  - Use `interpolate(frame, [a, b], [x, y], {extrapolateLeft:'clamp', extrapolateRight:'clamp'})` and `spring({frame, fps, config:{stiffness, damping}})`.
  - Scenes go in `<Sequence from durationInFrames>`.
  - Randomness comes from `random(seed)`.
  - No CSS transitions or `useEffect` timers.
- **Commands:**
  - Stills: `npx remotion still <CompId> --frame=<n> out.png`.
  - Video: `npx remotion render <CompId> out.mp4`.
- **Motion blur:** `@remotion/motion-blur` (`<CameraMotionBlur>`).
- **Licensing:** Remotion needs a paid company license for larger companies. Check remotion.dev/license before commercial use and tell the user.
- Run `qa.py report` on the output exactly as for the default renderer.
