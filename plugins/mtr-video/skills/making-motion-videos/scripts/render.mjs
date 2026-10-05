#!/usr/bin/env node
// Deterministic frame renderer for seek(t) pages: headless Chromium -> PNG -> ffmpeg.
//
//   node render.mjs lint  <page.html>
//   node render.mjs stills <page.html> --t 0,1.5,3,4.5 [--out probe] [--w 1920 --h 1080]
//   node render.mjs beats  <page.html> --bpm 120 [--out probe]          # one frame per beat -> sheet
//   node render.mjs video  <page.html> --out out/video.mp4 [--fps 60] [--sub 6] [--shutter 0.5]
//                          [--from 0 --to 6] [--workers 3] [--audio out/mix.wav] [--crf 16]
//   node render.mjs determinism <page.html> --t 1.2,3.7,0.4
//   node render.mjs splice <film.mp4> <part.mp4> --at 4.0 [--out film.fixed.mp4]   # replace a re-rendered range
//
// <page> may be a local .html (served over a built-in static http server rooted at its folder)
// or an http(s) URL. The page must expose window.seek(t), window.ready, window.FILM={duration,fps}.
// Requires: `playwright` resolvable from the current folder (npm i -D playwright) and ffmpeg on PATH.
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const require = createRequire(path.join(process.cwd(), 'noop.js'));
let chromium;
try { ({ chromium } = require('playwright')); }
catch { try { ({ chromium } = createRequire(import.meta.url)('playwright')); }
  catch { console.error('playwright not found: run `npm i -D playwright` in the project folder'); process.exit(1); } }

const [mode, page, ...rest] = process.argv.slice(2);
const opt = {};
for (let i = 0; i < rest.length; i++) if (rest[i].startsWith('--')) {
  const k = rest[i].slice(2), v = rest[i + 1] && !rest[i + 1].startsWith('--') ? rest[++i] : 'true'; opt[k] = v; }
if (!mode || !page) { console.error(fs.readFileSync(new URL(import.meta.url)).toString().split('\n').slice(1, 14).join('\n')); process.exit(1); }

const W = +(opt.w || 1920), H = +(opt.h || 1080);
const sh = (cmd, args, input) => new Promise((res, rej) => {
  const p = spawn(cmd, args, { stdio: [input ? 'pipe' : 'ignore', 'ignore', 'pipe'] });
  let err = ''; p.stderr.on('data', d => err += d);
  p.on('close', c => c === 0 ? res() : rej(new Error(`${cmd} exited ${c}\n${err.slice(-2000)}`)));
  if (input) input(p.stdin);
});

// ---------- lint: catch real-time clocks before they cost a render ----------
function lint(file) {
  if (/^https?:/.test(file)) return [];
  const bad = [
    [/\bsetTimeout\s*\(|\bsetInterval\s*\(/, 'timer'], [/requestAnimationFrame/, 'requestAnimationFrame'],
    [/Date\.now\(|performance\.now\(/, 'wall clock'], [/Math\.random\(/, 'unseeded Math.random'],
    [/transition\s*:|\.transition\s*=/, 'CSS transition'], [/animation\s*:|@keyframes/, 'CSS animation (only OK if driven by seek via animation-delay/paused)'],
    [/autoplay\s*:\s*true|\.play\(\)/, 'real-time playback'],
  ];
  const out = [];
  const src = fs.readFileSync(file, 'utf8')
    .replace(/<!--[\s\S]*?-->/g, m => m.replace(/[^\n]/g, ' '))      // drop HTML comments, keep line numbers
    .replace(/\/\*[\s\S]*?\*\//g, m => m.replace(/[^\n]/g, ' '));    // drop block comments
  src.split('\n').forEach((raw, i) => {
    if (/preview-only/.test(raw)) return;
    const line = raw.replace(/(^|[\s;{}])\/\/.*$/, '$1');            // drop line comments
    for (const [re, what] of bad) if (re.test(line)) out.push(`${file}:${i + 1}: ${what}: ${line.trim().slice(0, 100)}`);
  });
  return out;
}

// ---------- static server ----------
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.webp': 'image/webp',
  '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.otf': 'font/otf', '.mp4': 'video/mp4', '.webm': 'video/webm',
  '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.glb': 'model/gltf-binary' };
async function serve(file) {
  if (/^https?:/.test(file)) return { url: file, close: () => {} };
  const root = path.dirname(path.resolve(file));
  const srv = http.createServer((req, res) => {
    const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
    if (!p.startsWith(root) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(p).toLowerCase()] || 'application/octet-stream' });
    fs.createReadStream(p).pipe(res);
  });
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  return { url: `http://127.0.0.1:${srv.address().port}/${path.basename(file)}`, close: () => srv.close() };
}
const withSize = u => u + (u.includes('?') ? '&' : '?') + `w=${W}&h=${H}`;

async function openPage(browser, url) {
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  const pg = await ctx.newPage();
  const errors = []; pg.on('pageerror', e => errors.push(String(e)));
  await pg.goto(withSize(url), { waitUntil: 'load' });
  await pg.waitForFunction(() => window.ready === true && typeof window.seek === 'function', null, { timeout: 60000 })
    .catch(() => { throw new Error('page never set window.ready = true (or has no window.seek). Errors: ' + errors.join(' | ')); });
  await pg.evaluate(() => document.fonts.ready);
  const film = await pg.evaluate(() => window.FILM || {});
  return { pg, film, errors };
}
async function shot(pg, t) {
  await pg.evaluate(async tt => { await window.seek(tt); }, t);
  await pg.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))); // let layout+paint settle
  return pg.screenshot({ type: 'png' });
}

