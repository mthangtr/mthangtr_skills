#!/usr/bin/env node
// Usage: node scripts/preview.mjs <icon-dir>
// <icon-dir>/layers/NN-name.svg  (back -> front, 1024x1024, unmasked)
// Writes <icon-dir>/preview/sheet.png and icon-1024.png (flattened, unmasked) + prints a lint/metrics report.
import { Resvg } from '@resvg/resvg-js';
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const S = 1024;
const dir = process.argv[2];
if (!dir) { console.error('usage: node preview.mjs <icon-dir>'); process.exit(1); }

const layerDir = path.join(dir, 'layers');
const layers = fs.existsSync(layerDir)
  ? fs.readdirSync(layerDir).filter(f => f.endsWith('.svg')).sort().map(f => path.join(layerDir, f))
  : [];
if (!layers.length) { console.error('no layers/*.svg in', dir); process.exit(1); }

const render = (svg, w = S) => new Resvg(svg, { fitTo: { mode: 'width', value: w }, background: 'rgba(0,0,0,0)' }).render();
const dataUri = png => 'data:image/png;base64,' + Buffer.from(png).toString('base64');

// Apple's icon mask is a continuous-curvature squircle; a superellipse with n=5 is a close stand-in.
function squirclePath(size, x0 = 0, y0 = 0, n = 5) {
  const r = size / 2, pts = [];
  for (let i = 0; i < 360; i++) {
    const t = (i / 360) * 2 * Math.PI, c = Math.cos(t), s = Math.sin(t);
    pts.push([x0 + r + r * Math.sign(c) * Math.abs(c) ** (2 / n), y0 + r + r * Math.sign(s) * Math.abs(s) ** (2 / n)]);
  }
  return 'M' + pts.map(p => p.map(v => v.toFixed(1)).join(',')).join('L') + 'Z';
}

