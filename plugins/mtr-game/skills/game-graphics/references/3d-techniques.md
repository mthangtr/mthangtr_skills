# Real-Time Rendering Technique Catalog (engine-agnostic, with URP/HDRP, Godot 4, UE5 notes)

**How to read this.** Each entry gives: what/why · how · cost tier (M = mobile, C = console/mid PC, H = high-end) · pitfalls · engine notes · source. Every source listed was opened this session. Claims marked † come from general knowledge and were not confirmed in the cited page. Treat them as likely but unverified.

---

## 1. Render pipeline architectures

**Forward**
- **What/why:** Shade each object once per pass, with its lights. Simple, handles MSAA and transparency, has low bandwidth.
- **How:** Each draw evaluates a capped per-object light list in the fragment shader. Cost grows with objects × lights.
- **Cost:** M+.
- **Pitfalls:** Per-object light limits. Overdraw shades hidden pixels, so use a depth prepass.
- **Engine:** URP Forward allows 9 lights per object and 257 per camera, supports MSAA and per-vertex lights, and is the best fit for mobile.
- **Source:** https://docs.unity3d.com/6000.0/Documentation/Manual/urp/rendering-paths-comparison.html

**Forward+ (tiled forward)**
- **What/why:** Many lights in a forward renderer.
- **How:** A compute pass bins lights into 2D screen tiles, usually 16×16 px, using a depth min/max per tile. The fragment shader loops only over its tile's list.
- **Cost:** C (M is possible on newer GPUs).
- **Pitfalls:** Depth discontinuities inside a tile inflate its light list.
- **Engine:** URP Forward+ has no per-object light limit (256 per camera), supports MSAA, and blends reflection probes. Godot's Forward+ renderer is the desktop default (Vulkan/D3D12) and uses clustered light culling†.
- **Source:** URP page above; https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html

**Clustered (forward or deferred)**
- **What/why:** Fixes the tiled depth-discontinuity problem.
- **How:**
  - Divide the frustum into a 3D grid (x, y, plus exponential z slices).
  - A compute pass tests lights against cluster AABBs and writes three structures: a global light list, a light-index list, and a light grid of offset/count per cluster.
  - Shaders look up their cluster from screen xy and log(z).
- **Cost:** C/H.
- **Pitfalls:** Choosing the slice count, memory for the index list, atomics contention.
- **Engine:** DOOM 2016 uses clustered forward with 16×8×24 = 3072 clusters, and also puts decals and probes in the clusters. Filament uses clustered forward.
- **Source:** https://www.aortiz.me/2018/12/21/CG.html ; https://www.adriancourreges.com/blog/2016/09/09/doom-2016-graphics-study/

**Deferred**
- **What/why:** Decouples geometry from lighting, so lighting is O(objects + lights).
- **How:**
  - Write a G-buffer: albedo, normal, roughness/metal, depth (reconstruct position from depth instead of storing it).
  - Lighting runs as full-screen passes or as light volumes (spheres with back-face culling).
- **Cost:** C+. Bandwidth-heavy on mobile unless kept in tile memory (memoryless).
- **Pitfalls:**
  - No MSAA.
  - Transparency needs a forward pass.
  - Material variety is limited by G-buffer bits.
  - Normal encoding precision.
- **Engine:** URP Deferred has no MSAA, encoded normals, and is incompatible with Subtractive/Shadowmask modes. HDRP and UE5 are deferred by default; UE also has a forward path for VR†.
- **Source:** https://learnopengl.com/Advanced-Lighting/Deferred-Shading

**Visibility buffer**
- **What/why:** Efficient when triangles are tiny (1–10 px) and quad overdraw dominates.
- **How:**
  - Rasterize only a packed u32 of instance and triangle ID.
  - Then classify pixels per material (count plus prefix sum) and run indirect compute material passes.
  - Those passes refetch and transform vertices and compute barycentrics and analytic UV derivatives.
- **Cost:** H.
- **Pitfalls:**
  - Complexity: manual derivatives, storing post-deformation vertices.
  - Overhead on old GPUs.
  - Complex material graphs.
- **Engine:** Nanite renders a visibility buffer. Measured about 32% faster than deferred at 1 px triangle density.
- **Source:** http://filmicworlds.com/blog/visibility-buffer-rendering-with-material-graphs/

---

## 2. Color pipeline

**Linear vs gamma workflow**
- **What/why:** Lighting math is only correct in linear space.
- **How:**
  - Decode sRGB albedo/emissive textures to linear with an sRGB format or sampler.
  - Keep normal, roughness, metal, AO and mask textures linear.
  - Shade in linear; encode to sRGB exactly once at the end, after tonemapping.
- **Cost:** Free with hardware sRGB.
- **Pitfalls:**
  - Double gamma: an sRGB framebuffer plus manual pow(1/2.2).
  - Marking data maps as sRGB.
  - Gamma correction applied to intermediate buffers.
  - Linear attenuation hacks, where inverse-square becomes correct.
- **Engine:** Unity Project Settings > Color Space = Linear; untick sRGB on data textures. Godot 4 and UE are linear by default.
- **Source:** https://learnopengl.com/Advanced-Lighting/Gamma-Correction ; https://docs.unity3d.com/6000.0/Documentation/Manual/linear-color-space.html

**HDR rendering + tonemapping**
- **What/why:** Render scene-referred radiance in float targets (RGBA16F or R11G11B10F), then compress it to display range.
- **How:**
  - Multiply by exposure, then apply the tonemap curve.
  - Apply grading LUT, UI and dither after tonemapping, then encode sRGB.
- **Tonemappers:**
  - **ACES (Narkowicz fit):** `x(2.51x+.03)/(x(2.43x+.59)+.14)`. It is pre-exposed: input 1 maps to about 0.8; multiply by 0.6 for the original curve. It is a luminance-only fit that over-saturates and hue-shifts brights.
  - **AgX:** Film-like curve that desaturates highlights with better hue preservation (no "Notorious Six" skews).
  - **Khronos PBR Neutral:** Maps base color 1:1 up to a threshold, then compresses highlights. 13 lines of GLSL. Meant for product/eCommerce or true-colour PBR; use ACES/AgX for strong HDR or stylized looks.
- **Cost:** M+.
- **Pitfalls:**
  - Tonemapping before MSAA resolve or FXAA (do the reverse).
  - Banding: add dither, use 10-bit.
  - Grading in the wrong space.
- **Engine:** Godot offers Linear/Reinhard/Filmic/ACES/AgX, and adjustments apply after tonemapping. URP offers Neutral/ACES†. UE uses an ACES-based filmic curve by default†.
- **Sources:** https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/ ; https://www.khronos.org/news/press/khronos-pbr-neutral-tone-mapper-released-for-true-to-life-color-rendering-of-3d-products ; https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/3d/environment_and_post_processing.rst

**Exposure / auto-exposure (eye adaptation)**
- **What/why:** Map varying scene brightness to a target middle grey.
- **How:**
  - Build a luminance histogram, about 64–128 log2 bins.
  - Skip the darkest 50–80% and brightest 2–20%, average the rest, and convert to EV.
  - Blend exponentially over time, with different speeds for light and dark adaptation, plus artist EV compensation.
  - For physical cameras use EV100 from aperture, shutter and ISO.
- **Cost:** M+ (compute).
- **Pitfalls:**
  - Simple log-average is dominated by small bright spots.
  - Meter after the opaque pass only, excluding particles, UI and debug.
  - Consider metering illuminance rather than albedo-weighted values.
- **Engine:** Godot auto exposure is Forward+ only. UE has Histogram/Basic modes†. HDRP has physical camera exposure†.
- **Source:** https://knarkowicz.wordpress.com/2016/01/09/automatic-exposure/

---

## 3. PBR shading

**Metal/rough PBR with Cook-Torrance GGX**
- **What/why:** Standard physically based BRDF; materials look plausible under any lighting.
- **How:**
  - f = kd·albedo/π + D·F·G / (4(N·L)(N·V)).
  - D = GGX/Trowbridge-Reitz.
  - G = Smith with Schlick-GGX (or height-correlated Smith).
  - F = Schlick, with F0 = 0.04 for dielectrics and F0 = albedo for metals.
  - kd = (1−F)(1−metallic).
  - α = perceptualRoughness².
- **Cost:** M+. Mobile can use cheaper approximations and fp16.
- **Pitfalls:**
  - Missing energy conservation.
  - Rough surfaces lose energy with single scattering; Filament adds a multiscatter compensation term from its DFG LUT.
  - Clamp min roughness (Filament uses 0.089) for fp16 and specular aliasing.
  - Use physical light units (lux, lm, cd).
- **Engine:** All engines use metal/rough. Unity URP Lit also supports specular workflow. Clear coat is a second lobe.
- **Sources:** https://learnopengl.com/PBR/Theory ; https://google.github.io/filament/Filament.md.html

