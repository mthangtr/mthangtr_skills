# 2D Game Graphics and Rendering Techniques: Verified Catalog

**How to read this.** Every technique lists one source URL that was actually opened with WebFetch. Facts taken from a source are written as given there. Standard algorithm details added from common practice are marked **[std]**. Engine names and settings were checked against docs where a doc URL is cited. Settings that are not cited came from general knowledge and are marked **[verify]**.

Format for each entry: **Name** · What/why · How · Cost · Pitfalls · Engines · Source

---

## A. Pixel-perfect foundations

### A1. Low-res render target + integer scaling
- **What/why:** Render the whole game at a fixed small resolution, then upscale by a whole number. Every art pixel becomes an exact N×N block, so pixels never vary in size.
- **How:**
  - Pick a base resolution. Godot docs: most pixel games use 256×224 to 640×480. 640×360 scales to 720p, 1080p, 1440p and 4K with no bars.
  - Render to an offscreen target of that size with nearest filtering.
  - Blit it at `floor(min(screenW/baseW, screenH/baseH))`, and letterbox the rest.
- **Cost:** Very cheap. Fill rate falls by scale² for everything drawn into the small target.
- **Pitfalls:**
  - Fractional scale such as 2.5× gives uneven pixel widths.
  - UI or text drawn into the small target becomes blurry or chunky. Draw HUD and text at native resolution if you want crisp fonts.
  - Lighting and shadows follow viewport pixels, not texel resolution (Godot docs). Snap light UVs in a shader if you want light that looks pixelated.
- **Engines:**
  - Godot 4: `display/window/stretch/mode = viewport`, `stretch/scale_mode = integer`, aspect `keep` or `expand`.
  - Unity URP: Pixel Perfect Camera with Reference Resolution, Crop Frame (letterbox) and Upscale Render Texture.
  - Unreal: render to a low-res SceneCapture/RenderTarget, or lower the screen percentage with nearest upscale **[verify]**.
- **Source:** https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/rendering/multiple_resolutions.rst

### A2. Pixel snapping (transforms and vertices)
- **What/why:** Round sprite and camera positions to the art-pixel grid so sprites never sit between pixels. Without it you get shimmer, uneven "wobble" and mixels.
- **How:**
  - Snap world positions to multiples of 1/PPU at render time. Keep logical positions as floats.
  - Unity orthographic size = `screenHeight / (2 × PPU × scale)`.
- **Cost:** Free.
- **Pitfalls:**
  - Snapping only at render time can make sprites moving at different sub-pixel speeds jitter against each other.
  - A snapped camera plus a smooth-moving player gives visible stutter. Snap both, or use A3.
  - Unity Grid Snapping does not apply retroactively to existing objects.
  - In Godot 4, "Snap 2D Vertices to Pixel" is slated for deprecation. Use "Snap 2D Transforms to Pixel".
- **Engines:**
  - Godot: `rendering/2d/snap/snap_2d_transforms_to_pixel`.
  - Unity: Pixel Perfect Camera "Pixel Snapping" (render-time only; does not change Transforms). Sprites: Point filter, no mipmaps, no compression.