async function stills(times, outDir, tag = 'still') {
  fs.mkdirSync(outDir, { recursive: true });
  const s = await serve(page), browser = await chromium.launch();
  try {
    const { pg } = await openPage(browser, s.url);
    const files = [];
    for (const t of times) { const f = path.join(outDir, `${tag}_${t.toFixed(3)}.png`); fs.writeFileSync(f, await shot(pg, t)); files.push(f); }
    const cols = Math.min(4, files.length), rows = Math.ceil(files.length / cols);
    await sh('ffmpeg', ['-y', '-v', 'error', ...files.flatMap(f => ['-i', f]), '-filter_complex',
      files.map((_, i) => `[${i}:v]scale=480:-2,drawtext=text='${times[i].toFixed(2)}s':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6[v${i}]`).join(';') + ';' +
      files.map((_, i) => `[v${i}]`).join('') + (files.length > 1 ? `xstack=inputs=${files.length}:layout=${files.map((_, i) => `${(i % cols) * 480}_${Math.floor(i / cols) * (2 * Math.round(240 * H / W))}`).join('|')}:fill=black` : 'null'),
      path.join(outDir, 'sheet.png')]).catch(e => console.error('sheet failed (stills still written):', e.message.split('\n')[0]));
    console.log(`wrote ${files.length} stills + ${path.join(outDir, 'sheet.png')}  (${rows}x${cols}) -> LOOK AT THE SHEET before a full render`);
  } finally { await browser.close(); s.close(); }
}

async function video() {
  const out = opt.out || 'out/video.mp4'; fs.mkdirSync(path.dirname(out), { recursive: true });
  const s = await serve(page), browser = await chromium.launch();
  try {
    const probe = await openPage(browser, s.url); await probe.pg.context().close();
    const fps = +(opt.fps || probe.film.fps || 60), sub = Math.max(1, +(opt.sub || 1)), shutter = +(opt.shutter || 0.5);
    const dur = +(opt.to || probe.film.duration) - +(opt.from || 0);
    const f0 = Math.round(+(opt.from || 0) * fps), f1 = f0 + Math.round(dur * fps);
    const workers = Math.max(1, Math.min(+(opt.workers || 1), f1 - f0));
    const crf = opt.crf || '16';
    const vf = (sub > 1 ? `tmix=frames=${sub},select='eq(mod(n\\,${sub})\\,${sub - 1})',setpts=N/(${fps}*TB),` : '') +
      'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p';
    const encArgs = (o) => ['-y', '-v', 'error', '-f', 'image2pipe', '-c:v', 'png', '-framerate', String(fps * sub), '-i', '-',
      '-vf', vf, '-r', String(fps), '-c:v', 'libx264', '-preset', opt.preset || 'medium', '-crf', crf,
      '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', o];
    const per = Math.ceil((f1 - f0) / workers), parts = [];
    console.log(`render ${f1 - f0} frames @${fps}fps x${sub} subframes (shutter ${shutter}) with ${workers} worker(s)`);
    let done = 0; const tStart = Date.now();
    await Promise.all([...Array(workers)].map(async (_, wi) => {
      const a = f0 + wi * per, b = Math.min(f1, a + per); if (a >= b) return;
      const part = workers > 1 ? out.replace(/\.mp4$/, `.part${wi}.mp4`) : out; parts[wi] = part;
      const { pg, errors } = await openPage(browser, s.url);
      await sh('ffmpeg', encArgs(part), async stdin => {
        for (let f = a; f < b; f++) for (let j = 0; j < sub; j++) {
          const t = (f + shutter * (j / sub)) / fps;
          const buf = await shot(pg, t);
          if (!stdin.write(buf)) await new Promise(r => stdin.once('drain', r));
          if (j === sub - 1 && ++done % 60 === 0) console.log(`  ${done}/${f1 - f0} frames, ${((Date.now() - tStart) / done).toFixed(0)} ms/frame`);
        }
        stdin.end();
      });
      if (errors.length) console.warn(`worker ${wi} page errors:`, errors.slice(0, 3));
      await pg.context().close();
    }));
    if (workers > 1) {
      const list = out + '.txt'; fs.writeFileSync(list, parts.filter(Boolean).map(p => `file '${path.resolve(p)}'`).join('\n'));
      await sh('ffmpeg', ['-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', out + '.tmp.mp4']);
      fs.renameSync(out + '.tmp.mp4', out); parts.forEach(p => p && fs.rmSync(p)); fs.rmSync(list);
    }
    if (opt.audio) {
      const muxed = out.replace(/\.mp4$/, '.final.mp4');
      await sh('ffmpeg', ['-y', '-v', 'error', '-i', out, '-i', opt.audio, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
        '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', muxed]);
      console.log('muxed ->', muxed);
    }
    console.log(`done -> ${out} in ${((Date.now() - tStart) / 1000).toFixed(0)} s. Next: python3 qa.py report ${out}`);
  } finally { await browser.close(); s.close(); }
}