**IBL: split-sum approximation**
- **What/why:** Image-based ambient specular and diffuse lighting from the environment.
- **How:**
  - Diffuse: irradiance cubemap or L2 spherical harmonics (9 coefficients, one dot product).
  - Specular = prefilteredEnv(R, mip = roughness) × (F0·A + B).
  - The prefiltered env map is GGX-importance-sampled per mip, for example 128² with 5 mips and 1024 samples.
  - A and B come from a 2D BRDF LUT indexed by (N·V, roughness), 512² RG16F.
- **Cost:** M+ (precompute can be offline or at load).
- **Pitfalls:**
  - Bright "fireflies" in low mips: sample a source mip based on the PDF.
  - Cubemap seams: enable seamless cube filtering.
  - SH ringing: apply windowing.
- **Engine:** Reflection probes in all engines; the sky becomes the default env.
- **Sources:** https://learnopengl.com/PBR/IBL/Specular-IBL ; https://www.ppsloan.org/publications/StupidSH36.pdf

**Normal / parallax / parallax occlusion mapping (POM)**
- **What/why:** Surface detail without extra geometry.
- **How:**
  - **Normal maps:** Tangent-space normals with a TBN basis.
  - **Parallax:** Offset UVs along the tangent-space view vector by height.
  - **Steep parallax:** Ray-march fixed layers.
  - **POM:** Linearly interpolate between the layers before and after the hit. Scale layers 8–32 with view angle.
- **Cost:** Normal maps M; POM C (many dependent fetches).
- **Pitfalls:**
  - Silhouettes stay flat.
  - Steep angles show layering and swimming.
  - UV-edge artifacts (discard outside 0..1).
  - Tangent mismatch: use MikkTSpace†.
  - Normal maps must be linear (not sRGB).
- **Engine:** HDRP Lit has POM; UE uses the ParallaxOcclusionMapping material function; Godot has heightmap "deep parallax".
- **Source:** https://learnopengl.com/Advanced-Lighting/Parallax-Mapping

**Triplanar mapping**
- **What/why:** No stretching on cliffs or procedural meshes without UVs.
- **How:** Project the texture along X, Y and Z, and blend by |normal| raised to a sharpness power.
- **Cost:** 3× samples (C, careful on M).
- **Pitfalls:** Normal maps need per-axis swizzle; blend-seam smearing.
- **Source:** https://developer.nvidia.com/gpugems/gpugems3/part-i-geometry/chapter-1-generating-complex-procedural-terrains-using-gpu

---

## 4. Shadows

**Shadow mapping**
- **What/why:** Standard dynamic shadows.
- **How:** Render depth from the light, then compare the receiver's light-space depth to the stored depth.
- **Cost:** M+.
- **Pitfalls:**
  - Acne: use slope-scaled bias such as max(k(1−N·L), min).
  - Peter-panning from too much bias: use normal offset or front-face culling for closed meshes.
  - Outside the light frustum: clamp-to-border white, and treat z > 1 as lit.
  - Use hardware comparison samplers.
- **Source:** https://learnopengl.com/Advanced-Lighting/Shadows/Shadow-Mapping

**PCF (percentage-closer filtering)**
- **What/why:** Soft or anti-aliased edges.
- **How:** Average several depth comparisons. Hardware 2×2 bilinear comparison, Poisson disk, or optimized kernels.
- **Cost:** M+.
- **Pitfalls:** Large kernels need more bias. Pad cascades by half the kernel size.
- **Source:** same as above.

**Cascaded shadow maps (CSM)**
- **What/why:** Directional light over large view distances.
- **How:**
  - Split the view frustum into 2–4 cascades, denser near the camera (log/uniform blend†), each with an ortho shadow map.
  - Choose a cascade by depth interval or by map bounds.
- **Cost:** C (M with 1–2 cascades).
- **Pitfalls:**
  - Shimmering: use fixed-size cascades (fit to bounding sphere), snap to texel increments, keep intervals static.
  - Seams: blend bands between cascades.
  - Derivatives across cascades: compute in light-view space.
  - "Dueling frusta" when the light faces the camera.
- **Engine:** URP 1–4 cascades; Godot DirectionalLight3D splits; UE uses VSM by default in UE5 and CSM otherwise.
- **Source:** https://learn.microsoft.com/en-us/windows/win32/dxtecharts/cascaded-shadow-maps

**PCSS (percentage-closer soft shadows)**
- **What/why:** Contact-hardening soft shadows.
- **How:**
  1. Blocker search averages occluder depths in a region sized by the light.
  2. Penumbra width = (dReceiver − dBlocker) · wLight / dBlocker.
  3. PCF with that kernel size.
- **Cost:** C/H (about 36 + 64 samples in the original demo).
- **Pitfalls:** Noise or banding at low sample counts; expensive with large lights.
- **Source:** https://developer.download.nvidia.com/shaderlibrary/docs/shadow_PCSS.pdf

**VSM / ESM (filterable shadow maps)**
- **What/why:** Prefilterable shadows: mips, blur, anisotropic.
- **How:**
  - VSM stores depth and depth². Mean and variance feed Chebyshev's upper bound P = σ²/(σ² + (t−μ)²).
  - ESM stores exp(c·d)†.
- **Cost:** C.
- **Pitfalls:**
  - VSM light bleeding with multiple occluders: remap with linstep(amount, 1, p), which darkens penumbrae.
  - Needs fp32 or 16-bit pairs.
  - ESM breaks down near contact†.
  - EVSM combines both†.
- **Sources:** https://developer.nvidia.com/gpugems/gpugems3/part-ii-light-and-shadows/chapter-8-summed-area-variance-shadow-maps ; CSM page above.

**Contact / screen-space shadows**
- **What/why:** Small-scale shadow detail that shadow maps miss (feet, wrinkles).
- **How:** Short ray march toward the light through the depth buffer per pixel. Combine with shadow maps.
- **Cost:** C.
- **Pitfalls:** Screen-space only; needs thickness heuristics; can only show off-screen occluders if they are in the depth buffer.
- **Engine:** Days Gone (PS4) was the first to use it for sun shadows; open code from SIGGRAPH 2023. UE has "Contact Shadow Length"; HDRP has Contact Shadows†.
- **Source:** https://www.bendstudio.com/blog/inside-bend-screen-space-shadows/

**Virtual shadow maps (UE5)**
- **What/why:** Uniform high-resolution shadows for open worlds and film-quality assets.
- **How:**
  - 16k×16k virtual map split into 128² pages, allocated from on-screen depth samples.
  - Directional lights use clipmaps, each covering 2× the radius of the previous (about 64 cm to 40 km). Spot lights use one 16k map; point lights use a cube of 16k maps.
  - Static and dynamic pages are cached separately.
  - Soft shadows via SMRT (shadow-map ray tracing) from Source Radius or Source Angle.
- **Cost:** H.
- **Pitfalls:**
  - Designed for Nanite; non-Nanite geometry is expensive.
  - Skinned, WPO or PDO geometry invalidates pages every frame.
  - Inflated bounds plus low sun angles cause invalidation.
- **Source:** https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-shadow-maps-in-unreal-engine

---

## 5. Ambient occlusion

**SSAO**
- **What/why:** Cheap occlusion in creases.
- **How:**
  - Sample a normal-oriented hemisphere kernel (16–64 samples) against depth.
  - Rotate the kernel per pixel with a 4×4 noise texture.
  - A range check (smoothstep on radius) rejects distant occluders.
  - Bilateral blur.
- **Cost:** C (half-res on M).
- **Pitfalls:** Halos at depth edges, banding, per-scene tuning, double-darkening baked AO, must not darken direct light (apply to ambient only).
- **Source:** https://learnopengl.com/Advanced-Lighting/SSAO

**HBAO / HBAO+**
- **What/why:** Better-grounded AO from horizon angles.
- **How:**
  - March about 6 directions × 6 steps in depth to find the horizon angle.
  - AO = sin(h) − sin(t), with attenuation W(r) = 1 − r^0.6.
  - Per-pixel jitter plus cross-bilateral blur; half-res option.
- **Cost:** C (3.5 ms half-res on a GTX 280 in 2008; far less today).
- **Pitfalls:** Edge bleeding, noise, half-res upsampling artifacts.
- **Source:** https://developer.download.nvidia.com/presentations/2008/SIGGRAPH/HBAO_SIG08b.pdf

**GTAO (ground-truth AO)** — the source fetch failed (file too large), so all details are †
- **What/why:** Horizon-based AO with cosine weighting that matches a ray-traced reference.
- **How:** Analytic integration between two horizons per slice direction. A multi-bounce fit from albedo, plus temporal and spatial denoising. Can also produce bent normals and specular occlusion.
- **Cost:** C (about 0.5 ms on PS4 at half-res).
- **Pitfalls:** Needs TAA or a denoiser.
- **Engine:** UE's default SSAO is GTAO-based. Godot's SSAO is a GTAO-like variant.
- **Source attempted:** https://www.activision.com/cdn/research/Practical_Real_Time_Strategies_for_Accurate_Indirect_Occlusion_NEW%20VERSION_COLOR.pdf