- **Source:** https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/manual/2d-pixelperfect.html (also https://forum.godotengine.org/t/difference-between-snap-2d-vertices-to-pixel-and-snap-2d-transforms-to-pixel/78642 and https://www.gamedeveloper.com/programming/pixel-perfect-rendering-in-unity)

### A3. Sub-pixel smooth camera (snap then offset)
- **What/why:** Keep the pixel grid stable while the camera scrolls smoothly at sub-pixel speed. This avoids the jerky 1-art-pixel steps you get at large scales.
- **How:**
  - Make the low-res target 1 px larger than the base resolution on each axis.
  - Render with the camera at `floor(camPos)`.
  - When blitting the upscaled image, shift it by `-(fract(camPos) × scale)` screen pixels and crop to the screen.
  - World pixels stay locked to each other while the view glides.
- **Cost:** Negligible, about one extra row/column.
- **Pitfalls:**
  - Parallax layers jitter unless rendered separately (yal.cc).
  - Mouse-to-world conversion needs the offset applied.
  - UI must not get the offset.
- **Engines:**
  - Godot: SubViewport + TextureRect/Sprite offset.
  - Unity: Pixel Perfect Camera alone cannot do this. Use a custom RT plus a UI RawImage offset.
  - Same idea for 3D pixel art (see B2).
- **Source:** https://yal.cc/gamemaker-smooth-pixel-perfect-camera/

### A4. Pixel-art-aware filtering for non-integer scale and rotation ("sharp bilinear" / fat-pixel)
- **What/why:** Sometimes you must allow fractional zoom, rotation or sub-pixel sprite motion. Nearest filtering shimmers and bilinear blurs, so blend only at texel borders.
- **How:**
  - Use nearest sampling inside each texel and a narrow bilinear ramp at texel edges, about one screen pixel wide.
  - The ramp width comes from `fwidth(uv × texSize)`.
  - Typical form: `uv = (floor(p) + 0.5 + clamp(fract(p) − 0.5, −w, w) / w × 0.5) / texSize` **[std]**.
  - Variants: smoothstep (Golus/Klems), fwidth clamp (Klems/Santos), coverage "fat pixel". The texture sampler must be set to bilinear.
- **Cost:** A few ALU per sample.
- **Pitfalls:**
  - Needs bilinear sampler plus padded atlases (see C2).
  - Trades sharpness against smoothness.
- **Engines:** Custom sprite shader in any engine.
- **Source:** https://jorenjoestar.github.io/post/pixel_art_filtering/

---

## B. Pixelization, 3D to pixel art, colour reduction

### B1. 3D models pre-rendered to pixel sprites (Dead Cells pipeline)
- **What/why:** Animate in 3D for speed and reuse, and ship pixel-art frames.
- **How:**
  - Build simple 3D models in 3ds Max.
  - Animate pose-to-pose with tool-generated in-betweens.
  - Render each frame at tiny size with no antialiasing and cel shading.
  - Export PNG frames plus normal maps for in-game lighting.
- **Cost:** Offline. At runtime these are ordinary sprites.
- **Pitfalls:**
  - Rendered at low res, a 50 px character loses detail, so don't over-model.
  - Motion quality is prioritised over per-pixel hand polish.
- **Source:** https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-

### B2. Real-time 3D pixel art (t3ssel8r style)
- **What/why:** Render a live 3D scene so it reads as hand-made pixel art.
- **How:**
  - Use an orthographic camera rendering to a low-res RT.
  - Snap the camera to a view-aligned, texel-sized grid to stop "pixel creep".
  - Re-add the fractional remainder as a screen-space offset on upscale, the same as A3.
  - Outlines: depth and normal edge detection with a 4-tap kernel (up/down/left/right). Separate outer depth edges from convex-crease highlights, using the normal-difference sign or a cross product.
  - Toon shading, quantised light steps and noise cloud shadows.
- **Cost:**
  - The whole 3D scene renders at low res, so it is cheap.
  - Post edge detection is O(pixels).
- **Pitfalls:**
  - Snapping only works for orthographic cameras. With perspective, depths drift at different rates. The "Texel Splatting" paper (2026) addresses this by splatting a cubemap from a grid-snapped origin, but it suffers disocclusion.
  - Camera rotation still causes shimmer.
  - Some engines (Godot 4.3) needed source changes to get depth/normal access in the needed passes (D. Holland).
- **Engines:**
  - Godot: SubViewport + depth/normal-roughness texture.
  - Unity URP: Renderer Feature with DepthNormals.
  - Unreal: post-process material with SceneDepth/WorldNormal + low screen percentage **[verify]**.
- **Source:** https://www.davidhol.land/articles/3d-pixel-art-rendering/ (and https://arxiv.org/abs/2603.14587)

### B3. Pixelization post-effect
- **What/why:** Turn any image into chunky pixels, for transitions or stylising.
- **How:**
  - Downsample to N× smaller with point or box filtering, then upscale with nearest.
  - Alternative in one pass: `uv = (floor(uv × res / N) + 0.5) × N / res` **[std]**.
  - Often followed by palette quantisation (B4) and outlines.
- **Cost:** One cheap pass.
- **Pitfalls:**
  - Moving content crawls unless the camera is snapped (B2).
  - Box downsampling gives muddier but more stable results than point sampling.
- **Source:** https://bnpr.gitbook.io/bnpr/pixel-art/pixel-art-basics (Blender: low res, 1 sample, Pixelate/Scale nodes)

### B4. Palette quantisation + ordered (Bayer) dithering
- **What/why:** Limit output to N colours (retro look, banding control). Dither to suggest in-between tones.
- **How:**
  - `c' = quantize(c + r × (M(x mod n, y mod n) − 0.5))`, where M is a normalised Bayer threshold matrix.
  - The matrix is built recursively by Kronecker product, or with the closed form `bit_reverse(bit_interleave(i^j, i)) / n²`.
  - r is roughly the spacing between palette colours (255/(2^N−1) for uniform RGB).
  - For arbitrary palettes, find the nearest colour in a perceptual space (Oklab), or bake a 3D LUT **[std]**.
- **Cost:** Per-pixel, with no error propagation, so it is fully parallel and shader-friendly. Error diffusion (Floyd–Steinberg) is serial and unsuitable for real time.
- **Pitfalls:**
  - Visible cross-hatch pattern.
  - The dither pattern must stay fixed to the screen or the low-res grid. If it is in world space and the camera moves, it "swims".
  - Apply in the low-res buffer, not after upscaling.
- **Source:** https://en.wikipedia.org/wiki/Ordered_dithering

### B5. Palette swapping (index textures / palette LUT)
- **What/why:** One sprite, many colour variants (team colours, damage, day/night) with no extra art and runtime changes.
- **How:**
  - (a) **Index texture:** store the palette index or UV in R (or RG). The shader does `texture(palette, vec2(index, row))`, and changing the row swaps palettes.
  - (b) **Colour match:** loop over a source-palette row and compare with a tolerance (e.g. 0.01). Replace with the same column from a target row.
  - Both use a palette image of N columns × K variant rows with nearest filtering.
- **Cost:**
  - (a) is one extra fetch.
  - (b) loops over the palette width, so it is costlier and has precision issues.
- **Pitfalls:**
  - Lossy compression or bilinear filtering corrupts indices. Use uncompressed, point-filtered textures.
  - The Godot colour-match shader is incompatible with AtlasTexture.
  - Shared materials change every instance. Use per-instance uniforms or vertex colour to pick the row.
- **Engines:**
  - Aseprite extension exports index-as-UV.
  - Godot: `instance uniform`.
  - Unity: MaterialPropertyBlock (breaks the SRP Batcher) or vertex colour.
- **Source:** https://godotshaders.com/shader/palette-swap-shader-sampler2d/ (index-as-UV: https://community.aseprite.org/t/export-indexed-color-as-uv-coordinate-pixels-and-a-palette-lookup-texture/14154)

### B6. Sprite rotation without mixels (RotSprite, upscale-rotate)
- **What/why:** Nearest-neighbour rotation of pixel art produces jaggies and orphan pixels. RotSprite keeps the art clean and adds no new colours.
- **How:**
  - Upscale 8× with a modified Scale2x that treats similar colours as equal.
  - Optionally pick a rotation offset that avoids sampling boundary pixels.
  - Rotate and downscale in one nearest-neighbour step.
  - Optionally restore lost single-pixel details.
- **Cost:**
  - Expensive (8× buffers), so normally pre-baked offline (Aseprite has RotSprite) or cached per angle.
  - Cheaper real-time alternatives: A1/A4 (rotate inside the low-res target), or a shader-based "cleanEdge"/xBR-style upscale **[std]**.
- **Pitfalls:**
  - Real-time per-frame RotSprite is rarely viable.
  - Pre-baking means storing angle sets.
- **Related:** Scale2x/EPX, hqx, xBR for upscaling.
- **Source:** https://en.wikipedia.org/wiki/Pixel-art_scaling_algorithms

---

## C. Sprites, atlases, batching, UI

### C1. Sprite batching / draw-call reduction
- **What/why:** Thousands of sprites need few GPU submissions, because CPU and driver overhead per draw call dominates 2D.
- **How:** The renderer merges consecutive items into one draw call when they share texture, material, blend mode, shader and skeleton, and sit in the same layer/Z.
- **Cost:** Large CPU win.
- **Pitfalls:**
  - Interleaving textures in draw order breaks batches. A, B, A gives 3 calls. Group by layer and atlas.
  - Batches cannot cross scene layers or Z indices.
  - Per-instance material changes break batches. Use vertex colour or instance data instead.
  - Lights can multiply draws (per-light passes) **[std]**.
- **Engines:**
  - Godot 4: batches automatically. Tilemaps and text gain most.
  - Unity: Sprite Atlas plus the dynamic batcher or SRP Batcher. MaterialPropertyBlocks and Sprite Masks break the SRP Batcher. Inspect with Frame Debugger.
- **Source:** https://godotengine.org/article/gles2-renderer-optimization-2d-batching (also https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/performance/gpu_optimization.rst)

### C2. Texture atlases (+ bleeding/padding)
- **What/why:** Pack many sprites into one texture so they batch into one draw call, and cut texture switches.
- **How:**
  - A packer places sprite rects with padding.
  - Extrude padding by repeating edge pixels so filtering never samples a neighbour.
  - Inset UVs by half a texel if there is no padding.
- **Cost:** Saves memory and draw calls.
- **Pitfalls:**
  - Bleeding seams with bilinear filtering, mipmaps or sub-pixel positions.
  - The half-texel inset alone shows only half of the edge pixels, so padding is better.
  - Pixel art should not be VRAM-compressed (Godot docs).
  - Unity: use variants for low-res platforms, late binding for manual loading, and the V1→V2 atlas upgrade.
- **Engines:**
  - Unity Sprite Atlas: "Unity only needs to create one draw call for all the sprites in a sprite atlas".
  - Godot: AtlasTexture / TileSet atlas.
  - Unreal Paper2D: sprite atlas groups **[verify]**.
- **Source:** https://webglfundamentals.org/webgl/lessons/webgl-qna-how-to-prevent-texture-bleeding-with-a-texture-atlas.html (Unity: https://docs.unity3d.com/Manual/sprite/atlas/atlas-landing.html)

### C3. Sprite mesh shape: tight vs full-rect (overdraw)
- **What/why:** Transparent texels still cost fill rate. A tight polygon around the opaque pixels cuts overdraw.
- **How:** The importer generates a convex or concave hull mesh around alpha > threshold.
- **Cost:** Fewer fragments, more vertices.
- **Pitfalls:**
  - Unity UI Images always render full rect.
  - Full rect is needed for 9-slice and tiled modes.
  - If vertex-bound with huge counts of tiny sprites, full rect may win.
  - Default to tight on mobile.
- **Engines:**
  - Unity: Mesh Type Tight / Full Rect.
  - Unreal Paper2D: Edit RenderGeom (shrink-wrapped). Default material is Unlit Masked.
  - Spine: mesh hulls, where pixels outside the hull don't cost fill rate.
- **Source:** https://gamedev.net/tutorials/programming/graphics/oops-are-your-unity-sprites-too-tight-r5501

### C4. 9-slice (9-patch)
- **What/why:** Resize panels and buttons without stretching corners.
- **How:**
  - Border insets split the sprite into a 3×3 grid.
  - Corners stay fixed, top and bottom edges stretch horizontally, sides stretch vertically, and the centre stretches both ways.
  - Tiled mode repeats instead of stretching. Adaptive mode repeats only past a Stretch Value.
- **Cost:** 9 quads (more when tiled).
- **Pitfalls:**
  - Needs Full Rect mesh (Unity).
  - At pixel-art scale, stretched edges create non-integer texels. Prefer tiled.
  - Colliders need Auto Tiling enabled.
- **Engines:**
  - Unity: SpriteRenderer Draw Mode Sliced/Tiled, borders set in the Sprite Editor.
  - Godot: NinePatchRect, StyleBoxTexture.
  - Unreal UMG: Box/Border draw-as **[verify]**.
- **Source:** https://docs.unity3d.com/Manual/sprite/9-slice/9-slice-sprite.html

---

## D. World structure: tilemaps, parallax, sorting

### D1. Tilemaps + autotiling (marching squares / Wang / blob-47)
- **What/why:** Grid levels drawn from tilesets, with tile choice automated from neighbours.
- **How:**
  - **Corner (marching squares, 16 tiles):** `idx = TL + 2·TR + 4·BL + 8·BR`. This is the 2-corner Wang set.
  - **Edge Wang (16):** 4 side bits.
  - **Blob (47+1):** 8-neighbour 0–255 mask, where a corner bit counts only if both adjacent edges are set. Then look up one of 47 unique tiles.
  - **Sub-blob:** 20 quarter-subtiles composited per tile.
  - **Micro-blob:** 13 subtiles.
  - **Dual-grid trick:** offset the display grid half a tile and use the 16-tile corner set **[std]**.
- **Cost:**
  - Rendering is chunked and batched, so it is cheap.
  - Autotile cost is per-edit only.
- **Pitfalls:**
  - Seams from atlas bleeding (see C2).
  - Godot: terrain IDs start at 0. Alternative tiles don't inherit base properties. Scene tiles are instantiated per tile and are expensive.
  - Unity Rule Tiles are checked top-down, so put common rules first.
- **Engines:**
  - Godot 4 TileSet terrains: Match Corners and Sides (3×3, i.e. blob), Match Corners (2×2), Match Sides; peering bits.
  - Unity: Tilemap + Rule Tile (2D Tilemap Extras).
  - Unreal: Paper2D TileSet/TileMap.
- **Source:** https://www.boristhebrave.com/2013/07/14/tileset-roundup/ (Godot: https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/2d/using_tilesets.rst · Unity: https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@4.1/manual/RuleTile.html)

### D2. Parallax scrolling
- **What/why:** Fake depth by moving layers at different speeds relative to the camera.
- **How:**
  - `layerPos = cameraPos × (1 − scrollScale)`. A scale below 1 reads as far away, above 1 as near.
  - Infinite repeat wraps the layer by `repeat_size`.
  - Add `repeat_times` copies so zoomed-out views stay covered.
- **Cost:** Cheap, but full-screen layers mean overdraw. N stacked full-screen alpha layers cost N× fill on mobile. Cut opaque regions and use opaque shaders for the back layer.
- **Pitfalls:**
  - Godot: the repeat canvas starts at (0,0) and extends down-right, so don't centre the texture. Textures smaller than the viewport leave gaps.
  - With pixel-perfect cameras, fractional layer offsets jitter. Snap each layer or render it separately (A3).
- **Engines:**
  - Godot 4: Parallax2D (replaces ParallaxBackground), CanvasLayer for HUD/background.
  - Unity: script- or Cinemachine-driven **[std]**.
- **Source:** https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/2d/2d_parallax.rst

### D3. Depth sorting / Y-sort
- **What/why:** In top-down and isometric views, objects lower on screen draw in front.
- **How:**
  - Sort draw order by the y of each object's pivot or feet within a layer.
  - Unity: Transparency Sort Mode = Custom Axis (0,1,0).
  - For isometric, use the axis (0,1,−0.26) or sort by (x+y) **[std]**.
  - Use groups so multi-part characters sort as a unit.
- **Cost:** CPU sort, plus possible batch breaks from interleaving.
- **Pitfalls:**
  - Godot: Y-sort only compares nodes with the same z_index. z_index doesn't affect processing or input order. `z_as_relative` adds the parent's Z.
  - Tall or long objects need pivot tweaks or splitting.
  - Unity: Sorting Group stops children interleaving with others. Sorting Layer and Order in Layer beat distance.
- **Engines:**
  - Godot: `CanvasItem.y_sort_enabled`, TileMapLayer y-sort, `z_index`.
  - Unity: Sorting Layers, Order in Layer, Custom Axis, Sorting Group, Sprite Sort Point (Pivot/Center).
  - Unreal Paper2D: translucency sort priority / sort axis **[verify]**.
- **Source:** https://docs.unity3d.com/Manual/2d-renderer-sorting.html (Godot: https://raw.githubusercontent.com/godotengine/godot/master/doc/classes/CanvasItem.xml)

---

## E. Animation

### E1. 2D skeletal animation + mesh deformation (Spine, DragonBones, engine-native)
- **What/why:** Fewer frames, smooth interpolation, runtime blending and IK. Meshes let images bend.
- **How:**
  - Bones form a hierarchy. Attachments are images or meshes.
  - Mesh vertices are skinned by weighted bones (linear blend skinning).
  - Deform keys / FFD keyframe vertices directly.
  - IK and path constraints are solved on the CPU per frame.
- **Cost:**
  - Per-vertex CPU transforms: 100 verts × 2 bones gives 200 transforms per frame.
  - Prune weights and limit bones per vertex.
  - Prefer weights over deform keys.
  - Clipping attachments are costly.
  - Unity 2D Animation: CPU skinning batches many low-poly sprites dynamically. GPU skinning (requires the SRP Batcher; no MaterialPropertyBlock or Sprite Mask) suits fewer high-poly sprites. It falls back to CPU if the requirements aren't met.
- **Pitfalls:**
  - Mesh hulls can't have holes.
  - Hull edges cutting opaque pixels alias, so MSAA is needed.
  - Godot auto-triangulation bends unpredictably. Add internal vertices and re-paint weights.
  - Skeletal motion on pixel art produces mixels unless it is rendered in a low-res target (A1).
- **Engines:**
  - Godot: Skeleton2D + Bone2D + Polygon2D (UV + weights).
  - Unity: 2D Animation package (Sprite Skin, Skinning Editor).
  - Unreal: Paper2D flipbooks only, with Spine runtimes or third-party tools for bones.
  - Spine and DragonBones have runtimes for all three engines **[verify per version]**.
- **Source:** https://esotericsoftware.com/spine-meshes (Unity: https://docs.unity3d.com/Packages/com.unity.2d.animation@14.0/manual/GPUDeformation.html · Godot: https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/animation/2d_skeletons.rst)

---

## F. Per-sprite shader effects

### F1. Sprite outlines: neighbour sampling
- **What/why:** Selection or highlight outlines, or a stylised border around any sprite.
- **How:**
  - **Outer outline:** if the pixel's alpha is 0 and any neighbour at offset w (4 or 8 directions, or a circle) has alpha > 0, output the outline colour.
  - **Inner outline:** opaque pixel with a transparent neighbour.
  - Expand the quad in the vertex shader so outlines aren't clipped by the sprite bounds.
- **Cost:** 4–16 extra texture fetches per pixel. Fine for thin outlines, and cost grows with width.
- **Pitfalls:**
  - Atlases: neighbour samples bleed into adjacent sprites. Pad the atlas, or clamp to the sprite rect (pass region in uniforms).
  - Quad expansion breaks with flip/rotation. Use `sign(VERTEX)`.
  - Anti-aliased source art gives thin, broken outlines.
  - Outlining groups of sprites needs a composite pass (Godot CanvasGroup, or render to RT).
- **Source:** https://godotshaders.com/shader/2d-outline-inline/

### F2. Wide or uniform outlines via SDF / JFA
- **What/why:** Thick, crisp outlines at roughly constant cost.
- **How:**
  - Render the silhouette mask, seed it, then run the jump flood algorithm (step sizes N/2, N/4 … 1, ⌈log₂N⌉ passes) to get nearest-seed coordinates.
  - The distance field is `length(nearest − p)`.
  - Outline where `dist < width`, with a smoothstep for anti-aliasing.
- **Cost:**
  - Brute force is O(w²). Separable blur is O(w) and loses small features.
  - JFA is O(log w): about 0.6 ms at 1080p for 100 px, under 1 ms even for full-screen widths (Ben Golus).
- **Pitfalls:**
  - Needs RG16 or 32F targets for coordinates.
  - JFA has rare small errors, reducible with 1+JFA or extra passes **[std]**.
  - Pre-baked SDF sprites (F7) are cheaper for static art.
- **Source:** https://bgolus.medium.com/the-quest-for-very-wide-outlines-ba82ed442cd9

### F3. Hit flash / tint / colour effects
- **What/why:** Instant damage feedback (white or red frame), plus status tints and pulsing.
- **How:**
  - `rgb = mix(tex.rgb, flashColor, amount); a = tex.a`, keeping the alpha.
  - Animate `amount` with a tween over about 50–100 ms.
  - Variants: additive tint, grayscale (`dot(rgb, lum)`), hue shift.
- **Cost:** Trivial.
- **Pitfalls:**
  - A shared material flashes every enemy. Use per-instance uniforms or vertex colour.
  - Unity: MaterialPropertyBlock breaks the SRP Batcher. Vertex colour is batch-safe.
  - Plain `modulate`/`SpriteRenderer.color` multiplies and can't reach white.
- **Engines:** Godot `instance uniform float flash;`. Unity Shader Graph Lerp into a Sprite Unlit graph.
- **Source:** https://godotshaders.com/shader/hit-flash-effect-shader/

### F4. Dissolve (noise threshold + burn edge)
- **What/why:** Death, teleport and spawn effects.
- **How:**
  - Sample noise n(uv).
  - `mask = step(threshold, n)`, and multiply alpha by the mask.
  - Burn edge: where `n` is in `[threshold, threshold+edge]`, output an emissive edge colour (add HDR for bloom).
  - Use smoothstep for soft edges.
- **Cost:** One noise fetch or procedural noise.
- **Pitfalls:**
  - Hard `step` aliases.
  - For pixel art, quantise the noise UV to the sprite's texel grid so pixels dissolve whole: `floor(uv × texSize)`.
  - Atlas UVs make noise scale differ per sprite. Use local UV or region-normalised UV.
- **Source:** https://mirzabeig.substack.com/p/unity-tutorial-dissolve-shader-part-1

### F5. SDF text and vector shapes
- **What/why:** Text and icons that stay crisp at any scale and rotation from small textures. Cheap outline, glow and shadow.
- **How:**
  - Store signed distance in 8-bit alpha (e.g. 4096² source to 64² field).
  - Edge at 0.5, with `smoothstep(0.5 − fw, 0.5 + fw, d)` where `fw = fwidth(d)`.
  - Outline is a second threshold. Drop shadow is an offset lookup.
  - Multi-channel SDF (MSDF) keeps sharp corners. Valve's paper suggests storing two edge distances in R and G.
  - Analytic SDF primitives for UI or VFX shapes: circle `length(p) − r`, box, rounded box, segment, arcs. Union with `min` and smooth union with smin. Round with `sd − r`, ring with `abs(sd) − r`.
- **Cost:** About the same as a normal texture fetch.
- **Pitfalls:**
  - Single-channel SDF rounds corners.
  - Distance spread limits the maximum outline width.
  - Not for pixel fonts. Use bitmap fonts at integer scale for those.
- **Engines:** Unity TextMeshPro (SDF), Godot 4 MSDF fonts option, Unreal Slate/UMG font SDF **[verify]**.
- **Source:** https://steamcdn-a.akamaihd.net/apps/valve/2007/SIGGRAPH2007_AlphaTestedMagnification.pdf (primitives: https://iquilezles.org/articles/distfunctions2d/)

---

## G. 2D lighting and shadows

### G1. Normal-mapped 2D dynamic lighting
- **What/why:** Lights reveal volume on flat sprites.
- **How:**
  - Sprite = diffuse + tangent-space normal map (+ specular/mask).
  - Per light: `L = normalize(lightPos.xyz − fragPos.xyz)` with light height z, `N·L` × attenuation.
  - Accumulate into a light buffer, then multiply or add onto albedo.
  - Normals come from 3D renders (B1), are hand-painted, or are generated (Laigter, SpriteIlluminator).
- **Cost:**
  - Per-light per-pixel. Unity renders light textures at reduced Render Scale (default 0.5).
  - Unity normal maps need a depth pre-pass per layer batch.
- **Pitfalls:**
  - Normals must stay consistent under sprite flip (negate N.x) and rotation **[std]**.
  - Godot: raise the light Height when using normal maps or everything darkens.
  - Pixel-art lighting looks smooth unless light UVs are snapped.
- **Engines:**
  - Godot 4: CanvasTexture (diffuse/normal/specular) + PointLight2D/DirectionalLight2D, and CanvasModulate for ambient.
  - Unity URP 2D: Sprite secondary textures `_NormalMap` and `_MaskTex`, Light 2D "Use Normal Map: Fast/Accurate" with Distance.
  - Unreal Paper2D: Lit sprite materials (DefaultLitSpriteMaterial) with a normal map, using standard 3D lights **[verify]**.
- **Source:** https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/2d/2d_lights_and_shadows.rst (Unity: https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/manual/SecondaryTextures.html)

### G2. Light blending modes and light buffers
- **What/why:** Control how light combines with the scene: darkness-based (multiply) versus glow (additive).
- **How:**
  - Render lights into a light texture.
  - Combine as `final = albedo × (ambient + Σ light)` (multiply), `final = albedo + light` (additive) or subtract.
  - Godot: Add (default), Subtract (negative lights), Mix (lerp).
  - Unity URP: up to 4 Light Blend Styles in the 2D Renderer Data (Multiply, Additive, Subtractive, plus "with Mask (R/G/B/A)" variants using `_MaskTex`).
- **Cost:** One light RT plus a composite.
- **Pitfalls:**
  - Unity allows only one Global Light per blend style per sorting layer.
  - Unity settings: Max Light Render Textures 4, Max Shadow RTs 1.
  - Additive light washes out to white with no tone mapping.
  - Cheap alternative: additive-blend sprites as fake lights, with no shadows or normals (Godot docs recommend this for perf).
- **Source:** https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/manual/LightBlendStyles.html (also https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/manual/2DRendererData-overview.html)

### G3. 2D shadow casting: visibility polygon (geometric)
- **What/why:** Line of sight, fog of war, hard shadows.
- **How:**
  - Sort segment endpoints by angle around the light.
  - Sweep 360° while keeping the set of segments the ray crosses, ordered by distance.
  - When the nearest wall changes, emit a triangle.
  - The triangle fan is the lit or visible area: render it as a light mask.
  - Union for multiple lights. Intersect with the player's view for fog of war.
- **Cost:** O(n log n) per light on CPU. Fine for dozens of lights with simple geometry.
- **Pitfalls:** Numerical robustness at collinear or shared endpoints (cast rays at ±ε around each endpoint **[std]**).
- **Source:** https://www.redblobgames.com/articles/visibility/

### G4. 2D shadows: shadow-volume geometry (extruded edges)
- **What/why:** Fast GPU hard and soft shadows from occluder polygons.
- **How:**
  - For each occluder edge facing away from the light, extrude a quad to "infinity" along the light direction in the vertex shader.
  - Draw it into the light's mask, stencil or alpha.
  - Soft shadows: compute penumbra wedges per edge from the light radius in the fragment shader.
- **Cost:** Vertex-bound, one pass per light, scales well.
- **Pitfalls:**
  - Self-shadowing on the occluder sprite. Unity offers a "self shadows" toggle.
  - Overlapping casters double-darken without max blending or stencil. Unity's Composite Shadow Caster 2D merges child shadows.
- **Engines:**
  - Unity URP: ShadowCaster2D (shape from the sprite's Custom Outline or the Shape Editor) + CompositeShadowCaster2D.
  - Godot: LightOccluder2D (OccluderPolygon2D) with shadow filter None (best for pixel art), PCF5 or PCF13 (heaviest) and Filter Smooth (high values band).
- **Source:** https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/manual/2DShadows.html (slembcke's soft-shadow article is blocked by robots.txt and was not opened)

### G5. 2D shadows: polar 1D shadow map (pixel-perfect)
- **What/why:** Shadows from arbitrary pixel occluders, with no polygons needed.
- **How:**
  - Render occluders into an FBO centred on the light.
  - Reduce to a 1D map: per angle, store the minimum distance to the first occluder.
  - When drawing the light, compare each pixel's distance to the 1D map at its angle.
  - Blur by distance from the light for soft edges.
- **Cost:** Fill-rate bound, about 20 lights on old hardware (GeForce 9400). Optimise with atlasing, channel packing and downsampling.
- **Pitfalls:** Worse than geometry shadows on mobile. One FBO pass per light.
- **Source:** https://github.com/mattdesl/lwjgl-basics/wiki/2D-Pixel-Perfect-Shadows

### G6. SDF / Jump Flood distance fields (building block)
- **What/why:** Turn any 2D scene or mask into a distance field in O(log n) GPU passes. Used for GI raymarching, outlines, soft shadows, particle collision and Voronoi.
- **How:**
  - Seed texture: occupied pixels store their own UV.
  - For k = N/2, N/4, …, 1: each pixel checks 9 samples at ±k and keeps the nearest seed.
  - The final distance is `length(seedUV − uv)`.
- **Cost:** ⌈log₂N⌉ full-screen passes, independent of seed count.
- **Pitfalls:**
  - Approximate: rare errors are "hardly noticeable" (Rong and Tan). Use 1+JFA or JFA+2 variants if needed.
  - Needs high-precision targets.
  - Aspect ratio: compute distance in pixels, not UV.
- **Engines:**
  - Godot 4 has a built-in 2D SDF generated from LightOccluder2D nodes with SDF Collision. Read it with `texture_sdf()`, `texture_sdf_normal()`, `sdf_to_screen_uv()` in canvas shaders. GPUParticles2D can collide with it **[verify]**.
  - Unity/Unreal: custom compute or blit passes.
- **Source:** https://www.comp.nus.edu.sg/~tants/jfa.html (Rong and Tan, I3D 2006; Godot: https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/shaders/shader_reference/canvas_item_shader.rst)

### G7. 2D global illumination: naive SDF raymarching
- **What/why:** Emissive pixels light the scene with soft shadows and colour bleed.
- **How:**
  - Draw emitters and occluders.
  - JFA to get a distance field (G6).
  - Per pixel, cast N rays in a circle and sphere-trace using the SDF step.
  - Accumulate the emitter colour on hit and average.
  - Add per-pixel random angle jitter, then temporal accumulation.
- **Cost:** N rays per pixel. Even 8 rays is "wildly inefficient" at high resolution.
- **Pitfalls:** Noise and banding at low ray counts. Temporal smearing in motion.
- **Source:** https://jason.today/gi

### G8. 2D GI via Radiance Cascades (Sannikov)
- **What/why:** Noise-free real-time 2D GI at roughly fixed cost.
- **How:**
  - **Penumbra condition:** near-field radiance has high spatial and low angular frequency; far-field has low spatial and high angular frequency.
  - Cascade i uses probe spacing ×2 and ray count ×4 per level, and covers ray interval [start_i, end_i] with geometrically growing intervals.
  - Each cascade raymarches only its interval through the SDF.
  - Merge top-down: if a ray in cascade i is unoccluded, add cascade i+1's bilinearly interpolated radiance for the matching directions.
  - Merge operator: `M(R_ab, R_bc) = [I_cb + e^(−τ_cb)·I_ba, τ_cb + τ_ba]`.
  - Cascade 0 gives the final per-pixel fluence.
- **Cost:**
  - Total work per cascade is about equal: base 4 with 2 cascades is about 16 rays per 16-pixel group, comparable to 32 naive rays but noise-free.
  - Holographic RC (Freeman, Sannikov, Margel 2025): 1.85 ms at 512² and 7.67 ms at 1024² on an RTX 3080 Laptop, close to the reference result.
- **Pitfalls:**
  - Ringing artifacts, most visible with single small lights.
  - Light leaking at merge boundaries. Clamp the merge offsets and do the maths in linear space, converting to sRGB at the end.
  - Memory: one texture per cascade (same size with direction-first packing).
  - Fixes: bilinear "fix" and Holographic RC.
- **Engines:** Custom in all three. Godot via compositor/SubViewport chains; Unity via a Renderer Feature or compute.
- **Source:** https://jason.today/rc · paper attribution: https://arxiv.org/pdf/2408.14425 (Osborne and Sannikov: "core radiance cascades method was developed by A. Sannikov") · original preprint repo: https://github.com/Raikiri/RadianceCascadesPaper · https://arxiv.org/abs/2505.02041v1 (Holographic RC)

### G9. Deferred 2D lighting via a sprite G-buffer
- **What/why:** Many lights at a cost independent of sprite count. Unifies 2D sprites with 3D lighting (HD-2D).
- **How:**
  - Geometry pass writes albedo (RGBA8), world normal (RGBA16F, from sprite normal maps through the TBN) and material data. Depth is used for position reconstruction.
  - Lighting pass is a full-screen triangle (not a quad) per light or light tile.
  - Shadows on billboards: alpha-tested shadow maps, so silhouettes match pixel art, plus screen-space contact shadows so sprites don't float.
- **Cost:**
  - Bandwidth-heavy: multiple render targets. Tile-based mobile GPUs pay for MRT store and load.
  - Light cost O(lit pixels).
- **Pitfalls:**
  - No true translucency: semi-transparent sprites need a forward pass.
  - Alpha must be cutout (masked).
- **Engines:**
  - Unreal: Paper2D Lit Masked sprites plus the deferred renderer give this natively.
  - Unity: 2D Renderer is not deferred. Use 3D URP Deferred with lit sprite materials.
  - Godot: 2D lights are forward-style per item; for deferred use 3D with Sprite3D.
- **Source:** https://dev.to/gaurav_de/creating-an-hd-2d-rendering-pipeline-on-dx12-205k

---

## H. VFX and post-processing

### H1. GPU particles
- **What/why:** Tens of thousands of particles with no CPU cost.
- **How:**
  - A simulation shader updates position and velocity buffers each frame from a process material (emission shape, velocity, gravity, curves, colour ramps).
  - Rendered as instanced quads or flipbook frames.
  - Godot can collide with the 2D SDF (G6).
- **Cost:**
  - GPU only. Overdraw of big alpha particles is the real cost.
  - Fixed FPS and Fract Delta add smoothness at a cost.
- **Pitfalls:**
  - Visibility or bounds rect too small: particles get culled. Use Godot "Generate Visibility Rect".
  - CPUParticles2D can win on weak devices and the Compatibility renderer.
  - Pixel art: render particles into the low-res target so they snap.
- **Engines:**
  - Godot: GPUParticles2D + ParticleProcessMaterial (CPUParticles2D gets no new features).
  - Unity: VFX Graph (URP 2D supported in recent versions **[verify]**) or the Shuriken Particle System (CPU).
  - Unreal: Niagara with a sprite renderer.
- **Source:** https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/2d/particle_systems_2d.rst

### H2. Trails / ribbons
- **What/why:** Motion streaks for weapons, projectiles and dashes.
- **How:**
  - Record a history of points spaced by a minimum vertex distance and a lifetime.
  - Build a camera-aligned strip with a width curve and a colour gradient over age.
  - UV mode: stretch (once along the length) or tile (per world unit).
- **Cost:** CPU mesh rebuild per frame. Vertex count grows with lifetime / min distance.
- **Pitfalls:**
  - Teleports draw a long streak. Clear or stop emitting before moving.
  - Extra corner and cap vertices cost performance.
  - "Generate Lighting Data" adds overhead.
  - Pixel art: rasterise into the low-res RT.
- **Engines:** Unity TrailRenderer/LineRenderer. Godot Line2D (scripted points) or GPUParticles2D trails. Unreal Niagara Ribbon.
- **Source:** https://docs.unity3d.com/Manual/class-TrailRenderer.html

### H3. Distortion / heat haze / shockwaves
- **What/why:** Air shimmer, shockwave rings, underwater wobble.
- **How:**
  - Sample the already-rendered scene (screen texture or grab pass) at `uv + (noise(uv + time·rise) × 2 − 1) × strength`.
  - Fade strength with height or a mask.
  - Shockwave: radial offset `dir × f(ringDist)` **[std]**.
  - Offset can come from a scrolling seamless noise or normal map, or be accumulated in a distortion RT from sprite-based emitters.
- **Cost:** One screen copy plus one fetch. A screen copy per effect is expensive. Batch effects into one distortion buffer.
- **Pitfalls:**
  - Only distorts what was drawn before it.
  - Screen edges sample outside the screen: clamp.
  - Noise must be seamless and repeat-wrapped.
  - Pixel art: quantise the offset to whole texels.
- **Engines:**
  - Godot 4: `uniform sampler2D screen_tex : hint_screen_texture`.
  - Unity URP 2D: Camera Sorting Layer Texture (captured after chosen sorting layers, with optional downsampling).
  - Unreal: Refraction or PixelDepthOffset/SceneColor in a translucent material **[verify]**.
- **Source:** https://github.com/SFML/SFML/wiki/Source:-HeatHazeShader

### H4. 2D water reflections / refraction
- **What/why:** Mirrored, wavy reflections below a water line, plus distorted see-through.
- **How:**
  - On the water sprite, sample the screen texture with uv.y mirrored around the water line's screen y: `uv.y = 2·lineY − uv.y`.
  - Add noise-based horizontal offset and tint.
  - Refraction: sample the unflipped screen at uv + noise offset.
  - Add scrolling caustic or wave highlights.
- **Cost:** One screen copy.
- **Pitfalls:**
  - Reflects only what was already drawn, so Z order matters.
  - Objects above the screen top can't reflect. Fade near edges, or render a dedicated reflection camera/RT.
  - Camera zoom changes the line maths.
  - Seam lines appear with non-seamless noise.
- **Source:** https://godotshaders.com/shader/water-2d-reflection-4-x/

### H5. CRT / scanline post
- **What/why:** Retro display emulation.
- **How:**
  - Scanlines with beam width varying by brightness.
  - Phosphor mask: aperture grille, slot or dot.
  - Barrel curvature plus vignette.
  - Glow/halation (bloom-like), gamma handling.
  - Apply at output resolution after integer upscale.
- **Cost:** From very cheap (zfast-crt, crt-blurpi for mobile) to heavy (crt-royale, meta-crt, which want 1440p+).
- **Pitfalls:**
  - Looks best with integer scaling.
  - Masks moiré at low output resolution.
  - Darkens the image, so compensate brightness.
- **Source:** https://docs.libretro.com/shader/crt/

### H6. Bloom, including low-res pixel-art bloom
- **What/why:** Glow on bright and emissive things.
- **How:**
  - Brightness threshold extract (HDR > 1, via MRT or a separate pass).
  - Downsample chain + separable Gaussian ping-pong (about 64 vs 1024 taps). Additive combine before tone mapping.
  - **Pixel-art variant [std]:** keep the scene in the low-res target and nearest-upscale it. Do bloom at or below low res and upscale bilinearly so the glow is soft while the sprites stay crisp. Or nearest-upscale the bloom too for blocky glow.
- **Cost:** A few downsampled passes. Cheap if done at low res.
- **Pitfalls:**
  - LDR thresholds bloom white UI.
  - Bloom applied after upscaling costs scale² more and blurs pixel edges.
  - Mobile: limit iterations and resolution.
- **Engines:** Godot WorldEnvironment glow (2D needs HDR 2D enabled **[verify]**), Unity URP Volume Bloom (works with the 2D Renderer), Unreal post-process Bloom.
- **Source:** https://learnopengl.com/Advanced-Lighting/Bloom

### H7. Screen shake and game-feel VFX
- **What/why:** Impact and weight. Cheap juice with a big perceived effect.
- **How:**
  - **Trauma model (Eiserloh):** trauma 0..1 is added on hits and decays linearly. `shake = trauma²` (or ³).
  - `offset = maxOffset × shake × perlin(seed, t·freq)`. Rotational shake matters in 2D.
  - Smooth noise beats per-frame random.
  - Camera follow uses asymptotic averaging: `pos += (target − pos) × k`.
  - **Nuclear Throne pistol recipe (Nijman):** camera kick 6 px against the aim, +4 screenshake that decays fast, weapon recoil, round muzzle-flash frame, shell ejection, enemy knockback 3 px/frame, white hit frame, 10–20 ms hit-stop, material-specific impact sounds.
- **Cost:** Free.
- **Pitfalls:**
  - Shake must not move UI.
  - In pixel-perfect setups, shake integer offsets or apply it via the A3 offset to avoid shimmer.
  - Offer an accessibility toggle.
  - Hit-stop should freeze gameplay time, not rendering or audio.
- **Source:** https://www.gamedeveloper.com/programming/video-sprucing-up-cameras-with-math (GDC 2016, Squirrel Eiserloh) + https://infovore.org/?p=5275 (Nijman, "Art of Screenshake" summary)

---

## I. Procedural and fake-3D

### I1. Procedural 2D with noise
- **What/why:** Terrain, biomes, clouds, textures and animated VFX without hand-authoring.
- **How:**
  - Gradient noise (Perlin/Simplex/OpenSimplex) with fBm: octaves with frequency ×2 and amplitude ×0.5 (gain/persistence), normalised by the sum of amplitudes.
  - Redistribute with `pow(e, k)` for flat valleys.
  - Elevation × moisture lookup gives biomes.
  - Seamless wrap: sample 3D noise on a cylinder or 4D on a torus.
  - Domain warping for organic shapes **[std]**.
- **Cost:** CPU per tile at generation. GPU noise in shaders for animated effects.
- **Pitfalls:**
  - Library ranges differ ([-1,1] vs [0,1]).
  - Purely local noise has no global structure (rivers), so add separate passes.
  - Pixel art: quantise noise to the pixel grid and the palette.
- **Engines:** Godot FastNoiseLite + NoiseTexture2D (built in). Unity `Mathf.PerlinNoise` / `Unity.Mathematics.noise`. Unreal Noise material node.
- **Source:** https://www.redblobgames.com/maps/terrain-from-noise/

### I2. Mode 7 (per-scanline affine plane)
- **What/why:** A pseudo-3D floor or racetrack from one 2D texture.
- **How:**
  - Per scanline y, apply an affine matrix [a b; c d] plus origin (e, f): `tex = M·(screen − origin) + origin`.
  - Perspective comes from changing the scale per scanline (SNES HDMA).
  - Shader version: `z = camH / (y − horizon)`, `world = cam + rot(θ)·(x·z, z)`, then sample the tilemap texture **[std]**.
- **Cost:** One texture fetch per pixel.
- **Pitfalls:**
  - Aliasing and shimmer far away: use mipmaps or supersampling, or fog the horizon.
  - Sprites need manual projection and scaling.
  - The SNES used 16-bit fixed point with 13-bit offsets.
- **Source:** https://en.wikipedia.org/wiki/Mode_7

### I3. Raycasting (Wolfenstein-style)
- **What/why:** First-person pseudo-3D from a 2D grid map.
- **How:**
  - Per screen column, cast one ray through the grid with DDA (step to the next x or y gridline).
  - On a wall hit, take the perpendicular distance (avoids fisheye): `perp = sideDist − deltaDist`.
  - `lineHeight = screenH / perp`.
  - Texture column = `int(wallX × texW)`, with a vertical affine step.
  - Billboard sprites are sorted and clipped by a per-column z-buffer **[std]**.
- **Cost:** O(columns × steps). Trivial on modern hardware and doable in a fragment shader.
- **Pitfalls:**
  - Using Euclidean distance causes fisheye.
  - No looking up or down without y-shearing.
  - Floors and ceilings need a separate per-row cast.
- **Source:** https://lodev.org/cgtutor/raycasting.html

### I4. 2.5D / HD-2D (pixel sprites in a 3D world)
- **What/why:** Octopath look: pixel-art billboards in 3D dioramas with modern lighting and lens effects.
- **How:**
  - Pixel sprites as billboards or camera-facing quads in a 3D scene (UE4).
  - Dynamic point lights with shadows (alpha-tested shadow maps, plus contact shadows so sprites stay grounded).
  - Strong depth of field / tilt-shift for the miniature feel.
  - Bloom, volumetric fog and light, particles.
  - Octopath II: high-resolution pixel art, a day/night cycle, cameras swinging up to 90° in battle and 180° in events, Sequencer-driven.
- **Cost:** Full 3D deferred pipeline. DOF and volumetrics are the expensive parts.
- **Pitfalls:**
  - Flat sprites look like "paper" against 3D: lighting tricks are needed to unify them.
  - Billboards break at steep camera angles.
  - Keep sprites at integer texel density relative to the screen, or accept filtering (A4).
  - Bokeh gather needs noise to hide banding.
- **Engines:**
  - Unreal: Paper2D sprites with Lit Masked materials + Cinematic DOF.
  - Unity: URP 3D + SpriteRenderer with a lit material + DOF Volume.
  - Godot: Sprite3D (billboard, alpha cut, shaded) + Environment DOF/glow/volumetric fog.
- **Source:** https://en.wikipedia.org/wiki/HD-2D (also https://www.unrealengine.com/en-us/developer-interviews/octopath-traveler-ii-builds-a-bigger-bolder-world-in-its-stunning-hd-2d-style and the G9 dev.to source)

---

## J. Performance (2D-specific, including mobile)

### J1. Fill rate / overdraw / mobile
- **What/why:** 2D is usually fill-bound (transparent layers stacked) and draw-call-bound, not vertex-bound.
- **How:**
  - **Diagnose fill rate:** disable V-Sync and compare FPS in a large vs a small window. A big gain means fill-bound.
  - Transparent sprites must draw back-to-front and get no early-Z benefit, so overlapping alpha is the killer.
  - Mobile tile-based GPUs suffer when geometry piles into few tiles.
- **Mitigations:**
  - Tight meshes (C3).
  - Opaque shader for backgrounds and tiles.
  - Fewer full-screen parallax and post layers.
  - Render at low res (A1).
  - Lower light RT scale (Unity default 0.5).
  - Disable the depth/stencil buffer when there are no sprite masks (Unity 2D Renderer Data).
  - Shadow filter None (Godot).
  - Additive sprites instead of real lights.
  - Atlas everything (C2), and keep the material count low (C1).
  - No VRAM compression for pixel art (artifacts with little gain).
- **Pitfalls:**
  - Each post effect is a full-screen pass, which is expensive at native mobile resolution. Run it in the low-res buffer.
  - Screen-texture reads force resolves or copies.
  - Use the profiler (Unity Frame Debugger, Godot Monitors/visual profiler, Unreal stat GPU).
- **Source:** https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/performance/gpu_optimization.rst

### J2. Anti-aliasing for non-pixel 2D (vector art, lines)
- **What/why:** Smooth edges for HD 2D art, lines and polygons.
- **How:**
  - Per-object AA on lines and polygons: Godot Line2D `antialiased`, draw_* `antialiased`.
  - MSAA 2D for geometry and sprite edges. It increases coverage samples only.
  - SDF shapes with fwidth smoothing (F5).
- **Cost:** Per-object AA is cheap. MSAA costs memory and bandwidth.
- **Pitfalls:**
  - MSAA does nothing for aliasing inside nearest-filtered textures, shader aliasing or fonts.
  - In Godot, MSAA 2D is Forward+/Mobile only.
  - Spine mesh hulls need MSAA.
- **Source:** https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/2d/2d_antialiasing.rst

---

## Quick engine cheat-sheet (verified items only unless marked)

**Godot 4**
- Stretch: viewport + integer, Snap 2D Transforms to Pixel.
- Parallax2D, CanvasLayer.
- `y_sort_enabled` (same z_index only).
- TileSet terrains (3 match modes).
- PointLight2D/DirectionalLight2D/CanvasModulate/LightOccluder2D. Blend Add/Sub/Mix. Shadow filter None/PCF5/PCF13.
- CanvasTexture normal/specular.
- Canvas shader: `hint_screen_texture`, `texture_sdf`, `light()`, `SHADOW_MODULATE`, render modes `unshaded`/`light_only`/`blend_add`/`blend_premul_alpha`.
- GPUParticles2D. Skeleton2D/Bone2D/Polygon2D. MSAA 2D.

**Unity URP 2D**
- Pixel Perfect Camera (Assets PPU, Reference Resolution, Crop Frame, Grid Snapping, Upscale RT, Retro AA filter).
- Sprite Atlas. Mesh Type Tight/Full Rect. 9-slice Sliced/Tiled.
- Sorting Layers, Custom Axis, Sorting Group. Rule Tile.
- Light 2D (Freeform/Sprite/Spot/Global; 2D lighting is not physically based). 4 Blend Styles. `_NormalMap`/`_MaskTex`.
- ShadowCaster2D/Composite. 2D Renderer Data (Render Scale 0.5, Max Light RTs 4, Camera Sorting Layer Texture).
- 2D Animation CPU vs GPU skinning. TrailRenderer.

**Unreal Paper2D**
- Sprites (texture-mapped planar mesh). Default material Unlit Masked; Lit/Unlit × Opaque/Masked/Translucent variants.
- Edit RenderGeom. Flipbooks. TileSets/TileMaps.
- Import settings: Default Pixels Per Unreal Unit, Sprite Texture Group "2D pixels" for retro, compression override, normal-map suffix auto-detection, "Apply Paper2D Texture Settings".
- 2D lighting and DOF come from the standard 3D renderer.
- No native 2D bones; use Spine or third-party.

---

## Sources actually opened (WebFetch, content returned)

1. https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/rendering/multiple_resolutions.rst
2. https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/2d/2d_lights_and_shadows.rst
3. https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/2d/using_tilesets.rst
4. https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/2d/2d_parallax.rst
5. https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/2d/2d_antialiasing.rst
6. https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/2d/particle_systems_2d.rst
7. https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/2d/canvas_layers.rst
8. https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/animation/2d_skeletons.rst
9. https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/shaders/shader_reference/canvas_item_shader.rst
10. https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/performance/gpu_optimization.rst
11. https://raw.githubusercontent.com/godotengine/godot/master/doc/classes/CanvasItem.xml
12. https://forum.godotengine.org/t/difference-between-snap-2d-vertices-to-pixel-and-snap-2d-transforms-to-pixel/78642
13. https://godotengine.org/article/gles2-renderer-optimization-2d-batching
14. https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/manual/2d-pixelperfect.html
15. https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/manual/Lights-2D-intro.html
16. https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/manual/LightBlendStyles.html
17. https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/manual/2DShadows.html
18. https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/manual/SecondaryTextures.html
19. https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/manual/2DRendererData-overview.html
20. https://docs.unity3d.com/Manual/sprite/atlas/atlas-landing.html
21. https://docs.unity3d.com/Manual/sprite/9-slice/9-slice-sprite.html
22. https://docs.unity3d.com/Manual/2d-renderer-sorting.html
23. https://docs.unity3d.com/Manual/class-TrailRenderer.html
24. https://docs.unity3d.com/Packages/com.unity.2d.animation@14.0/manual/GPUDeformation.html
25. https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@4.1/manual/RuleTile.html
26. https://dev.epicgames.com/documentation/en-us/unreal-engine/2d-in-unreal-engine
27. https://dev.epicgames.com/documentation/en-us/unreal-engine/paper-2d-sprites?application_version=4.27
28. https://dev.epicgames.com/documentation/en-us/unreal-engine/paper2d-import-settings-in-the-unreal-engine-project-settings
29. https://www.unrealengine.com/en-us/developer-interviews/octopath-traveler-ii-builds-a-bigger-bolder-world-in-its-stunning-hd-2d-style
30. https://en.wikipedia.org/wiki/HD-2D
31. https://dev.to/gaurav_de/creating-an-hd-2d-rendering-pipeline-on-dx12-205k
32. https://arxiv.org/pdf/2408.14425 (Osborne and Sannikov, Radiance Cascades, credits Sannikov for the core method)
33. https://arxiv.org/abs/2408.14425
34. https://github.com/Raikiri/RadianceCascadesPaper (Sannikov's unpublished RC paper repo; PDF itself not parsed)
35. https://arxiv.org/abs/2505.02041v1 (Holographic Radiance Cascades, Freeman/Sannikov/Margel)
36. https://jason.today/rc
37. https://jason.today/gi
38. https://www.comp.nus.edu.sg/~tants/jfa.html (Rong and Tan, JFA, I3D 2006)
39. https://bgolus.medium.com/the-quest-for-very-wide-outlines-ba82ed442cd9
40. https://www.redblobgames.com/articles/visibility/
41. https://www.redblobgames.com/maps/terrain-from-noise/
42. https://www.boristhebrave.com/2013/07/14/tileset-roundup/
43. https://github.com/mattdesl/lwjgl-basics/wiki/2D-Pixel-Perfect-Shadows
44. https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-
45. https://www.gamedeveloper.com/programming/pixel-perfect-rendering-in-unity
46. https://www.gamedeveloper.com/programming/video-sprucing-up-cameras-with-math
47. https://infovore.org/?p=5275
48. https://yal.cc/gamemaker-smooth-pixel-perfect-camera/
49. https://jorenjoestar.github.io/post/pixel_art_filtering/
50. https://www.davidhol.land/articles/3d-pixel-art-rendering/
51. https://arxiv.org/abs/2603.14587 (Texel Splatting)
52. https://bnpr.gitbook.io/bnpr/pixel-art/pixel-art-basics
53. https://en.wikipedia.org/wiki/Pixel-art_scaling_algorithms
54. https://en.wikipedia.org/wiki/Ordered_dithering
55. https://en.wikipedia.org/wiki/Mode_7
56. https://lodev.org/cgtutor/raycasting.html
57. https://steamcdn-a.akamaihd.net/apps/valve/2007/SIGGRAPH2007_AlphaTestedMagnification.pdf
58. https://iquilezles.org/articles/distfunctions2d/
59. https://godotshaders.com/shader/palette-swap-shader-sampler2d/
60. https://community.aseprite.org/t/export-indexed-color-as-uv-coordinate-pixels-and-a-palette-lookup-texture/14154
61. https://godotshaders.com/shader/2d-outline-inline/
62. https://godotshaders.com/shader/hit-flash-effect-shader/
63. https://godotshaders.com/shader/water-2d-reflection-4-x/
64. https://mirzabeig.substack.com/p/unity-tutorial-dissolve-shader-part-1
65. https://esotericsoftware.com/spine-meshes
66. https://gamedev.net/tutorials/programming/graphics/oops-are-your-unity-sprites-too-tight-r5501
67. https://webglfundamentals.org/webgl/lessons/webgl-qna-how-to-prevent-texture-bleeding-with-a-texture-atlas.html
68. https://github.com/SFML/SFML/wiki/Source:-HeatHazeShader
69. https://learnopengl.com/Advanced-Lighting/Bloom
70. https://docs.libretro.com/shader/crt/

## Gaps and caveats

- **Failed or blocked fetches:**
  - slembcke "SuperFastSoftShadows" (robots.txt); G4 cites Unity instead.
  - cr31 blob page (timeout).
  - The rendered docs.godotengine.org HTML pages return no body; raw RST/XML on GitHub was used instead.
  - Godot 3.5 batching page (empty).
- **Sannikov's original RC preprint PDF was not parsed.** RC mechanics come from the Osborne and Sannikov arXiv paper (penumbra criterion, merge operator) and jason.today (2D implementation details).
- **t3ssel8r has no written article; his work is on YouTube.** His approach is documented here through D. Holland's article, which credits him.
- **Items marked [verify] are not confirmed.** This covers Unreal-specific settings, Godot HDR-2D glow, Unity VFX Graph 2D support, and the TextMeshPro/MSDF specifics. Check these against current engine docs before treating them as authoritative.
- **No dedicated source for low-res bloom or DragonBones.** The pixel-art bloom variant is standard practice; DragonBones is mentioned only alongside Spine.
---

## Addenda (added after skill verification; general knowledge, marked [verify])

- **Godot `viewport` vs `canvas_items` stretch mode.** In `viewport` mode the whole frame (lights, shadows, glow, UI) is rendered at base resolution, so lighting is already low-res and the "snap light UVs" tip in §A1 is unnecessary. That tip applies to `canvas_items` mode, where lights evaluate at screen resolution. [verify]
- **Native-resolution HUD over a low-res game.** Render the game into a SubViewport at base resolution (nearest filter), display it with integer scaling (SubViewportContainer or a TextureRect with a scale = floor(min(W/w, H/h))), and draw the HUD in the window at native resolution on a CanvasLayer above it. Unity: Pixel Perfect Camera on the game camera, with UI on a separate Screen Space canvas. [verify]
- **Ultrawide / non-16:9.** Choose between pillarbox (same view for all players) and aspect `expand` (wider view: camera bounds and level design must allow it). Decide this with design; it is a gameplay choice, not only a render setting.
- **2D GI (§G7–G8) practical notes:**
  - Pad the GI render target beyond the screen (for example by the longest light reach) so off-screen emitters still light the visible area.
  - Snap the GI target to whole texels as the camera moves, otherwise GI shimmers.
  - Multi-bounce: feed last frame's GI (times albedo) back as emission into the scene texture; clamp and damp it to avoid runaway energy.
  - Unity URP 2D Renderer support for custom Renderer Features depends on the Unity version; otherwise use a separate camera + compute dispatch from a script. [verify]
- **Rotation with normal maps.** Rotate the normal vector with the sprite (most engines do this when the normal map is sampled in the sprite's local space); on horizontally flipped sprites negate N.x if the engine does not.
- **Cost labels.** 2D entries describe cost in prose. Rough tiers: A–F and H (except H1 at scale) run on any mobile; G1–G5 mobile with capped light counts; G7–G9 mid PC or better.
