# making-motion-videos

A Claude Code / Agent Skills skill for producing motion design videos as code: launch films, product teasers, explainers, showreels and social clips. The film is written as HTML/Canvas/SVG/Three.js (or as a HyperFrames or Remotion project), rendered frame by frame in headless Chromium, and encoded with ffmpeg.

## Install

```bash
# all projects
mkdir -p ~/.claude/skills && cp -r making-motion-videos ~/.claude/skills/
# or one project
mkdir -p .claude/skills && cp -r making-motion-videos .claude/skills/
```

Dependencies:
- Node 18+ with `playwright` resolvable from the project (`npm i -D playwright` and `npx playwright install chromium`).
- ffmpeg/ffprobe on PATH.
- Python 3 with `numpy`.

## Contents

```
SKILL.md                    process, truth rules, delivery report, red flags (read first)
references/engine.md        seek(t) contract, springs, camera, handoffs, media, look defaults
references/renderers.md     Playwright pipeline, HyperFrames, Remotion
references/motion-grammar.md  6 rules, composition, the generic-AI-look table, mechanisms, pacing
references/audio.md         music by buyer, drop by energy, SFX by peak, -14 LUFS
references/critic-loop.md   independent critic prompts, verification, ledger
references/prompting.md     prompt patterns for users, remake mode
scripts/render.mjs          lint | stills | beats | video (subframe motion blur, workers, mux) | determinism | splice
scripts/qa.py               report | sheets | frozen | pops | space | loudness
scripts/audio.py            drop | bpm | peak | mix (cue sheet -> two-pass loudnorm) | synth
templates/film.html         a deterministic starter film (persistent actor, masked type, flood on the drop)
```

## How it was built and tested

The skill was written with the TDD method from [obra/superpowers `writing-skills`](https://github.com/obra/superpowers/tree/main/skills/writing-skills): RED, then GREEN, then REFACTOR.

**RED: baseline, without the skill.** Two real build tasks plus one set of forced-choice pressure scenarios. The agents already wrote deterministic `seek(t)` code. They failed in these ways:
- Shipped defects they had noticed ("acceptable but slightly messy").
- Never used an independent critic.
- Accepted a "made with one prompt" caption.
- Kept unsourced "10,000 teams" / "3x" claims, with a "fallback" file instead of fixing the main deliverable.
- Showed invented data without a label.
- Opened on an empty frame 0.
- Left a small subject in a big dark field.
- Skipped motion blur to save time.

In the quiz format they gave the right answers. Under real work, they didn't.

**GREEN: the same build tasks, with the skill.** All of the following passed:
- Frame 0 is a finished composition.
- No holds and no pops.
- Subject span 0.6–0.9 (baseline: < 0.45).
- Motion blur on.
- −14 LUFS.
- True captions.
- Unsourced claims removed.
- Illustrative data labelled.

**REFACTOR: closed the loopholes found in GREEN.**
- "Cosmetic" items accepted to avoid a re-render: added `splice` and made "cosmetic" not a stop reason.
- Self-review stopped at a score of 7: same stop rule for self-review.
- Labelling a "Trusted by 10,000 teams" claim: social proof must be removed, not labelled.
- Mixed subframe counts: `--sub 6` on every delivered second.
- Determinism broken by Chromium anti-aliasing.
- Beat punches without attack.
- `qa.py` heuristics.
- The audio loudnorm LRA undershoot.

A pressure re-test then passed on every item.

## Sources

The research behind the skill draws on:
- [howseen-ai/claude-motion-design](https://github.com/howseen-ai/claude-motion-design) (MIT, Raphaël Aubry): the seek(t) engine, beat-map flow, subframe blur, drop by energy, SFX by peak, remake mode, honesty rules.
- [echris6/motion-video-kit](https://github.com/echris6/motion-video-kit) (MIT): the motion grammar from 28 launch films, the Gauntlet critic loop, the quality bar, audio rules.
- [HyperFrames](https://github.com/heygen-com/hyperframes) (Apache-2.0) and [Remotion agent skills](https://www.remotion.dev/docs/ai/skills).
- Public X posts and articles from the Opus 5.5 motion-design wave of September 2026: the showreel prompt, structured `<inputs>/<rules>/<structure>/<motion>` prompts, and "one prompt is ~10 % of the video".

All text and code in this folder are original. They are released under MIT.