---

## 6. Global illumination

**Lightmaps**
- **What/why:** Baked direct and indirect light at minimal runtime cost; best for static scenes and mobile.
- **How:** An offline path tracer writes lightmaps into a non-overlapping UV2 atlas with chart margins. Directional lightmaps add a dominant direction for normal maps†.
- **Cost:** M (fastest).
- **Pitfalls:**
  - Needs UV2.
  - Seams and bleeding (margins, dilation).
  - Texel-density balance.
  - Static only; dynamic objects need probes.
- **Engine:** Unity Progressive Lightmapper (CPU/GPU). Godot LightmapGI (up to 16 bounces, all renderers). UE Lightmass/GPU Lightmass (incompatible with Lumen).
- **Sources:** https://docs.unity3d.com/6000.0/Documentation/Manual/Lightmappers.html ; https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/3d/global_illumination/introduction_to_global_illumination.rst

**Light probes (SH)**
- **What/why:** Baked indirect lighting for dynamic objects.
- **How:** Store L2 SH (9 RGB coefficients) at points; Unity interpolates over a tetrahedral mesh†. Evaluate with a dot product with the SH basis of N.
- **Cost:** M.
- **Pitfalls:** Leaking through walls, sparse placement, per-object (not per-pixel) sampling causes pops on large objects.
- **Engine:** Unity Light Probes, plus Adaptive Probe Volumes (per-pixel). Godot LightmapGI probes. UE Volumetric Lightmap†.
- **Sources:** https://docs.unity3d.com/6000.0/Documentation/Manual/LightProbes.html ; Sloan SH PDF above.

**Reflection probes**
- **What/why:** Local specular IBL.
- **How:** Capture a cubemap at a point and prefilter it per roughness mip. Box/parallax projection corrects for finite room size. Blend between overlapping probes.
- **Cost:** M (baked); real-time capture costs up to 6 scene renders.
- **Pitfalls:** Wrong parallax outside the box, light leaking, seams between probes.
- **Engine:** Unity Box Projection plus Forward+ probe blending. Godot ReflectionProbe (Update "Once" is cheapest). UE Sphere/Box captures.
- **Source:** https://docs.unity3d.com/6000.0/Documentation/Manual/AdvancedRefProbe.html

**Voxel cone tracing / VoxelGI**
- **What/why:** Real-time multi-bounce diffuse and glossy GI.
- **How:** Voxelize the scene into a (sparse) 3D texture or octree, inject direct light, mip it. Trace a few cones whose footprint grows with distance; sample the mip that matches the cone radius.
- **Cost:** C/H (25–70 fps in the 2011 paper).
- **Pitfalls:** Light leaks through thin walls, memory, streaking on slopes, revoxelizing dynamic objects.
- **Engine:** Godot VoxelGI (Forward+ only, bake in under 10 s).
- **Source:** https://research.nvidia.com/publication/2011-09_interactive-indirect-illumination-using-voxel-cone-tracing ; Godot GI page.

**SDFGI (Godot)**
- **What/why:** Automatic semi-real-time GI for large worlds.
- **How:** Cascaded signed-distance-field representation around the camera, ray traced to update probe lighting†.
- **Cost:** C/H (half-res option).
- **Pitfalls:** Visible cascade shifts, GI detail varies with distance, some leaking (enable occlusion).
- **Engine:** Godot 4 Forward+ only; enable in Environment.
- **Source:** Godot GI page above.

**SSIL / SSGI**
- **What/why:** Screen-space one-bounce indirect light from on-screen emissive and lit surfaces.
- **How:** Horizon or ray-march based gather from the color buffer, usually half-res.
- **Cost:** C/H.
- **Pitfalls:** No off-screen contribution, no reflections; meant to complement other GI.
- **Engine:** Godot SSIL (Forward+); HDRP SSGI†.
- **Source:** Godot GI page.

**DDGI (probe-based dynamic diffuse GI)** — paper page fetch failed; details †
- **What/why:** Multi-bounce indirect light with no baking, and minimal leaking.
- **How:** Grid of probes that ray-trace N rays per frame and store irradiance plus depth moments in octahedral atlases. Chebyshev visibility test prevents leaks; hysteresis blends over time.
- **Cost:** H (needs hardware RT or SDF tracing).
- **Pitfalls:** Probes inside geometry (relocate or disable), lag from hysteresis.
- **Engine:** NVIDIA RTXGI (also NRC and SHaRC), RTX branch of UE5.
- **Source:** https://developer.nvidia.com/rtxgi

**Lumen (UE5)**
- **What/why:** Fully dynamic GI and reflections.
- **How:**
  - Screen traces first.
  - Software RT: mesh SDFs for the first 2 m, then the merged global SDF. Or hardware RT against triangles.
  - Hit lighting comes from the Surface Cache: about 12 "cards" per mesh capture material and lighting.
  - Final gather with denoising.
- **Cost:** H. Targets 60 fps on current consoles at High; Epic is about 8 ms at 1080p internal.
- **Pitfalls:**
  - Walls under 10 cm leak.
  - Needs modular geometry.
  - WPO and translucency limits.
  - Not compatible with static lighting or forward shading; no VR.
  - Hardware RT is costly with many overlapping instances.
- **Source:** https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-technical-details-in-unreal-engine

**ReSTIR**
- **What/why:** Direct lighting from millions of dynamic lights with ray tracing. Extended to GI and path tracing as ReSTIR GI/PT†.
- **How:** Each pixel keeps a weighted reservoir of candidate light samples (resampled importance sampling), then reuses reservoirs from the previous frame and from neighbours.
- **Cost:** H. 3.4 M emissive triangles in under 50 ms at 8 rays/px (2020); 6–60× faster than prior unbiased methods.
- **Pitfalls:** Bias vs. correctness in reuse (MIS weights), temporal lag, needs a denoiser.
- **Source:** https://research.nvidia.com/publication/2020-07_spatiotemporal-reservoir-resampling-real-time-ray-tracing-dynamic-direct

**Path tracing**
- **What/why:** Ground truth; offline or reference rendering, or "full RT" modes on top GPUs.
- **How:** Progressive Monte Carlo accumulation while the view is static; any change resets it. AI denoisers (OIDN, OptiX, NNE).
- **Cost:** H only.
- **Pitfalls:** Noise in motion, cost. UE's Path Tracer is explicitly not for gameplay (use Movie Render Queue).
- **Source:** https://dev.epicgames.com/documentation/en-us/unreal-engine/path-tracer-in-unreal-engine

---

## 7. Reflections

**SSR (screen-space reflections)**
- **What/why:** Dynamic reflections of on-screen content.
- **How:**
  - Ray march the reflected ray in view/screen space (coarse steps), then binary-search refine.
  - A thickness tolerance decides hits.
  - Blur or pick a mip by roughness.
  - Fade at screen edges, at max distance, and for rays facing the camera.
  - McGuire-Mara DDA and HZB tracing are faster variants†.
- **Cost:** C.
- **Pitfalls:** Missing off-screen and back-facing content (fall back to probes), streaks, noise.
- **Engine:** Godot SSR is Forward+ only. DOOM layers SSR over cubemaps.
- **Source:** https://lettier.github.io/3d-game-shaders-for-beginners/screen-space-reflection.html

**Planar reflections**
- **What/why:** Exact mirror or water reflections on a single plane.
- **How:** Re-render the scene from a camera mirrored about the plane with an oblique near plane†, into a render texture sampled in screen space.
- **Cost:** About 1 extra scene render (C; low-res on M).
- **Pitfalls:** Doubles draw calls; one plane only; resolution vs. memory.
- **Engine:** HDRP Planar Reflection Probe (Every Frame / On Enable / On Demand). UE Planar Reflection actor†.
- **Source:** https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.0/manual/Planar-Reflection-Probe.html

**Probe reflections**
- See the reflection-probe entry in section 6.

**Ray-traced reflections**
- **What/why:** Correct off-screen reflections.
- **How:** DXR/VK RT rays from the G-buffer; hit shading (or Lumen surface cache); denoise. DLSS Ray Reconstruction can replace the denoiser.
- **Cost:** H.
- **Source:** Lumen page above; https://developer.nvidia.com/rtx/dlss

---

## 8. Anti-aliasing and upscaling

**MSAA**
- **What/why:** Hardware geometric edge AA.
- **How:** Coverage and depth per sample (2–8×), shading once per pixel, then resolve.
- **Cost:** Cheap on mobile TBDR (resolves in tile memory); expensive with deferred.
- **Pitfalls:**
  - Resolving HDR before tonemapping gives aliased bright edges: tonemap per sample, resolve, inverse-tonemap.
  - No help for shader or specular aliasing.
  - Not usable with deferred or Nanite.
- **Source:** https://therealmjp.github.io/posts/msaa-overview/

