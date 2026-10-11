# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal Claude Code **plugin marketplace** (`mtr-skills`). There is no app, build step, or test suite — the product is skill content (Markdown) plus small helper scripts that skills tell Claude to run.

- `.claude-plugin/marketplace.json` — lists every plugin (`name`, `source`, `description`). Adding a plugin means adding an entry here **and** creating `plugins/<name>/.claude-plugin/plugin.json`.
- `plugins/<plugin>/skills/<skill>/SKILL.md` — one skill per directory. Frontmatter `name` must match the directory; `description` is the trigger text (phrased "Use when…" / "This skill should be used when…" with concrete user phrasings, sometimes Vietnamese).
- Supporting material sits beside `SKILL.md`: `references/` (long-form knowledge loaded on demand), `scripts/` (runnable helpers), `assets/` / `templates/`. SKILL.md stays short and points into these.

Plugins: `mtr-business` (idea validation, GTM), `mtr-design` (SVG app icons, product mascots), `mtr-video` (AI film pipeline + HTML motion videos), `mtr-game` (GDD doc sets, 2D/3D graphics techniques).

## Versioning

`plugin.json` carries the plugin version. In `mtr-video`, each pipeline SKILL.md also has `metadata.version` — keep these in sync with `plugins/mtr-video/.claude-plugin/plugin.json` (currently 0.3.0) when bumping.

## mtr-video architecture (the only multi-file system)

- `film-pipeline` is the orchestrator for 8 step skills (concept → story → visual-bible → shot-design → blender-previs → video-generation → dailies-review → post-assembly). Each step has a gate; project state follows `film-pipeline/references/project-state-template.json`.
- `film-pipeline/references/shared-conventions.md` is the **common law and wins over every other file** (fps, IDs, folder contract `00_concept.md` … `06_review/`, cost formula, tests T1–T10, max 3 regen rounds). Change conventions there, not in individual skills.
- **Model-agnostic rule:** no video-model limits are hardcoded. They live in `video-generation/references/models/<id>/profile.json` (schema: `model-profile.schema.json`); validators and linters read limits from the active profile. New models follow `video-generation/references/adding-a-model.md`; adapters go in `video-generation/scripts/adapters/<id>/`.
- `making-motion-videos` is independent of the pipeline (HTML `seek(t)` pages rendered to video via headless Chromium).
- `plugins/mtr-video/README.md` records what has/hasn't been executed (e.g. Seedance `client.py`, `afs_previs_lib.py` in Blender are untested). Update it when you verify a script.

## Running the helper scripts

Scripts are standalone CLIs; usage is in each file's header docstring/comment. Examples:

```bash
python3 plugins/mtr-video/skills/video-generation/scripts/validate_profile.py <path>/profile.json
python3 plugins/mtr-video/skills/shot-design/scripts/validate_shotlist.py shotlist.json [--models-dir DIR]
python3 plugins/mtr-video/skills/video-generation/scripts/lint_prompt.py prompt.md manifest.json --profile <profile.json>
node plugins/mtr-video/skills/making-motion-videos/scripts/render.mjs lint <page.html>
npm install --prefix plugins/mtr-design/skills/designing-premium-app-icons/scripts   # once; node_modules is gitignored
node plugins/mtr-design/skills/designing-premium-app-icons/scripts/preview.mjs <out-dir>
```

Python deps (not pinned anywhere): `jsonschema`, `opentimelineio`, `opencv-python`, `numpy`; ffmpeg/ffprobe on PATH. Quick sanity check for edited Python: `python3 -m py_compile <file>`. `shot-design/references/shotlist.example.json` is a ready input for `validate_shotlist.py`.