const issues = [];
const warn = (f, msg) => issues.push(`${path.basename(f)}: ${msg}`);
const colors = new Set();
for (const f of layers) {
  const src = fs.readFileSync(f, 'utf8');
  const vb = src.match(/viewBox="([^"]+)"/);
  if (!vb || vb[1].trim().split(/[\s,]+/).map(Number).join(' ') !== `0 0 ${S} ${S}`) warn(f, `viewBox should be "0 0 ${S} ${S}" (got ${vb ? vb[1] : 'none'})`);
  if (/<text[\s>]/.test(src)) warn(f, '<text> element - convert letterforms to paths; avoid words in icons');
  if (f !== layers[0] && /<filter[\s>]/.test(src)) warn(f, 'filter (blur/shadow) baked into a foreground layer - Icon Composer adds shadow/blur/specular itself');
  if (/<(clipPath|mask)[\s>]/.test(src) && /rx=/.test(src)) warn(f, 'looks like a baked rounded-corner mask - layers must be full-bleed squares, the system masks');
  for (const m of src.matchAll(/#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b/g)) colors.add(m[0].toLowerCase());
}

// Apple system palette values: using them verbatim is the most common tell of generated icons.
const SYSTEM_COLORS = new Set(['#34c759', '#30d158', '#ff9f0a', '#ff9500', '#0a84ff', '#007aff', '#ff3b30', '#ff453a', '#5e5ce6', '#5856d6',
  '#af52de', '#bf5af2', '#ff2d55', '#ff375f', '#ffcc00', '#ffd60a', '#64d2ff', '#5ac8fa', '#1c1c1e', '#2c2c2e', '#3a3a3c', '#48484a',
  '#8e8e93', '#636366', '#aeaeb2', '#c7c7cc', '#d1d1d6', '#e5e5ea', '#f2f2f7']);
const tells = [];
const sys = [...colors].filter(c => SYSTEM_COLORS.has(c));
if (sys.length) tells.push(`Apple system color(s) used verbatim: ${sys.join(', ')} - derive the palette from a named reference instead`);

const pngs = layers.map(f => render(fs.readFileSync(f, 'utf8')));
const flatPng = render(`<svg xmlns="http://www.w3.org/2000/svg" width="${S}" height="${S}">${pngs.map(p => `<image href="${dataUri(p.asPng())}" width="${S}" height="${S}"/>`).join('')}</svg>`);
const flat = flatPng.pixels;

const lum = (px, i) => (0.2126 * px[i] + 0.7152 * px[i + 1] + 0.0722 * px[i + 2]) / 255;

const corner = [0, (S - 1) * 4, (S * (S - 1)) * 4, (S * S - 1) * 4].map(i => flat[i + 3]);
if (corner.some(a => a < 250)) warn(layers[0], 'transparent corners - background must be full-bleed (opaque edge to edge)');

let report = { layers: layers.map(f => path.basename(f)), hexColors: colors.size };
if (pngs.length >= 2) {
  // Foreground = layers above the background, minus scenery planes that run edge to edge horizontally (P8 ground/sea).
  const fg = new Uint8Array(S * S);
  const scenery = [];
  for (const [j, p] of pngs.entries()) {
    if (j === 0) continue;
    const px = p.pixels;
    let spans = false;
    for (let y = 0; y < S && !spans; y += 4) spans = px[(y * S) * 4 + 3] > 128 && px[(y * S + S - 1) * 4 + 3] > 128;
    if (spans) { scenery.push(path.basename(layers[j])); continue; }
    for (let i = 0; i < S * S; i++) if (px[i * 4 + 3] > 128) fg[i] = 1;
  }
  if (scenery.length) report.scenery = scenery;
  let x0 = S, y0 = S, x1 = -1, y1 = -1, fgL = 0, fgN = 0, bgL = 0, bgN = 0;
  for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
    const k = y * S + x, L = lum(flat, k * 4);
    if (fg[k]) { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); fgL += L; fgN++; }
    else { bgL += L; bgN++; }
  }
  if (fgN) {
    const w = (x1 - x0 + 1) / S, h = (y1 - y0 + 1) / S;
    const dL = Math.abs(fgL / fgN - bgL / bgN);
    report = { ...report, fgBox: `${(w * 100).toFixed(0)}% x ${(h * 100).toFixed(0)}%`, fgCenter: `${(((x0 + x1) / 2 / S) * 100).toFixed(0)}%, ${(((y0 + y1) / 2 / S) * 100).toFixed(0)}%`, bleeds: x0 === 0 || y0 === 0 || x1 === S - 1 || y1 === S - 1, tintContrast: +dL.toFixed(2) };
    if (dL < 0.25) warn(layers[1], `foreground/background luminance gap ${dL.toFixed(2)} < 0.25 - icon will mush together in Tinted/Clear modes`);
    let both = 0, either = 0;
    for (let y = 0; y < S; y++) for (let x = 0; x < S / 2; x++) {
      const a = fg[y * S + x], b = fg[y * S + S - 1 - x];
      if (a && b && Math.abs(lum(flat, (y * S + x) * 4) - lum(flat, (y * S + S - 1 - x) * 4)) < 0.08) both++;
      if (a || b) either++;
    }
    const sym = both / either;
    report.mirrorSymmetry = +sym.toFixed(2);
    if (sym > 0.97) tells.push(`mirror symmetry ${sym.toFixed(2)} - perfect left/right symmetry is the generated default; break it unless the idea needs it`);
    const cx = (x0 + x1) / 2 / S, cy = (y0 + y1) / 2 / S;
    if (Math.abs(cx - 0.5) < 0.03 && Math.abs(cy - 0.5) < 0.03 && w > 0.45 && w < 0.66 && h > 0.45 && h < 0.66)
      tells.push('median placement - one centered shape at 45-65% of the canvas; consider a crop, offset or scale move');
  }
}
if (report.hexColors > 6) issues.push(`${report.hexColors} distinct hex colors - premium icons usually need 2-4`);