**FXAA**
- **What/why:** Cheapest post AA.
- **How:** Luma contrast test against N/S/E/W neighbours, search along the edge, sub-pixel blend.
- **Cost:** M (under 1 ms at 1080p on 2010 hardware).
- **Pitfalls:** Must run after tonemapping, in sRGB, with luma in alpha. Blurs texture detail (tune subpix). No temporal stability.
- **Source:** https://developer.download.nvidia.com/assets/gamedev/files/sdk/11/FXAA_WhitePaper.pdf

**SMAA**
- **What/why:** Sharper morphological AA than FXAA.
- **How:** Edge detection (luma, color or depth, with predicated thresholding), pattern search including diagonals and corners, then a blending-weight pass. Variants: 1x, S2x (with MSAA), T2x (temporal), 4x.
- **Cost:** M/C.
- **Pitfalls:** No help for sub-pixel or temporal shimmer without the T variants.
- **Source:** https://www.iryoku.com/smaa/

**TAA**
- **What/why:** Supersampling amortized over frames. Required by modern deferred, RT and noisy effects.
- **How:**
  - Sub-pixel jitter of the projection (Halton).
  - Reproject history with motion vectors (camera plus per-object).
  - Blend about 10% new / 90% old.
  - Reject history with neighbourhood clamp or clip (YCoCg, variance).
  - Bicubic (Catmull-Rom) history sampling.
- **Cost:** C.
- **Pitfalls:**
  - Ghosting (bad or missing motion vectors, transparency, particles).
  - Blur (sharpen, unjitter).
  - Flicker (luma weighting).
  - Disocclusion.
  - Use a negative texture mip bias.
- **Source:** https://www.elopezr.com/temporal-aa-and-the-quest-for-the-holy-trail/

**Temporal upscalers (DLSS / FSR / XeSS)**
- **What/why:** Render at a lower internal resolution and reconstruct to output resolution.
- **Inputs:** Jittered color (pre-tonemap linear), depth, motion vectors, jitter offset, exposure; FSR also takes a reactive/transparency mask.
- **Typical scales:** Quality 1.5×, Balanced 1.7×, Performance 2×, Ultra Performance 3×. XeSS 1.3 differs: Quality 1.7×, Balanced 2.0×, Performance 2.3×.
- **Mip bias:** log2(renderWidth / displayWidth), e.g. −1 at 2×.
- **Jitter sequence length:** at least 8 × scale² (72 for 3×).
- **Variants:**
  - **DLSS:** RTX tensor cores; transformer models; Super Resolution, DLAA, Ray Reconstruction, Multi Frame Generation (RTX 50).
  - **FSR 3:** Cross-vendor; frame generation works best from 60+ fps base, avoid under 30; needs a UI composition mode.
  - **XeSS:** XMX path on Intel, DP4a path elsewhere (SM 6.4).
- **Pitfalls:**
  - Upscaling after tonemapping, UI or post (do it before post).
  - Missing motion vectors for particles or animated UVs.
  - Hardcoded ratios.
  - Noisy RT input.
- **Engine:** UE TSR and plugins; Unity HDRP/URP STP† and DLSS/FSR; Godot 4 FSR 2 and TAA†.
- **Sources:** https://developer.nvidia.com/rtx/dlss ; https://gpuopen.com/fidelityfx-superresolution-3/ ; https://www.intel.com/content/www/us/en/developer/articles/technical/xess-sr-developer-guide.html

---

## 9. Post-processing

Order (typical): opaque → SSAO/SSR → transparent → TAA/upscale → DOF → motion blur → bloom → exposure/tonemap → LUT → vignette, grain, CA → UI.

**Bloom**
- **What/why:** HDR glow.
- **How:**
  - **Classic:** Bright-pass threshold, separable Gaussian ping-pong, add before tonemapping.
  - **Modern (COD:AW):** 13-tap downsample chain with a Karis average on the first mip against fireflies, then a 3×3 tent upsample chain. No threshold; lerp about 0.04 into HDR.
- **Cost:** M (fewer mips) to C.
- **Pitfalls:** Fireflies or flicker, thresholds causing hard edges, adding bloom after tonemapping.
- **Sources:** https://learnopengl.com/Advanced-Lighting/Bloom ; https://learnopengl.com/Guest-Articles/2022/Phys.-Based-Bloom

**Depth of field**
- **What/why:** Lens focus.
- **How:** Circle of confusion from depth and focus parameters. Downsample, blur the CoC to handle foreground spill, then a variable blur or bokeh gather (separate near and far layers).
- **Cost:** C (Gaussian on M).
- **Pitfalls:** In-focus objects bleeding into the background, halos, weak foreground blur.
- **Engine:** URP: Gaussian for mobile, Bokeh for desktop.
- **Source:** https://developer.nvidia.com/gpugems/gpugems3/part-iv-image-effects/chapter-28-practical-post-process-depth-field

**Motion blur**
- **What/why:** Hides low frame rates and conveys speed.
- **How:** Per-pixel velocity (current vs. previous view-projection, plus per-object velocity buffer), sample along it. Tile max-velocity variants are used in production†.
- **Cost:** C.
- **Pitfalls:** Camera-only versions miss moving objects; edge artifacts; avoid in VR.
- **Source:** https://developer.nvidia.com/gpugems/gpugems3/part-iv-image-effects/chapter-27-motion-blur-post-processing-effect

**Color grading LUT**
- **What/why:** Art-directed look.
- **How:**
  - 3D LUT (16³–65³) sampled trilinearly with a half-texel scale/offset: (N−1)/N·c + 0.5/N.
  - Apply after tonemapping (LDR), or with a log "shaper" for HDR grading.
- **Cost:** M.
- **Pitfalls:** Missing half-texel correction, 8-bit banding, can't do spatial operations.
- **Engine:** Godot 3D LUT (17/33/65³) after tonemap; URP LDR/HDR grading modes†.
- **Source:** https://developer.nvidia.com/gpugems/gpugems2/part-iii-high-quality-rendering/chapter-24-using-lookup-tables-accelerate-color

**Vignette / chromatic aberration / lens distortion / film grain**
- **What/why:** Lens and film look.
- **How:**
  - Vignette: radial darkening.
  - CA: offset R/B samples radially.
  - Distortion: radial UV warp.
  - Grain: animated noise added after tonemapping, scaled by luminance†.
- **Cost:** M.
- **Pitfalls:** Avoid CA, distortion and motion blur in VR (sickness). Vignette is fine in VR.
- **Engine:** URP lists Bloom (no HQ filter), CA, color grading, lens distortion and vignette as mobile-friendly.
- **Source:** https://docs.unity3d.com/6000.0/Documentation/Manual/urp/integration-with-post-processing.html

---

## 10. Fog, volumetrics, atmosphere, clouds

**Distance / height fog**
- **What/why:** Depth cue and atmosphere.
- **How:**
  - Distance fog: 1 − exp(−b·t).
  - Height fog: density a·e^(−b·y), integrated analytically along the ray (one extra divide).
  - Split extinction and inscatter (per-RGB); tint toward sun colour by dot(viewDir, sunDir).
- **Cost:** M.
- **Pitfalls:** Monochrome flat fog; division by zero for horizontal rays.
- **Engine:** UE Exponential Height Fog costs about two fog layers; Start Distance can cut cost 50%.
- **Sources:** https://iquilezles.org/articles/fog/ ; https://dev.epicgames.com/documentation/en-us/unreal-engine/exponential-height-fog-in-unreal-engine

**Froxel volumetric fog**
- **What/why:** Lit participating media with local lights and shadows.
- **How:**
  - A camera-aligned 3D grid (e.g. 160×90×64, exponential depth).
  - Per-froxel density from global settings and fog volumes, lighting from shadowed lights, jittered.
  - Temporal reprojection, then a front-to-back integration pass.
  - Apply by sampling the 3D texture at each pixel's depth.
- **Cost:** C.
- **Pitfalls:** Ghosting or trails from temporal reprojection on moving lights and volumes, finite range (combine with analytic fog), aliasing.
- **Engine:** Godot volumetric fog and FogVolume nodes are Forward+ only (the Godot environment page lists it for all renderers, but the dedicated volumetric fog page says Forward+ only, so trust the dedicated page). UE Volumetric Fog. HDRP Volumetric Fog with Local Volumetric Fog†.
- **Sources:** https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/3d/volumetric_fog.rst ; https://www.ea.com/frostbite/news/physically-based-unified-volumetric-rendering-in-frostbite

**God rays (screen-space radial blur)**
- **What/why:** Cheap light shafts.
- **How:** Occlusion mask (occluders black, sky bright), radial blur toward the light's screen position with density, weight, decay and exposure parameters.
- **Cost:** M/C.
- **Pitfalls:** Breaks when the sun is off-screen or behind the camera; shafts flicker at screen edges and can appear in front of foreground objects. Froxel fog is the physically based alternative.
- **Source:** https://developer.nvidia.com/gpugems/gpugems3/part-ii-light-and-shadows/chapter-13-volumetric-light-scattering-post-process

