# Audio

Sound decides whether strong visuals feel amateur. Picture and sound read from the **same cue sheet** (`cues.json`), so sync is exact by construction.

## Music

- **Match the buyer's customer, not "tech launch".**

  | BPM | Feel |
  |---|---|
  | 60–80 | Regal |
  | 90–110 | Smooth |
  | 115–123 | Confident/premium |
  | > 125 | Hype |

  Warm acoustic works for home services. A chill track still needs a pulse.
- **Source:** licensed library music, e.g. Mixkit (free license, credit it): `https://assets.mixkit.co/music/<id>/<id>.mp3`. Pixabay, or the user's own track. Human-made library music edited to picture usually beats generated scores.
- **Find the real drop by energy:** `python3 scripts/audio.py drop track.mp3 --from 8 --to 30`. Never trust an auto beat grid; they are often 1–2 beats off. Then set `drop_in_song` and `drop_in_film` in `cues.json`. The mixer starts the song at `drop_in_song - drop_in_film`.
- **Edit like a music editor:**
  - Cut on bar lines with equal-power crossfades.
  - Time-stretch ≤ 8 % so cuts fall on beats.
  - Optionally a dead stop (~0.4 s) right before the drop.
  - A 5 ms fade-in (a full-level first sample clicks).
  - Fade the tail.
- **Avoid:** vocals, ukulele/whistle corporate stock, trailer hits on calm films. Never reuse a reference film's music.

## Sound effects

- **Sparse and clean beats dense.**
  - One soft, rumble-free whoosh per real transition (little energy below 150 Hz, 80–400 ms rise).
  - UI sounds only on real actions: click on click, tick on label, pop on badge, one chime on confirmation.
  - Typing ticks follow the same per-character rhythm as the animation.
- **Place every SFX by its measured peak** (`align: "peak"`), not by file start. A sample with a 33 ms lead-in lands every hit 2 frames late.
- **Gains:** 0.04–0.3. Keep repeated sounds consistent. Soften sounds that cluster within 0.15 s (×0.6). No effect should peak more than ~6 dB over the local music level.
- **Sources:**
  - Mixkit SFX: `https://assets.mixkit.co/active_storage/sfx/<id>/<id>-preview.mp3`.
  - A licensed library.
  - `audio.py synth` (click, tick, pop, thump, whoosh, riser) as an offline fallback. Clients have rejected purely synthesized sine ticks as cheap, so prefer real recordings when you have network access and say which you used.
- **Voice-over:** a TTS with word timestamps → cues. Duck the music ~9 dB under the voice. Captions come from the same timestamps.

## Master

- **Punchy launch film:** −14 LUFS integrated, true peak ≤ −1 dBFS (`audio.py mix` does a two-pass loudnorm plus limiter). Calm films can sit at −16 to −19 LUFS, but say so.
- **Loudness range:** ≥ ~3 LU for energetic scores on films of 10 s or more. A flat wall of sound reads as stock. Under ~10 s LRA is unstable, so judge section contrast instead: RMS of intro vs drop vs end should differ by ≥ 2–3 dB.
- **Verify on the muxed file:** `python3 scripts/qa.py loudness out/video.final.mp4`.
- **Be honest:** if nobody listened, say that the mix was verified by measurement only. Deliver a music-only fallback when sound effects are contested.
