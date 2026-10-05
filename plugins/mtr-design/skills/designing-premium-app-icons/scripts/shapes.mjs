// Procedural shape helpers for breaking the "primitive at center" look.
// Points are [x, y] arrays on the 1024 canvas; turn them into SVG with toPath().
// Every function is seeded, so re-running a generator gives identical output.

export function rng(seed = 1) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Smooth periodic noise: a few random sine octaves, so wobble has no seams on closed shapes.
function noise1d(seed, octaves = 3) {
  const r = rng(seed);
  const waves = Array.from({ length: octaves }, (_, i) => ({ f: 2 + i * 2 + Math.floor(r() * 3), p: r() * Math.PI * 2, a: 1 / (i + 1) }));
  const norm = waves.reduce((s, w) => s + w.a, 0);
  return t => waves.reduce((s, w) => s + w.a * Math.sin(w.f * t * Math.PI * 2 + w.p), 0) / norm;
}

export function ellipse(cx, cy, rx, ry = rx, n = 96) {
  return Array.from({ length: n }, (_, i) => {
    const t = (i / n) * Math.PI * 2;
    return [cx + rx * Math.cos(t), cy + ry * Math.sin(t)];
  });
}

// Organic closed silhouette: a circle whose radius breathes with `lobes` bulges.
export function blob(cx, cy, r, { lobes = 3, irregularity = 0.18, seed = 1, n = 96 } = {}) {
  const nz = noise1d(seed), r0 = rng(seed + 7)() * Math.PI * 2;
  return Array.from({ length: n }, (_, i) => {
    const t = i / n, a = t * Math.PI * 2;
    const k = 1 + irregularity * (0.6 * Math.sin(lobes * a + r0) + 0.4 * nz(t));
    return [cx + r * k * Math.cos(a), cy + r * k * Math.sin(a)];
  });
}

// Hand-drawn edge: displaces every point along its normal by smooth noise of amplitude `amp` px.
export function wobble(points, { amp = 8, seed = 1, closed = true } = {}) {
  const nz = noise1d(seed, 4), n = points.length;
  return points.map((p, i) => {
    const a = points[closed ? (i - 1 + n) % n : Math.max(i - 1, 0)], b = points[closed ? (i + 1) % n : Math.min(i + 1, n - 1)];
    const dx = b[0] - a[0], dy = b[1] - a[1], len = Math.hypot(dx, dy) || 1;
    const d = amp * nz(i / n);
    return [p[0] + (-dy / len) * d, p[1] + (dx / len) * d];
  });
}

// Brush stroke along an open polyline: filled outline whose width swells and tapers like ink.
export function brush(points, { width = 90, taper = 0.6, jitter = 0.15, seed = 1 } = {}) {
  const nz = noise1d(seed), n = points.length, left = [], right = [];
  points.forEach((p, i) => {
    const a = points[Math.max(i - 1, 0)], b = points[Math.min(i + 1, n - 1)];
    const dx = b[0] - a[0], dy = b[1] - a[1], len = Math.hypot(dx, dy) || 1;
    const t = i / (n - 1), ends = Math.sin(Math.PI * t) ** taper;
    const w = (width / 2) * Math.max(ends, 0.12) * (1 + jitter * nz(t));
    left.push([p[0] - (dy / len) * w, p[1] + (dx / len) * w]);
    right.push([p[0] + (dy / len) * w, p[1] - (dx / len) * w]);
  });
  return [...left, ...right.reverse()];
}

// Catmull-Rom spline through the points, emitted as cubic Béziers.
export function toPath(points, closed = true) {
  const n = points.length, P = i => points[closed ? (i + n) % n : Math.min(Math.max(i, 0), n - 1)];
  const f = v => v.toFixed(1);
  let d = `M${f(P(0)[0])},${f(P(0)[1])}`;
  for (let i = 0; i < (closed ? n : n - 1); i++) {
    const p0 = P(i - 1), p1 = P(i), p2 = P(i + 1), p3 = P(i + 2);
    d += `C${f(p1[0] + (p2[0] - p0[0]) / 6)},${f(p1[1] + (p2[1] - p0[1]) / 6)} ${f(p2[0] - (p3[0] - p1[0]) / 6)},${f(p2[1] - (p3[1] - p1[1]) / 6)} ${f(p2[0])},${f(p2[1])}`;
  }
  return closed ? d + 'Z' : d;
}

// Grain/stipple texture as plain circles (no SVG filters, so it survives Icon Composer import).
export function stipple({ count = 5000, color = '#000', opacity = 0.12, rMin = 1, rMax = 2.6, seed = 1, x = 0, y = 0, w = 1024, h = 1024 } = {}) {
  const r = rng(seed);
  let dots = '';
  for (let i = 0; i < count; i++) dots += `<circle cx="${(x + r() * w).toFixed(1)}" cy="${(y + r() * h).toFixed(1)}" r="${(rMin + r() * (rMax - rMin)).toFixed(1)}"/>`;
  return `<g fill="${color}" fill-opacity="${opacity}">${dots}</g>`;
}

export const svg = body => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">${body}</svg>`;