**Atmosphere: Bruneton precomputed scattering**
- **What/why:** Physically based sky and aerial perspective with multiple scattering.
- **How:** Precompute transmittance, single and multiple scattering (4D), and irradiance LUTs on the GPU. Look them up at runtime. 2017 version adds ozone, spectral-to-RGB conversion and light shafts.
- **Cost:** C (precompute cost on atmosphere change).
- **Pitfalls:** Re-precompute needed for parameter changes; 4D parameterization artifacts near the horizon.
- **Source:** https://ebruneton.github.io/precomputed_atmospheric_scattering/

**Atmosphere: Hillaire 2020 (UE Sky Atmosphere)**
- **What/why:** Scalable, fully dynamic, mobile-capable.
- **How:** Small per-frame LUTs: transmittance; multiple-scattering approximation (no iterative precompute); sky-view (lat-long, ray-marched); aerial perspective (froxel 3D texture). Allows time-of-day and planet changes†.
- **Cost:** M–C.
- **Pitfalls:** Sky-view LUT resolution near the horizon†.
- **Engine:** UE SkyAtmosphere; HDRP Physically Based Sky†.
- **Source:** https://github.com/sebh/UnrealEngineSkyAtmosphere

**Volumetric clouds (Horizon Zero Dawn)**
- **What/why:** Art-directable, evolving cloudscapes on a 2 ms budget.
- **How:**
  - Noise textures: 128³ Perlin-Worley base, 32³ Worley detail erosion, 2D curl for distortion.
  - Weather map (R coverage, G precipitation, B cloud type) plus height gradients per type.
  - Lighting: Beer's law, "powder" darkening, Henyey-Greenstein phase for silver lining.
  - Ray march 64–128 steps, cheap until a hit then detailed; 6 cone light samples (the last one far away).
  - Temporal reprojection updates 1 of 16 pixels per 4×4 block per frame, about 10× faster.
- **Cost:** C (2 ms on PS4).
- **Pitfalls:** Reprojection smear during fast camera moves; banding (use blue-noise jitter).
- **Engine:** UE Volumetric Cloud; HDRP Volumetric Clouds†; Godot needs a custom sky shader†.
- **Source:** https://www.advances.realtimerendering.com/s2015/The%20Real-time%20Volumetric%20Cloudscapes%20of%20Horizon%20-%20Zero%20Dawn%20-%20ARTR.pdf

---

## 11. Water

**Gerstner waves**
- **What/why:** Peaked waves from a few analytic functions.
- **How:** Sum of waves that displace xz toward crests (steepness Q) as well as y. Analytic normals and tangents from partial derivatives. Qi = Q/(wi·Ai·numWaves).
- **Cost:** M (vertex shader).
- **Pitfalls:** Σ Qi·wi·Ai > 1 makes crests loop (negative normals). Visible repetition; add normal-map detail.
- **Source:** https://developer.nvidia.com/gpugems/gpugems/part-i-natural-effects/chapter-1-effective-water-simulation-physical-models

**FFT ocean (Tessendorf)**
- **What/why:** Statistically realistic ocean.
- **How:**
  - Phillips (or JONSWAP†) spectrum h0(k) with Gaussian randoms.
  - Evolve h(k,t) with dispersion ω = √(gk), inverse FFT to a heightfield (128²–2048²).
  - Choppy horizontal displacement D = Σ −i(k/|k|)h.
  - Jacobian < 0 marks folds, used for foam.
  - Tiles seamlessly; layer cascades at different scales to hide repetition†.
- **Cost:** C (compute FFT).
- **Pitfalls:** Visible tiling at the horizon, choppiness self-intersection.
- **Engine:** HDRP Water System is FFT-based with swell/agitation/ripple bands, caustics, foam, underwater and current maps†.
- **Sources:** https://jtessen.people.clemson.edu/reports/papers_files/coursenotes2004.pdf ; https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.0/manual/water.html

**Refraction and depth color**
- **How:** Sample the opaque-scene copy (grab pass, URP Opaque Texture, Godot SCREEN_TEXTURE†) with UVs offset by the normal. Underwater fog = exp2(−density · depthDiff).
- **Cost:** M+ (one screen copy).
- **Pitfalls:** Refracted UVs sampling foreground objects: if the depth difference is negative, use unrefracted UVs. Align to texels.
- **Source:** https://catlikecoding.com/unity/tutorials/flow/looking-through-water/

**Caustics**
- **How:** Cheap: project an animated (wave-theory) caustic texture onto underwater surfaces, additive. Better: refract rays per pixel from wave normals (Snell) and measure convergence.
- **Cost:** M (texture) / C.
- **Source:** https://developer.nvidia.com/gpugems/gpugems/part-i-natural-effects/chapter-2-rendering-water-caustics

**Foam**
- **How:** Jacobian fold mask (FFT), plus shoreline foam from scene depth difference, plus a decaying accumulation texture†.
- **Source:** Tessendorf notes above.

---

## 12. Terrain

**Heightmap terrain + splatting**
- **How:** Grid mesh displaced by a heightmap. A splat/control map (RGBA weights per layer, 4 layers per map) blends tiling material layers. Height-based blending gives sharper transitions†.
- **Cost:** M (4 layers) to C (8+).
- **Pitfalls:** Sample count grows with layer count, tiling repetition (use macro variation and stochastic sampling†), stretching on cliffs (use triplanar).
- **Source:** triplanar page above.

**Virtual texturing (terrain/decals)**
- **What/why:** Bake splats and decals into a streamed virtual texture: one sample at runtime instead of N layers.
- **How:**
  - A feedback pass writes the required pages.
  - Page cache atlas plus indirection texture.
  - Pages are composited on the GPU and cached.
- **Results:**
  - Far Cry 4 adaptive VT: 10 texels/cm over a 10×10 km world, with decals baked in.
  - DOOM: 16k×8k atlas of 128² tiles.
- **Cost:** C.
- **Pitfalls:** Page pop-in latency, feedback cost, anisotropic filtering needs borders.
- **Engine:** UE Runtime Virtual Texture† and Streaming VT; HDRP Streaming VT (experimental)†.
- **Sources:** https://www.gdcvault.com/play/1021761/Adaptive-Virtual-Texture-Rendering-in ; DOOM study above.

**Geometry clipmaps**
- **What/why:** View-centred terrain LOD with constant cost.
- **How:** Nested regular grids (e.g. 255²) as hollow rings, height fetched in the vertex shader, toroidal update of only the L-shaped new region, alpha blend across transition regions to avoid cracks and pops.
- **Cost:** M/C.
- **Pitfalls:** Vertex texture fetch bottleneck; seams without transition blending.
- **Source:** https://developer.nvidia.com/gpugems/gpugems2/part-i-geometric-complexity/chapter-2-terrain-rendering-using-gpu-based-geometry

**Tessellation / displacement** — no source opened, all †
- **How:** Hull/domain shaders or a compute-subdivided mesh adaptively tessellate by screen-space edge length and displace by a heightmap.
- **Cost:** C/H.
- **Pitfalls:** Cracks at patch edges (match edge factors), poor GPU efficiency at low factors, not supported on many mobile GPUs or Metal paths.
- **Engine:** UE5 replaced classic tessellation with Nanite tessellation/displacement (5.3+); HDRP Lit Tessellation; Godot 4 has no hardware tessellation.

---

## 13. Vegetation

**GPU instancing**
- **How:** One draw call for many copies, with a per-instance transform buffer. GPU culling feeds an indirect draw.
- **Cost:** M+.
- **Pitfalls:** Per-instance data limits; SRP Batcher vs. instancing conflicts in Unity (decals use property blocks and instancing).
- **Source:** see GPU-driven entry in section 14.

**Wind animation**
- **How:** Vertex shader bending with layered noise frequencies:
  - Trunk sway (whole-tree bend scaled by height).
  - Branch motion (weights and phase from vertex colors).
  - Leaf flutter (high-frequency).
  - Hierarchical rotations can be blended between branch and parent.
- **Cost:** M.
- **Pitfalls:** Stretching (preserve length), mismatch with shadow and motion-vector passes (must run in every pass, including the previous-frame position for TAA).
- **Source:** https://developer.nvidia.com/gpugems/gpugems3/part-i-geometry/chapter-6-gpu-generated-procedural-wind-animations-trees

**Alpha-to-coverage / alpha test**
- **How:**
  - A2C turns alpha into an MSAA coverage mask: soft edges with correct depth sorting.
  - Fix mip alpha shrinking: alpha *= 1 + mipLevel × 0.25.
  - Sharpen: (a − cutoff) / fwidth(a) + 0.5.
- **Cost:** Needs MSAA (good on mobile TBDR).
- **Pitfalls:**
  - Alpha test/discard disables early-Z and HSR on TBDR: use a depth prepass or opaque cutout meshes.
  - Foliage vanishes at distance without the mip fix.
  - Without MSAA use alpha hash (dithered) plus TAA.
