# Escaping the Median

## The median

Before ideating, describe what any model would produce for "app icon for <brief>". It is almost always: the function's most common noun, drawn from circles and rounded rectangles, centered at 50–60% of the canvas, mirror-symmetric, uniform stroke with round caps, white on `#1c1c1e` or on a two-stop indigo/blue gradient, with one Apple system accent. Your median sentence names the specific noun and colors for this brief.

## Five lenses (raw material)

| Lens | Question | Example |
|---|---|---|
| Name | What does the name look, sound or mean like, literally or as wordplay? | "Pip" → a seed with a sprout; "Drift" → a slow sideways slide, flotsam |
| Feeling | What does the user feel after using it — a verb or emotion, not a noun? | A focus app → "the room exhaling"; a finance app → "loose ends tied" |
| Vernacular | Which visual language from outside app icons fits? | Japanese kamon crests, Swiss poster, tattoo flash, postage stamp, luggage tag, enamel pin, risograph print, folk papercut, road signage, toy packaging, botanical plate |
| Object | If the app were a physical object, creature or material, what is it? | A travel journal → a well-worn passport stamp; a habit app → a pebble polished by use |
| Paradox | Which two things that don't belong together make the idea vivid? | A cloud made of bricks, a calm alarm, a soft lock |

A strong concept usually combines two lenses: an idea from Name/Feeling/Object/Paradox, executed in a Vernacular.

## Form moves (pick ≥ 2 per concept)

| Move | What it does | Helper |
|---|---|---|
| Crop | Subject at 110–140% so the edges cut it; or tiny subject in a big field | — |
| Offset | Subject off-center with deliberate tension toward one edge or corner | — |
| Figure–ground | Negative space forms a second reading | — |
| Organic silhouette | Replace circle/rect primitives with a breathing, irregular outline | `blob()` |
| Hand line | Edges or strokes with ink-like taper and slight wobble | `brush()`, `wobble()` |
| Material | Grain, paper or print texture in the background layer | `stipple()` |
| Single surprising detail | One unexpected detail (eyes on an object, a bite, a fold, a stitch) | — |
| Off-tone palette | Colors from a real reference instead of pure/system values | see below |

`scripts/shapes.mjs` exports `blob`, `wobble`, `brush`, `ellipse`, `stipple`, `toPath`, `svg`, `rng`. All are seeded, so one generator script reproduces the icon exactly.

## Palette references

Name a concrete source and sample 2–4 colors from it, e.g.: Kodak Portra skin and shadow tones · terracotta pot and moss · 1970s Swiss rail signage · risograph fluorescent pink on newsprint · enamel pin gold and cream · Lisbon azulejo blue · Kraft paper and stamp red · Matcha, rice paper and lacquer black · Sodium streetlight orange on asphalt. Off-tones (a slightly warm white, an ink-black with brown in it) read as made by a person; `#ffffff` on `#1c1c1e` reads as default.

## AI tells (what the lint and your eye look for)

| Tell | Seen in testing |
|---|---|
| Apple system colors verbatim | `#1c1c1e` backgrounds, `#34c759` toggle, `#0a84ff → #5e5ce6` gradient |
| Median placement: one centered shape at 45–65% | Bookmark D, hatching egg, pause, paw |
| Perfect mirror symmetry without a reason | Balloon, paw, pause, notification stack |
| Function noun as the idea | Toggle for focus, paw for pets, pause for "silence", map dots for travel |
| Uniform stroke, round caps, primitives only | Photo-trail dots, pause bars |
| Indigo/violet gradient as "premium" | Every unguided baseline |

A tell can stay if the idea needs it — say why in the review.
