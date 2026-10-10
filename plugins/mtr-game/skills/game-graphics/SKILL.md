---
name: game-graphics
description: Use when choosing, implementing, debugging or optimizing game rendering or visual effects in 2D or 3D, including pixel art, sprites, 2D lighting and shadows, shaders, PBR, shadows, GI, post-processing, stylized or toon looks, VFX, or when a game "looks flat", "looks cheap", is blurry, shimmers, or misses its frame budget.
---

# Game Graphics: 2D and 3D Rendering Techniques

## Overview

A technique catalog plus a selection procedure. The catalogs live in `references/` and every entry follows the same layout: what/why · how · cost · pitfalls · engine notes (Unity URP/HDRP, Godot 4, Unreal 5) · source.

**Core principle:** pick techniques from the target look, the platform tier and the frame budget, in that order. Fix the foundation pipeline before adding effects: post-processing grades a correct image, it does not repair a wrong one.

## Procedure

1. **Pin the target.** Write down: art style (pixel art, HD 2D, painterly, toon/anime, stylized PBR, realistic), resolution model, platforms with their lowest-tier device, fps target, and GPU budget per frame (60 fps = 16.6 ms, 30 fps = 33.3 ms; on mobile, leave thermal headroom).
2. **Fix the foundation** (table below) before any feature. Most "looks flat/cheap/blurry/shimmery" reports are foundation bugs.
3. **Choose each feature** by finding its entry in the catalog, checking its cost tier against the budget, and reading its pitfalls before writing code.
4. **Tier per platform.** For every expensive feature, define the high tier and the cheap stand-in (SSR → reflection probes, froxel fog → height fog plus light-shaft meshes, CSM 4 → 1 cascade). The look stays the same at a glance.
5. **Measure.** Time every pass with GPU timer queries or the engine profiler; inspect frames in RenderDoc (or the Xcode/Arm/Snapdragon tools on mobile). Each feature sits behind a toggle and has a measured cost.

## Foundations (check first)

| Look | Foundation | Catalog |
|---|---|---|
| Pixel art | Low-res render target, integer scaling, nearest filtering, pixel snapping, sub-pixel camera; lights, shadows and bloom rendered at art resolution; HUD text at native resolution | 2D §A, §G, §H6 |
| Any 3D | Linear color space (albedo/emissive textures sRGB, data textures linear), HDR render target, exposure and tonemapping (ACES / AgX / Khronos PBR Neutral), then sRGB output | 3D §2 |
| Lit 3D | Shadows on the main light, an ambient term that is not a constant (IBL or probes), energy-conserving shading | 3D §3, §4, §6 |
| Lit 2D sprites | Normal maps (hand-painted or generated) so dynamic lights shape sprites instead of tinting them | 2D §G1 |

## Catalog Index

**2D** — `references/2d-techniques.md`

| § | Area | Highlights |
|---|---|---|
| A | Pixel-perfect foundations | low-res RT + integer scale, snapping, smooth camera, sharp-bilinear |
| B | Pixelization and color | 3D→pixel art (Dead Cells, t3ssel8r), pixelize post, palette quantize + Bayer dither, palette swap LUT, RotSprite |
| C | Sprites and batching | batching, atlases + padding, tight meshes vs overdraw, 9-slice |
| D | World structure | tilemaps + autotiling (Wang, blob-47), parallax, Y-sort |
| E | Animation | skeletal 2D (Spine, DragonBones), mesh deformation |
| F | Sprite shaders | outlines (neighbor, SDF/JFA), hit flash, dissolve, SDF text |
| G | Lighting and shadows | normal-mapped lights, light buffers, visibility polygon, shadow volumes, 1D polar shadow map, SDF/JFA, SDF GI, **Radiance Cascades**, deferred sprite G-buffer |
| H | VFX and post | GPU particles, trails, distortion, 2D water, CRT, low-res bloom, screen shake |
| I | Procedural and fake 3D | noise, Mode 7, raycasting, HD-2D |
| J | Performance | fill rate, overdraw, mobile, AA for vector art |

**3D** — `references/3d-techniques.md`