- **Source:** https://bgolus.medium.com/anti-aliased-alpha-test-the-esoteric-alpha-to-coverage-8b177335ae4f

**Impostors / billboards**
- **How:** Final LOD is a camera-facing quad. Octahedral impostors capture N×N views on a (hemi-)octahedron into an atlas, blend the 3 nearest frames, and use depth for parallax and shadows†.
- **Cost:** M.
- **Pitfalls:** View-switch popping, lighting mismatch (bake normals and depth), atlas memory.
- **Engine:** Unity LOD Group supports a Billboard Asset for the last LOD.
- **Source:** https://docs.unity3d.com/6000.0/Documentation/Manual/LevelOfDetail.html (the shaderbits octahedral impostor page returned no body text).

---

## 14. LOD and culling

**Discrete LOD + cross-fade**
- **How:** Swap meshes by screen-relative size; dither cross-fade to hide pops†; HLOD merges distant clusters†.
- **Cost:** M.
- **Pitfalls:** Popping, shadow LOD mismatch.
- **Source:** Unity LOD page above.

**Frustum culling**
- **How:** Test bounding spheres or AABBs against 6 planes, on the CPU or in GPU compute.
- **Cost:** M.
- **Source:** see GPU-driven entry below.

**Occlusion culling / HZB**
- **How:**
  - Baked PVS (Unity Umbra†), or a hierarchical-Z depth pyramid.
  - Two-phase: test against last frame's HZB, draw visible, rebuild the HZB, then retest the rejected set to fix false negatives.
- **Cost:** C.
- **Pitfalls:** One-frame latency pops without the two-phase scheme; conservative bounds needed.
- **Source:** https://advances.realtimerendering.com/s2015/aaltonenhaar_siggraph2015_combined_final_footer_220dpi.pdf

**GPU-driven rendering**
- **How:** Split meshes into about 64-vertex clusters. A compute pass culls instance, then cluster (frustum, HZB, backface cone), then triangle (backface, small-primitive). It writes MultiDrawIndexedInstancedIndirect args; virtual texturing or bindless removes state changes.
- **Results:** Draw calls fall by 1–2 orders of magnitude; ~10× more objects; 20–40% of triangles culled.
- **Cost:** C/H.
- **Pitfalls:** Debugging complexity, needs bindless or atlases.
- **Engine:** Unity GPU Resident Drawer†, UE Nanite, Godot none built-in†.
- **Source:** Aaltonen/Haar link above.

**Mesh shaders**
- **How:** An optional task (amplification) shader culls meshlets and picks LOD, then emits mesh-shader workgroups. Each emits up to 64 vertices / 126 triangles. Index data is about 75% of the original.
- **Cost:** H (Turing+, RDNA2+, DX12 Ultimate / VK_EXT_mesh_shader).
- **Pitfalls:** Vendor-specific optimal sizes; fallback path needed.
- **Source:** https://developer.nvidia.com/blog/introduction-turing-mesh-shaders/

**Nanite (UE5)**
- **What/why:** Virtualized geometry; film-quality meshes with automatic LOD.
- **How:**
  - Hierarchical cluster DAG built at import; clusters chosen per view by screen error.
  - Streamed and compressed.
  - Hardware raster for large triangles, software (compute) raster for small ones, into a visibility buffer.
  - Pairs with VSM.
- **Cost:** H (DX12 SM6).
- **Pitfalls:**
  - Opaque and masked only; no translucency.
  - No morph targets, MSAA, forward, or stereo VR.
  - WPO costs.
  - Ray tracing uses fallback meshes.
- **Source:** https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine

---

## 15. Skinning and animation

**GPU skinning (linear blend skinning)**
- **How:** Up to 4 bone indices and weights per vertex, a bone matrix palette (uniform buffer or structured buffer). v = Σ wᵢ·Mᵢ·v. Compute pre-skinning caches results for multiple passes†.
- **Cost:** M+.
- **Pitfalls:** Candy-wrapper and volume loss at twisting joints (dual-quaternion skinning†), missing previous-frame skinning for motion vectors, transform normals too.
- **Source:** https://learnopengl.com/Guest-Articles/2020/Skeletal-Animation

**Blend shapes / morph targets**
- **How:** Store sparse per-vertex position, normal and tangent deltas; final = base + Σ wᵢ·Δᵢ. Evaluate in the vertex shader from one buffer indexed by vertex ID (faster than stream-out: 2.4× at 50 shapes), or in compute.
- **Cost:** M+.
- **Pitfalls:** Memory, normals need deltas too, apply before skinning.
- **Engine:** Nanite does not support morph targets.
- **Source:** https://developer.nvidia.com/gpugems/gpugems3/part-i-geometry/chapter-3-directx-10-blend-shapes-breaking-limits

---

## 16. Stylized / NPR

**Toon / cel shading**
- **How:** Quantize N·L with step or smoothstep (narrow band), or look up a 1D or 2D ramp texture. Thresholded Blinn-Phong specular. Rim light = (1 − N·V) masked by N·L. Ambient floor so shadows aren't black. Still sample shadow maps.
- **Cost:** M.
- **Pitfalls:** Noisy terminator from bad normals (edit or transfer normals), self-shadow acne is very visible (larger bias), tonemapper alters ramp colors (use neutral or none).
- **Source:** https://roystan.net/articles/toon-shader/

**Guilty Gear Xrd / ASW techniques**
- **How:**
  - Hand-edited vertex normals control the light/shadow terminator.
  - Inverted-hull outlines use a second set of "outline normals" stored in tangents, so silhouettes stay smooth while shading normals are edited.
  - Outline width from vertex-color alpha (thin hair, thick muscles), scaled by camera distance and FOV.
  - Push outline vertices away in depth to hide lines in creases.
  - Threshold shading, ILM texture channels for shadow bias and specular, inner "Motomura lines" drawn in UV-aligned texture, held-frame (limited) animation† — none of these four are in the opened deck.
- **Cost:** M.
- **Source:** https://image.docswell.com/s/ASW_Academy/5LVY67-GG-Toonline-Eng

**Genshin-style anime shading**
- **How:**
  - Ramp textures per material and time of day.
  - Lightmap or ILM channels (AO, shadow threshold, specular mask).
  - Face SDF shadow map: a precomputed threshold texture compared against the light angle relative to face forward, giving clean nose and cheek shadows independent of normals. Requires face forward/right vectors.
  - Screen-space depth-offset rim light†.
  - Inverted-hull outlines.
- **Cost:** M.
- **Pitfalls:** Face SDF overrides received shadows, which become unstable up close.
- **Source:** https://github.com/NoiRC256/URPSimpleGenshinShaders

**Outlines: inverted hull**
- **How:** Second pass with front faces culled, vertices extruded along (smoothed) normals in clip or view space for constant width.
- **Cost:** M (doubles vertex work and draws).
- **Pitfalls:** Gaps at hard edges (use averaged normals), no inner lines, issues with transparency.
- **Source:** Docswell deck above.

**Outlines: post-process edge detection**
- **How:** Roberts cross or Sobel on depth (threshold scaled by depth and by view angle N·V to avoid false edges on grazing surfaces) plus on normals, combined with max(). Optional object-ID or color edges.
- **Cost:** M/C (needs depth and normals textures).
- **Pitfalls:** Line width fixed in pixels, false edges on slopes, aliasing (run before TAA or AA the lines).
- **Source:** https://roystan.net/articles/outline-shader/

**Hatching (tonal art maps)**
- **How:** Prerendered, mip-mapped hatch textures nested by tone (lighter strokes are a subset of darker) and by mip, so strokes don't swim. Blend 6 tones from per-vertex weights (two dot products). Lapped textures handle arbitrary surfaces.
- **Cost:** M.
- **Source:** https://hhoppe.com/hatching.pdf

---

## 17. Materials and special surfaces

**Decals**
- **How:**
  - Projected-box (deferred / screen-space): reconstruct position from depth inside the box, project UVs, write into G-buffer or DBuffer before lighting.
  - Clustered forward decals: decal atlas plus cluster lists (DOOM).
  - Mesh decals.
- **Cost:** M (screen space) to C.
- **Pitfalls:** Stretching on surfaces parallel to the projection (fade by normal angle), no decals on transparents, normal blending, sorting.
- **Engine:** URP Decal Renderer Feature (DBuffer or Screen Space; not on transparent surfaces; atlas plus instancing). HDRP Decal Projector. UE deferred decals. Godot Decal node.
- **Sources:** https://docs.unity3d.com/6000.0/Documentation/Manual/urp/renderer-feature-decal.html ; DOOM study.

**Subsurface scattering (skin)**
- **How:**
  - **Texture-space diffusion:** Sum of 6 Gaussians, separable blurs in UV space (84 vs. 4096 taps). Translucent shadow maps for thin areas such as ears.
  - **Screen-space separable SSS (Jimenez):** Two 1D passes with a separable kernel, about 7 samples per pixel, under 0.5 ms. Stencil-masked; transmission via shadow-map thickness.