// Mono + tinted variants simulate the iOS Clear/Tinted appearances (luminance mapped onto one hue).
const tint = [255, 179, 64];
const mono = Buffer.alloc(S * S * 4), tinted = Buffer.alloc(S * S * 4);
for (let i = 0; i < S * S; i++) {
  const L = lum(flat, i * 4), g = Math.round(L * 255);
  mono.set([g, g, g, 255], i * 4);
  tinted.set([Math.round(18 + L * (tint[0] - 18)), Math.round(18 + L * (tint[1] - 18)), Math.round(18 + L * (tint[2] - 18)), 255], i * 4);
}
const rawToPng = buf => render(`<svg xmlns="http://www.w3.org/2000/svg" width="${S}" height="${S}"><image href="${dataUri(encodeRaw(buf))}" width="${S}" height="${S}"/></svg>`).asPng();

// Minimal PNG encoder for raw RGBA buffers (avoids an extra dependency).
function encodeRaw(rgba) {
  const raw = Buffer.alloc((S * 4 + 1) * S);
  for (let y = 0; y < S; y++) { raw[y * (S * 4 + 1)] = 0; rgba.copy(raw, y * (S * 4 + 1) + 1, y * S * 4, (y + 1) * S * 4); }
  const crcTable = Array.from({ length: 256 }, (_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c >>> 0; });
  const crc = b => { let c = 0xffffffff; for (const x of b) c = crcTable[(c ^ x) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
  const chunk = (type, data) => { const len = Buffer.alloc(4); len.writeUInt32BE(data.length); const td = Buffer.concat([Buffer.from(type), data]); const c = Buffer.alloc(4); c.writeUInt32BE(crc(td)); return Buffer.concat([len, td, c]); };
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(S, 0); ihdr.writeUInt32BE(S, 4); ihdr.set([8, 6, 0, 0, 0], 8);
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]);
}

const flatUri = dataUri(flatPng.asPng());
let id = 0;
const tile = (uri, x, y, size) => {
  const c = `m${id++}`;
  return `<clipPath id="${c}"><path d="${squirclePath(size, x, y)}"/></clipPath><image href="${uri}" x="${x}" y="${y}" width="${size}" height="${size}" clip-path="url(#${c})"/>`;
};
const label = (t, x, y, fill) => `<text x="${x}" y="${y}" font-family="Segoe UI, Arial" font-size="15" fill="${fill}">${t}</text>`;
const sizes = [180, 120, 76, 60, 40, 29];
let row = '', rx = 40;
for (const s of sizes) { row += tile(flatUri, rx, 520 + (180 - s), s) + tile(flatUri, rx, 740 + (180 - s), s); rx += s + 28; }
const sheet = `<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="960">
<rect width="1100" height="960" fill="#0b0b0d"/><rect x="0" y="720" width="1100" height="240" fill="#e9e9ee"/>
${tile(flatUri, 40, 40, 420)}${label('Default', 40, 490, '#999')}
${tile(dataUri(rawToPng(mono)), 500, 40, 200)}${label('Mono / Clear (luminance)', 500, 270, '#999')}
${tile(dataUri(rawToPng(tinted)), 500, 290, 200)}${label('Tinted', 500, 520, '#999')}
${row}${label("Home 180 · 120 · Spotlight 76/60 · Settings 40/29 — on dark and light wallpaper", 40, 948, '#555')}
</svg>`;
fs.mkdirSync(path.join(dir, 'preview'), { recursive: true });
const out = path.join(dir, 'preview', 'sheet.png');
fs.writeFileSync(path.join(dir, 'preview', 'icon-1024.png'), flatPng.asPng());
fs.writeFileSync(out, new Resvg(sheet, { font: { loadSystemFonts: true } }).render().asPng());

console.log(JSON.stringify(report, null, 2));
console.log(issues.length ? 'ISSUES:\n- ' + issues.join('\n- ') : 'ISSUES: none');
console.log(tells.length ? `AI-TELLS (${tells.length}):\n- ` + tells.join('\n- ') : 'AI-TELLS (0)');
console.log('sheet:', out);