async function determinism(times) {
  const s = await serve(page), browser = await chromium.launch();
  try {
    const A = await openPage(browser, s.url), B = await openPage(browser, s.url);
    const h = b => crypto.createHash('sha1').update(b).digest('hex');
    const ha = {}, hb = {};
    for (const t of times) ha[t] = h(await shot(A.pg, t));
    for (const t of [...times].reverse()) { await shot(B.pg, Math.max(0, t - 0.37)); hb[t] = h(await shot(B.pg, t)); }
    let ok = true;
    for (const t of times) { const same = ha[t] === hb[t]; ok &&= same; console.log(`t=${t}: ${same ? 'identical' : 'DIFFERENT'}`); }
    if (!ok) console.log('Causes, most likely first: state carried between seek() calls, a clock/timer, unseeded randomness, ' +
      'or Chromium compositing (anti-aliasing differs when a layer was promoted by an earlier transform). Fixes for the last one: ' +
      'set settled transforms to "none" instead of identity values, draw dense repeated shapes on one canvas from t, avoid will-change.');
    process.exitCode = ok ? 0 : 2;
  } finally { await browser.close(); s.close(); }
}

async function splice(base, part) {
  // replace frames [at, at+dur(part)) of base with part; re-encodes once (crf 16) so codecs/params always match
  const at = +opt.at, out = opt.out || base.replace(/\.mp4$/, '.spliced.mp4');
  const dur = s => new Promise(r => { const p = spawn('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', s]);
    let o = ''; p.stdout.on('data', d => o += d); p.on('close', () => r(+o)); });
  const dp = await dur(part), db = await dur(base);
  await sh('ffmpeg', ['-y', '-v', 'error', '-i', base, '-i', part, '-filter_complex',
    `[0:v]trim=0:${at},setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[0:v]trim=${at + dp}:${db},setpts=PTS-STARTPTS[c];` +
    `[a][b][c]concat=n=3:v=1:a=0,format=yuv420p[v]`, '-map', '[v]', '-map', '0:a?', '-c:a', 'copy',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', opt.crf || '16', '-color_range', 'tv', '-colorspace', 'bt709',
    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-movflags', '+faststart', out]);
  console.log(`spliced ${part} at ${at}s (${dp.toFixed(3)} s) -> ${out}. Check the seams: python3 qa.py sheets ${out} --strip ${at},${(at + dp).toFixed(2)}`);
}

const times = (opt.t || '').split(',').filter(Boolean).map(Number);
if (mode === 'splice') { await splice(page, rest[0]); process.exit(0); }
const warn = lint(page);
if (mode === 'lint') { console.log(warn.length ? warn.join('\n') : 'lint: clean'); process.exitCode = warn.length ? 2 : 0; }
else {
  if (warn.length) console.warn('LINT WARNINGS (fix before trusting the render):\n' + warn.join('\n'));
  if (mode === 'stills') await stills(times.length ? times : [0, 1, 2, 3], opt.out || 'probe');
  else if (mode === 'beats') {
    const s = await serve(page), b = await chromium.launch(); const { film } = await openPage(b, s.url); await b.close(); s.close();
    const beat = 60 / +(opt.bpm || 120), ts = []; for (let t = 0; t < (film.duration || 10) - 1e-6; t += beat) ts.push(+t.toFixed(4));
    await stills(ts, opt.out || 'probe', 'beat');
  }
  else if (mode === 'video') await video();
  else if (mode === 'determinism') await determinism(times.length ? times : [0.5, 1.7, 3.3]);
  else { console.error('unknown mode', mode); process.exit(1); }
}