- **Cost:** C.
- **Pitfalls:** Blur across depth discontinuities (depth-aware kernel), loss of albedo detail (pre- or post-scatter texturing), cost at close-up.
- **Engine:** UE Subsurface Profile; HDRP Diffusion Profile†.
- **Sources:** https://www.iryoku.com/separable-sss/ ; https://developer.nvidia.com/gpugems/gpugems3/part-iii-rendering/chapter-14-advanced-techniques-realistic-real-time-skin

**Hair / fur**
- **How:**
  - **Cards:** Kajiya-Kay or Marschner-style anisotropic specular using the tangent. Two shifted highlights (tangent shifted along the normal by a noise texture).
  - **Sorting:** Static inside-to-outside index order. A depth prepass with alpha test enables early-Z, then a blended pass.
  - **Strands:** UE Groom renders hundreds of thousands of strands with LOD to cards and meshes.
  - **Shell texturing for fur**†.
- **Cost:** M (cards) to H (strands).
- **Pitfalls:** Sorting and transparency artifacts, aliasing (TAA or A2C), shadow self-occlusion (deep opacity maps†).
- **Sources:** https://web.engr.oregonstate.edu/~mjb/cs519/Projects/Papers/HairRendering.pdf ; https://dev.epicgames.com/documentation/en-us/unreal-engine/hair-rendering-and-simulation-in-unreal-engine

---

## 18. Particles and VFX

**GPU particles**
- **How:** Simulate (spawn, update, die) in compute with append/consume buffers. Sort (bitonic) only if blending needs it. Indirect draw. Millions of particles are possible†.
- **Cost:** C (M with compute).
- **Pitfalls:** Overdraw dominates cost; lighting particles is expensive (DOOM uses a particle lighting atlas).
- **Engine:** Unity VFX Graph (GPU, compute required) vs. the CPU Particle System; UE Niagara GPU emitters; Godot GPUParticles3D†.
- **Source:** https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.0/manual/index.html (overview only).

**Flipbooks** — no source opened, all †
- **How:** Atlas of animation frames; blend frame N to N+1; motion-vector flipbooks distort UVs toward the next frame for smooth playback with fewer frames.
- **Pitfalls:** Mip bleeding between atlas cells (padding).

**Soft particles**
- **What/why:** Remove hard intersection lines with geometry.
- **How:** Fade alpha by a contrast curve over (sceneDepth − particleDepth).
- **Cost:** Needs a depth texture; measured 25–60% overhead in the 2007 paper; cheap today.
- **Source:** https://developer.download.nvidia.com/whitepapers/2007/SDK10/SoftParticles_hi.pdf

**Low-resolution particle buffer**
- **How:** Render particles at 1/4 or 1/16 resolution against a max-downsampled depth. Upsample, re-rendering Sobel-detected edges at full resolution via stencil. Separate alpha blending.
- **Result:** About 2.4× faster at 4× fewer pixels.
- **Source:** https://developer.nvidia.com/gpugems/gpugems3/part-iv-image-effects/chapter-23-high-speed-screen-particles

---

## 19. Transparency

**Sorted alpha blending**
- **How:** Draw opaque first; draw transparents back-to-front per object, depth test on, depth write off.
- **Cost:** M.
- **Pitfalls:**
  - Per-object sorting fails for intersecting or overlapping objects.
  - Self-overlap.
  - No SSR, SSAO or DOF data for transparents.
  - Prefer alpha scissor/hash where possible.
- **Engine:** Godot sorts by node position (use render priority). Unity uses render queue and sorting priority.
- **Source:** https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/3d/3d_rendering_limitations.rst

**Weighted Blended OIT**
- **How:**
  - RGBA16F accumulation target (additive, Σ C·w), R8 revealage target (multiplicative, Π(1−α)).
  - Weight from depth and alpha.
  - Composite: accum.rgb / accum.a blended over by revealage.
- **Cost:** M/C.
- **Pitfalls:** Approximate (wrong for high opacity), weight tuning per depth range, no refraction.
- **Exact alternatives:** Per-pixel linked lists or depth peeling (H)†.
- **Source:** https://casual-effects.blogspot.com/2014/03/weighted-blended-order-independent.html

---

## 20. Optimization and profiling

**Mobile TBDR**
- **How:**
  - On-chip tile memory.
  - Load/store actions: use clear or don't-care and avoid loads.
  - Memoryless (transient) attachments for depth and G-buffer.
  - MSAA resolves in tile, so 4× MSAA is cheap.
  - Hardware HSR, which discard and alpha test defeat.
  - Programmable blending / framebuffer fetch / subpasses for deferred in tile memory.
- **Rules:**
  - Avoid mid-frame render target switches and readbacks.
  - Minimize full-screen post passes (merge them).
  - Use fp16.
  - Prefer opaque.
  - Draw front-to-back.
- **Cost:** n/a.
- **Source:** https://developer.apple.com/documentation/metal/tailor-your-apps-for-apple-gpus-and-tile-based-deferred-rendering (the Arm Mali guide redirected and returned no content).

**General GPU optimization checklist**
- Draw calls and state changes: batch, instance, SRP Batcher, GPU-driven.
- Overdraw: depth prepass, sort front-to-back, cap particle size.
- Bandwidth: compressed textures (BC/ASTC), mipmaps, R11G11B10F instead of RGBA16F, half-res effects.
- Quad overdraw from tiny triangles: LOD.
- ALU: fp16, precompute into LUTs.
- Temporal amortization: TAA, checkerboard, cloud reprojection 1/16.
- Profile before optimizing.
- **Source:** Aaltonen/Haar link; DOOM study (1331 draws, 50 render targets in under 16 ms).

**RenderDoc**
- **How:**
  - Launch the app through RenderDoc and capture with F12 or PrintScreen.
  - Event Browser lists EIDs.
  - Texture Viewer shows render targets, mips, channels, overlays.
  - Pipeline State shows bound shaders, resources and state.
  - Mesh Viewer shows vertex shader input and output.
  - Supports shader debugging.
- **Other tools:** Nsight Graphics, PIX, Xcode GPU capture, Arm Mobile Studio / Snapdragon Profiler for counters†.
- **Pitfalls:** RenderDoc is a frame debugger, not a precise timer (use vendor profilers for timings).
- **Source:** https://renderdoc.org/docs/getting_started/quick_start.html

---

## 21. Neural / novel representations

**3D Gaussian Splatting**
- **What/why:** Photoreal captured scenes rendered in real time.
- **How:**
  - Millions of anisotropic 3D Gaussians (position, covariance, opacity, SH color†) optimized from SfM points with adaptive densify/prune.
  - Rendered by projecting to 2D splats, tile-based depth sort, and front-to-back alpha blending.
  - At least 100 fps at 1080p.
- **Cost:** C/H (mobile possible with compression†).
- **Pitfalls† (not stated on the opened page):** Large memory (hundreds of MB), baked lighting (no relighting), sorting cost and popping, hard to mix with depth-buffered meshes and shadows, view-dependent artifacts away from captured views.
- **Engine†:** Community plugins for UE, Unity and Godot; UE also has third-party support†.
- **Source:** https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/

---

## Sources actually opened (successful fetches)

