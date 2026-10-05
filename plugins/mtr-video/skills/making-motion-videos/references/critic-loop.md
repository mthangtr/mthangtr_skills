# Independent critic loop

**The builder never grades its own work.** The builder knows what each frame was meant to show and sees that intent in the pixels. A fresh critic sees only the pixels, the way viewers do.

## How

1. Render, then run `python3 scripts/qa.py report <film>`. Also run `qa.py sheets <film> --strip <t,…>`, with a strip at every transition and fast move.
2. **Spawn a fresh critic.** Use your harness's subagent/Task tool, or a new session. Give it only:
   - the MP4 path;
   - the brief and the user's own words;
   - any references;
   - for verification rounds, the previous critic's report.

   Never give it your reasoning or a list of what you think you fixed.
3. Fix the highest-impact items first. Re-render only the affected range (`render.mjs video --from a --to b`, then `render.mjs splice`) and re-measure.
4. **Verify with a NEW critic:** each prior item is FIXED / PARTLY / STILL PRESENT, plus any new regressions. Fixes often create new defects: z-order lost, a moved object now crossing a headline.
5. **Stop** when every score is ≥ 8, measured checks pass and no known defect remains. Usually 2–4 rounds. "Cosmetic" is not an exit: an item you can see on a contact sheet or strip is a defect, and a range re-render plus `splice` fixes it. The only items that may stay are ones measurable but invisible at native resolution; list them.

**If the harness truly cannot spawn another agent:**
- Run the critic prompt yourself in a clean pass that starts from the sheets, not from your code.
- Write the scores before reading your own notes.
- State in the delivery report that review was self-review, so it carries less trust.
- Apply the **same stop rule**. Any axis below 8, or any defect you named, means another pass. Otherwise deliver a cut explicitly labelled "unfinished" with those items listed.
- Offer the user a one-line way to get an independent review (the full-film prompt below, pasted into a fresh session).

## Full-film critic prompt

```
You are an independent, harsh motion director. You did NOT build this; judge rendered pixels and measured audio, not intentions.

Artifact: <path> (<dur>s, <w>x<h>, <fps>fps, audio: yes/no). Brief: <one paragraph: product, buyer, the one action, brand palette/type>.
User's words, verbatim: <paste>.
Benchmark: premium SaaS launch films (Linear/Vercel/Apple-keynote calibre).

Method: extract frames yourself with ffmpeg: a contact sheet every 0.25 s, 12-frame strips around every transition (<times>), and a 360-px-wide sheet for phone readability. Run `python3 <skill>/scripts/qa.py report <path>`.

Score 1-10, each with timestamps: hook in first 2 s · frame 0 as thumbnail · readability at 360 px · motion quality (springs, no dead frames, no linear drift) · variety (new idea every 2-4 s) · composition (lead subject fills 60-85%, no empty fields) · transitions (shared element / matched direction, no unrelated crossfades) · brand + claim accuracy (every number sourced or labelled "Example data") · sound sync.
Then: the 5 worst problems ranked by impact, each with timestamp, screen region and a concrete code-level fix. Hunt for: text overlapping during swaps, clipped descenders, linear motion, centred title on a gradient, small subject in empty field, blur-crossfade between unrelated scenes, a dead beat, 1-frame pops, unlabeled invented data, a false caption.
End with SHIP or ANOTHER PASS. Under 700 words, also written to <report path>.
```

## Verification critic prompt

```
You are an independent critic; you did NOT build this. New render: <path>. Previous critic report: <path>.
For each item in that report: FIXED / PARTLY / STILL PRESENT with timestamps. Then list NEW defects (glitch frames, overlaps, clipped text, regressions). Re-score the same axes. End with SHIP or ANOTHER PASS (max 3 fixes). Under 500 words.
```

## Ledger (goes in the delivery report)

| Round | Artifact | Critic verdict + scores | Top findings | Changes | Measured after |
|---|---|---|---|---|---|
| 1 | out/v1.mp4 | ANOTHER PASS, comp 6, transitions 5 | small card 2-5 s; crossfade at 4.5 | zoom camera to card; button morphs into card | frozen 3.3→0.6 s/30s |
