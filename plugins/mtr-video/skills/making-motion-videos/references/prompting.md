# Prompting patterns (for users who ask how to prompt this)

"One prompt" videos on X are real outputs with hidden iteration. What actually decides quality is the harness: a brief, a beat map, stills first, a critic loop and real assets. Use max or xhigh effort for a new film and medium for small fixes.

## The showreel one-liner (exploration only)

> make a dynamic 15-second motion graphics video that shows what an incredible motion designer you are, like it's your showreel for a résumé. go all out.

This is good for discovering a style. It is not enough for a product film.

## Structured product brief (works best)

```
<inputs>
Ask me for: my product + URL · 8–12 UI states that tell its story · the real data shown in each · brand colors, fonts, accent · formats (16:9, 9:16, 1:1, 4:5) · music preference
</inputs>
<rules>
One HTML file. One window.seek(t). No CSS transitions, no timers, no state between frames.
One shape, never cut: every state is the same element changing size, radius and colour while content swaps.
A cursor drives the sequence with real clicks, typing and one drag. Real UI, real data, no placeholders.
</rules>
<structure>
120 BPM grid; something happens on every beat; the music drop lands on the key reveal.
logo → button → field → loader → result → … → logo
</structure>
<motion>
Closed-form springs with a tiny overshoot; sum one spring per retarget.
Content enters after its container starts morphing and leaves before the next morph.
Short blur on transitions; never fade black straight into the accent; zoom so every state fills the frame.
</motion>
<process>
Write BRIEF.md and a beat-mapped STORYBOARD.md first. Show me 4 stills before the full render.
Render 60 fps with motion blur. Mix music + SFX on the same cue sheet at −14 LUFS.
Have a fresh reviewer score it and fix until every score ≥ 8.
</process>
```

## Useful revision notes

- "slow every zoom to 0.7×"
- "hard cut here on the beat"
- "push in on the button"
- "the card should carry its title into the next scene"
- "nothing still for more than half a second"

## Remake mode (frame-locked 1:1 copy for another brand)

1. **Analyze.** Extract every frame of the reference. Detect hard cuts (frame-diff spikes); expect only 10–15, because most "cuts" are continuous morphs. Write SPEC.md with a shot table (frames, content, brand swap).
2. **Build.** Write a shared `seek(F)` engine with a palette filter that re-hues leftover colours from the old brand. Parallel builders each own a contiguous shot group and verify against side-by-side compare sheets. One audio agent places a royalty-free track stretched to the reference BPM, with SFX on the reference hit times.
3. **Deliver.** A split-screen "original | copy" with labels.

Never reuse the reference's music, voice, people or logos. Credit the original in the post, and never imply a partnership.