1. https://learnopengl.com/PBR/Theory
2. https://learnopengl.com/PBR/IBL/Specular-IBL
3. https://google.github.io/filament/Filament.md.html
4. https://learnopengl.com/Advanced-Lighting/Gamma-Correction
5. https://learnopengl.com/Advanced-Lighting/Deferred-Shading
6. https://learnopengl.com/Advanced-Lighting/Shadows/Shadow-Mapping
7. https://learn.microsoft.com/en-us/windows/win32/dxtecharts/cascaded-shadow-maps
8. https://developer.download.nvidia.com/shaderlibrary/docs/shadow_PCSS.pdf
9. https://developer.nvidia.com/gpugems/gpugems3/part-ii-light-and-shadows/chapter-8-summed-area-variance-shadow-maps
10. https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-shadow-maps-in-unreal-engine
11. https://learnopengl.com/Advanced-Lighting/SSAO
12. https://developer.download.nvidia.com/presentations/2008/SIGGRAPH/HBAO_SIG08b.pdf
13. https://www.aortiz.me/2018/12/21/CG.html
14. http://filmicworlds.com/blog/visibility-buffer-rendering-with-material-graphs/
15. https://www.khronos.org/news/press/khronos-pbr-neutral-tone-mapper-released-for-true-to-life-color-rendering-of-3d-products
16. https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/
17. https://knarkowicz.wordpress.com/2016/01/09/automatic-exposure/
18. https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/3d/environment_and_post_processing.rst
19. https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/3d/global_illumination/introduction_to_global_illumination.rst
20. https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/3d/volumetric_fog.rst
21. https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/3d/3d_rendering_limitations.rst
22. https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html (partial)
23. https://docs.unity3d.com/6000.0/Documentation/Manual/urp/rendering-paths-comparison.html
24. https://docs.unity3d.com/6000.0/Documentation/Manual/linear-color-space.html
25. https://docs.unity3d.com/6000.0/Documentation/Manual/urp/integration-with-post-processing.html
26. https://docs.unity3d.com/6000.0/Documentation/Manual/AdvancedRefProbe.html
27. https://docs.unity3d.com/6000.0/Documentation/Manual/urp/renderer-feature-decal.html
28. https://docs.unity3d.com/6000.0/Documentation/Manual/LightProbes.html
29. https://docs.unity3d.com/6000.0/Documentation/Manual/Lightmappers.html
30. https://docs.unity3d.com/6000.0/Documentation/Manual/LevelOfDetail.html
31. https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.0/manual/water.html
32. https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.0/manual/Planar-Reflection-Probe.html
33. https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.0/manual/index.html
34. https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-technical-details-in-unreal-engine
35. https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine
36. https://dev.epicgames.com/documentation/en-us/unreal-engine/exponential-height-fog-in-unreal-engine
37. https://dev.epicgames.com/documentation/en-us/unreal-engine/path-tracer-in-unreal-engine
38. https://dev.epicgames.com/documentation/en-us/unreal-engine/hair-rendering-and-simulation-in-unreal-engine
39. https://developer.nvidia.com/rtxgi
40. https://research.nvidia.com/publication/2020-07_spatiotemporal-reservoir-resampling-real-time-ray-tracing-dynamic-direct
41. https://research.nvidia.com/publication/2011-09_interactive-indirect-illumination-using-voxel-cone-tracing
42. https://www.ppsloan.org/publications/StupidSH36.pdf
43. https://ebruneton.github.io/precomputed_atmospheric_scattering/
44. https://github.com/sebh/UnrealEngineSkyAtmosphere
45. https://www.guerrilla-games.com/read/the-real-time-volumetric-cloudscapes-of-horizon-zero-dawn
46. https://www.advances.realtimerendering.com/s2015/The%20Real-time%20Volumetric%20Cloudscapes%20of%20Horizon%20-%20Zero%20Dawn%20-%20ARTR.pdf
47. https://www.ea.com/frostbite/news/physically-based-unified-volumetric-rendering-in-frostbite
48. https://iquilezles.org/articles/fog/
49. https://developer.nvidia.com/gpugems/gpugems3/part-ii-light-and-shadows/chapter-13-volumetric-light-scattering-post-process
50. https://developer.nvidia.com/gpugems/gpugems/part-i-natural-effects/chapter-1-effective-water-simulation-physical-models
51. https://jtessen.people.clemson.edu/reports/papers_files/coursenotes2004.pdf
52. https://developer.nvidia.com/gpugems/gpugems/part-i-natural-effects/chapter-2-rendering-water-caustics
53. https://catlikecoding.com/unity/tutorials/flow/looking-through-water/
54. https://developer.nvidia.com/gpugems/gpugems2/part-i-geometric-complexity/chapter-2-terrain-rendering-using-gpu-based-geometry
55. https://developer.nvidia.com/gpugems/gpugems3/part-i-geometry/chapter-1-generating-complex-procedural-terrains-using-gpu
56. https://www.gdcvault.com/play/1021761/Adaptive-Virtual-Texture-Rendering-in
57. https://developer.nvidia.com/gpugems/gpugems3/part-i-geometry/chapter-6-gpu-generated-procedural-wind-animations-trees
58. https://bgolus.medium.com/anti-aliased-alpha-test-the-esoteric-alpha-to-coverage-8b177335ae4f
59. https://advances.realtimerendering.com/s2015/aaltonenhaar_siggraph2015_combined_final_footer_220dpi.pdf
60. https://developer.nvidia.com/blog/introduction-turing-mesh-shaders/
61. https://learnopengl.com/Guest-Articles/2020/Skeletal-Animation
62. https://developer.nvidia.com/gpugems/gpugems3/part-i-geometry/chapter-3-directx-10-blend-shapes-breaking-limits
63. https://www.adriancourreges.com/blog/2016/09/09/doom-2016-graphics-study/
64. https://www.iryoku.com/smaa/
65. https://www.elopezr.com/temporal-aa-and-the-quest-for-the-holy-trail/
66. https://gpuopen.com/fidelityfx-superresolution-3/
67. https://developer.nvidia.com/rtx/dlss
68. https://www.intel.com/content/www/us/en/developer/articles/technical/xess-sr-developer-guide.html
69. https://developer.download.nvidia.com/assets/gamedev/files/sdk/11/FXAA_WhitePaper.pdf
70. https://therealmjp.github.io/posts/msaa-overview/
71. https://learnopengl.com/Advanced-Lighting/Bloom
72. https://learnopengl.com/Guest-Articles/2022/Phys.-Based-Bloom
73. https://developer.nvidia.com/gpugems/gpugems3/part-iv-image-effects/chapter-27-motion-blur-post-processing-effect
74. https://developer.nvidia.com/gpugems/gpugems3/part-iv-image-effects/chapter-28-practical-post-process-depth-field
75. https://developer.nvidia.com/gpugems/gpugems2/part-iii-high-quality-rendering/chapter-24-using-lookup-tables-accelerate-color
76. https://roystan.net/articles/toon-shader/
77. https://roystan.net/articles/outline-shader/
78. https://image.docswell.com/s/ASW_Academy/5LVY67-GG-Toonline-Eng
79. https://www.gdcvault.com/play/1022031/GuiltyGearXrd-s-Art-Style-The (abstract only)
80. https://github.com/NoiRC256/URPSimpleGenshinShaders
81. https://hhoppe.com/hatching.pdf
82. https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/
83. https://casual-effects.blogspot.com/2014/03/weighted-blended-order-independent.html
84. https://developer.download.nvidia.com/whitepapers/2007/SDK10/SoftParticles_hi.pdf
85. https://developer.nvidia.com/gpugems/gpugems3/part-iv-image-effects/chapter-23-high-speed-screen-particles
86. https://www.iryoku.com/separable-sss/
87. https://developer.nvidia.com/gpugems/gpugems3/part-iii-rendering/chapter-14-advanced-techniques-realistic-real-time-skin
88. https://web.engr.oregonstate.edu/~mjb/cs519/Projects/Papers/HairRendering.pdf
89. https://lettier.github.io/3d-game-shaders-for-beginners/screen-space-reflection.html
90. https://www.bendstudio.com/blog/inside-bend-screen-space-shadows/
91. https://developer.apple.com/documentation/metal/tailor-your-apps-for-apple-gpus-and-tile-based-deferred-rendering
92. https://renderdoc.org/docs/getting_started/quick_start.html

**Fetches that failed** (content not used as verification): the Activision GTAO PDF/PPTX (too large), JCGT DDGI and SSR pages (empty), Hillaire EGSR 2020 PDF (too large), shaderbits octahedral impostors (no body), Arm Mali best-practices guide (redirected, empty), and a realtimevfx flipbook thread (404).

**Gaps:**
- Weakest coverage (claims mostly †): GTAO, DDGI internals, AgX details, tessellation, flipbooks, GPU particle internals, Genshin specifics beyond the face SDF, Guilty Gear threshold/ILM shading details. These are worth a second pass if the skill needs citations for them.
- Engine notes for URP Deferred+, HDRP STP, Unity GPU Resident Drawer and Godot FSR 2 are not verified.

---

## Addenda (added after skill verification; general knowledge, marked [verify])

- **Unity URP feature gaps by version.** Built-in SSR, volumetric fog and planar reflections have historically not shipped in URP (HDRP has SSR and volumetrics). Check the exact Unity version's URP docs; otherwise use a Renderer Feature, a third-party package, or the mobile stand-ins below. [verify]
- **Mobile (Mali / Adreno / Apple, tile-based) rules of thumb:**
  - Forward over Forward+/deferred on mid-range Android unless light counts demand it; avoid extra full-screen passes and mid-frame render-target switches (each forces tile store/load).
  - MSAA 2x–4x is cheap on TBDR; TAA costs a history buffer and blurs stylized lines.
  - Prefer opaque geometry over alpha test (alpha test disables hidden-surface removal); use fp16 in shaders and ASTC textures.
  - Merge post effects into one uber pass; run bloom at quarter resolution.
  - Leave thermal headroom: target well under 16.6 ms GPU for sustained 60 fps; measure on a real device with Arm Mobile Studio, Snapdragon Profiler or Xcode GPU tools.
- **Grass.** GPU instancing of blade clumps (DrawMeshInstancedIndirect / MultiMesh / Instanced Static Mesh), compute or chunk-based frustum + distance culling, density scaled per quality tier, wind in the vertex shader applied in every pass (including shadow and depth), player interaction via a global position uniform or a trail render texture, no shadow casting on low tiers.
- **Stylized looks and tonemapping.** ACES shifts hue and saturation of ramp colors; use a neutral tonemapper (Khronos PBR Neutral, or none) when colors are art-directed per band.
