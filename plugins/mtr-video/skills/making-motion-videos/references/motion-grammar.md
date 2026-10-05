# Motion grammar

Distilled from analyses of professional SaaS launch films and from the viral Opus 5.5 motion pieces (Sep 2026). Read this before writing STORYBOARD.md.

## Six rules

1. **The foreground becomes the transition.** A headline, logo or shape scales through the camera, with directional blur, while the next scene is already in place underneath. There is no empty gap between scenes.
2. **One persistent actor.** A shape, cursor, card, line or bubble keeps its identity across shots. Unrelated reveals in sequence read as a slideshow however well each one is animated. The strongest one-prompt films are "one shape, never cut".
3. **Density comes from hierarchy.** One primary move (camera or actor), supporting staggers (cards, labels) and tertiary detail (sheens, ticks, counters), all overlapping. Don't start and stop the whole frame on every beat.
4. **Change speed; don't drift at a constant rate.** Readable landing → fast exit → slowing arrival.
5. **Hard cuts are fine** when subject, scale, direction and material match, and motion continues through the cut on a beat.
6. **Cause → effect.** Scans produce findings, prompts produce artifacts, clicks produce states. Every animated action visibly produces a result.

## Composition

- The lead subject fills **60–85 %** of the usable frame in feature beats. A small card floating in a big dark field reads as cheap. Zoom the camera so each state fills the frame.
- Vary composition type across beats: macro, wide, overhead, UI close-up, typographic impact. Don't repeat "heading above three cards".
- Keep 1–2 reading targets at a time.
- Oversized type enters on opposing axes, masks or reveals the next scene, and never sits over busy footage without a backing.
- Hand objects across scenes at exact pixel coordinates. Pre-position the destination so the carried object lands on it.
- Keep one wipe direction and one title position through a sequence of similar shots. The outgoing title leaves before a wipe, and the incoming one enters after it.

## The generic "AI video" look: what to replace

| Generic | Replace with |
|---|---|
| Centered title on a radial gradient glow | Type as an actor: oversized, cropped by the frame, masked, interacting with the subject |
| Scene A blur-crossfades into an unrelated scene B | A shared element or a foreground fly-through carries A into B |
| Small UI card in the middle of an empty field | Camera zoomed so the UI fills 60–85 %; a cursor driving real clicks and typing |
| Everything eases in, holds, eases out together | A staggered hierarchy where the next beat's motion starts before the previous one settles |
| Linear drifts, uniform speed | Springs with tiny overshoot; anticipation before big moves |
| A dot or a glow on frame 0 | A finished composition on frame 0 (it is the thumbnail) |

## Mechanism catalog

| Mechanism | What it does |
|---|---|
| Foreground fly-through | Claim/logo scales past the camera to reveal the pre-positioned next scene |
| Logo-as-portal | The brand shape grows until its hole becomes the next frame |
| Selection → expansion | A selected item expands into the detailed workspace for the next beat |
| Materializing result | A shell appears, then its regions fill in order |
| Persistent rails | Lines/paths survive a text swap and connect two states |
| Continuous canvas | The camera travels over one spatial layout; the selected item stays sharp, neighbours blur |
| Artifact ring | Many small artifacts orbit one stable sentence |
| Card stack / fan | One card becomes a collection, or a collection resolves to one |
| Perspective fold | A panel folds to a luminous strip; the next panel rises out of it |
| Exploded layers | A product separates into its layers, then recombines |
| Wall → one actor | Information overload collapses into a single subject |
| Colour flood | A circle from the source clears the frame; use it once, on the drop |
| Request → picker → confirmation | A bubble anchors while a sheet rises, a choice is made, the state confirms |

## Pacing (30 s film)

- 12–15 distinct compositions; beats of 1.4–3.5 s; nothing fully still for over 0.6 s.
- Hook in the first 2 s.
- Reading holds only on the frames that carry the message (result, CTA), with a slow push.
- End card readable for 1.5–2 s with gentle drift.
- Muted-first: X and LinkedIn autoplay without sound, so kinetic type must carry the story.
- **X:** 16:9 or 1:1, ≤ 2:20. **LinkedIn:** 4:5 1080×1350. Captions go in the post.

## Product films

- **Story as a chain:** the problem in the user's words (3–5 s) → each step produces what the next uses (one continuous camera) → a measurable result on screen → CTA.
- **Rebuild screens in code from real screenshots, never paste them.**
  - Sample exact colours.
  - Extract one ui-tokens file (colours, radii, shadows, spacing, fonts).
  - Animate element by element: rows cascading, counters, typing, cursor clicks.
  - Check each rebuilt screen side by side with its screenshot.