| § | Area | Highlights |
|---|---|---|
| 1 | Pipelines | forward, forward+, clustered, deferred, visibility buffer |
| 2 | Color | linear vs gamma, HDR, tonemappers |
| 3 | PBR | GGX metal/rough, IBL split-sum, normal / parallax / POM |
| 4 | Shadows | shadow maps, CSM, PCF, PCSS, VSM/ESM, contact, virtual shadow maps |
| 5 | AO | SSAO, HBAO, GTAO |
| 6 | GI | lightmaps, SH probes, reflection probes, voxel GI, SDFGI, DDGI, Lumen, ReSTIR, path tracing |
| 7 | Reflections | SSR, planar, probes, ray traced |
| 8 | AA and upscaling | MSAA, FXAA, SMAA, TAA, DLSS / FSR / XeSS |
| 9 | Post | bloom, DOF, motion blur, LUT grading, auto-exposure, grain |
| 10 | Atmosphere | height and froxel fog, god rays, sky models, volumetric clouds |
| 11–13 | Water, terrain, vegetation | Gerstner / FFT ocean, splatting, clipmaps, virtual texturing, instancing, wind, impostors |
| 14 | LOD and culling | frustum, HZB occlusion, GPU-driven, mesh shaders, Nanite |
| 15 | Animation | GPU skinning, blend shapes |
| 16 | Stylized / NPR | cel/ramp, inverted-hull and edge-detect outlines, anime face SDF, Guilty Gear Xrd, hatching |
| 17–19 | Materials, VFX, transparency | decals, SSS, hair, soft particles, flipbooks, OIT |
| 20 | Optimization | draw calls, overdraw, bandwidth, mobile TBDR, RenderDoc |
| 21 | Novel | Gaussian splatting |

Each file ends with **Addenda** (native-res HUD over pixel art, ultrawide, 2D GI off-screen/camera-stable/multi-bounce, URP feature gaps, mobile TBDR rules, grass, tonemapping for stylized looks) and a sources list. Read the section, not the whole file. Entries marked † or [verify] come from general knowledge: confirm them against current engine docs before relying on them.

## Engine Mapping

| Need | Unity (URP/HDRP) | Godot 4 | Unreal 5 |
|---|---|---|---|
| Shader language | HLSL / Shader Graph | Godot shading language (GLSL-like) | HLSL / Material Editor |
| Custom full-screen pass | URP Renderer Feature / HDRP Custom Pass | CompositorEffect, or SubViewport + canvas shader | Post-process material, SceneViewExtension |
| Pixel-perfect 2D | Pixel Perfect Camera | stretch mode `viewport` + scale mode `integer` | low-res render target + nearest upscale |
| 2D lights | URP 2D Renderer (Light2D, Shadow Caster 2D) | PointLight2D, LightOccluder2D, CanvasModulate | Paper2D: lit sprite materials (limited) |
| GPU profiling | Frame Debugger, Profiler, RenderDoc | Visual Profiler, RenderDoc | Unreal Insights, `stat gpu`, RenderDoc |

Write algorithms engine-agnostic first (GLSL/HLSL), then port with this table.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Lighting math on sRGB textures, writing straight to the backbuffer | Linear workflow + HDR target + tonemapping (3D §2) |
| Bloom, lights or soft shadows at screen resolution over pixel art | Render them at art resolution (2D §A1, §H6) |
| Rotating pixel sprites with nearest filtering only | RotSprite / upscale-rotate, or angle snapping + hand-drawn frames (2D §B6) |
| Shipping the PC feature set on mobile | Per-tier stand-ins (step 4); avoid full-screen passes and alpha test on TBDR GPUs (3D §20) |
| TAA smearing outlines and pixel art | MSAA or SMAA for outlined/toon looks; no TAA on pixel art |
| Stacking post effects to fix a flat image | Foundations first: shadows, IBL/probes, AO, then grade |
| Adding a feature without measuring it | Toggle + GPU timing per pass (step 5) |
| ACES on an art-directed toon palette | Neutral tonemapper or none, so ramp colors stay as painted |
| Assuming an engine feature exists (e.g. SSR in URP) | Check that engine version's docs; otherwise custom pass or stand-in |

## Scope

This skill covers rendering and visuals only. Gameplay engineering (architecture, ECS, physics, networking, AI) belongs in a separate skill.
