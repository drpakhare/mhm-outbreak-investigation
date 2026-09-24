// Deck checker. Usage (from repo root, with `python3 -m http.server 8765` running):
//   node src/chk.mjs outbreak-investigation
// Reports slide count, overflow past 700 px, text under 14 pt, em dashes, JS errors.
// Set CHROMIUM=/path/to/chrome if Chromium is not found automatically.
import { chromium } from 'playwright-core';
import fs from 'node:fs';

const name = process.argv[2];
if (!name) { console.error('usage: node src/chk.mjs <deck-name>'); process.exit(2); }
const port = process.env.PORT || 8765;
const url = `http://localhost:${port}/slides/${name}.html`;

const candidates = [process.env.CHROMIUM, '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'].filter(Boolean);
const executablePath = candidates.find(p => fs.existsSync(p));
const browser = await chromium.launch(executablePath ? { executablePath } : {});
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
const errors = [];
page.on('pageerror', e => errors.push(e.message));
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
page.on('requestfailed', r => errors.push('failed to load ' + r.url()));

await page.goto(url, { waitUntil: 'load' });
await page.waitForFunction(() => window.Reveal && Reveal.isReady());
await page.waitForTimeout(300);

const report = await page.evaluate(async () => {
  const LIMIT = 700, MINPX = 18.6; // 14 pt = 18.67 px
  const slides = Reveal.getSlides();
  const out = [];
  for (let i = 0; i < slides.length; i++) {
    Reveal.slide(i);
    await new Promise(r => setTimeout(r, 60));
    const s = slides[i];
    const top = s.getBoundingClientRect().top;
    const scale = Reveal.getScale();
    let bottom = 0, small = new Set(), culprit = '';
    for (const el of s.querySelectorAll('*')) {
      if (el.closest('aside.notes')) continue;
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      if (el.closest('.cite')) continue; // footer line sits in the margin by design
      const r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) continue;
      const b = (r.bottom - top) / scale;
      if (b > bottom) { bottom = b; culprit = el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ').join('.') : ''); }
      const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
      if (hasText && parseFloat(cs.fontSize) < MINPX && !el.closest('svg')) small.add(el.tagName.toLowerCase() + ' ' + cs.fontSize);
      if (el.tagName === 'text' && el.closest('svg')) {
        // SVG text: effective size = font-size * (rendered width / viewBox width)
        const svg = el.ownerSVGElement; const vb = svg.viewBox.baseVal;
        const k = vb && vb.width ? svg.getBoundingClientRect().width / scale / vb.width : 1;
        const px = parseFloat(cs.fontSize) * k;
        if (px < MINPX) small.add('svg text ' + px.toFixed(1) + 'px');
      }
    }
    const title = (s.querySelector('h2, h1')?.textContent || '').trim().slice(0, 60);
    const hasNotes = !!s.querySelector('aside.notes');
    out.push({ i: i + 1, title, bottom: Math.round(bottom), culprit, small: [...small], hasNotes });
  }
  const text = document.body.innerText + [...document.querySelectorAll('aside.notes')].map(n => n.textContent).join(' ');
  const html = document.documentElement.outerHTML;
  const em = (html.match(/—|&mdash;/g) || []).length;
  return { out, em };
});
await browser.close();

let problems = 0;
console.log(`deck: ${name}`);
console.log(`slides: ${report.out.length}`);
for (const s of report.out) {
  const flags = [];
  if (s.bottom > 700) flags.push(`OVERFLOW bottom=${s.bottom}px (${s.culprit})`);
  if (s.small.length) flags.push('UNDER 14pt: ' + s.small.join(', '));
  if (!s.hasNotes) flags.push('NO NOTES');
  if (flags.length) problems += flags.length;
  console.log(`${String(s.i).padStart(2)}  ${String(s.bottom).padStart(3)}px  ${s.title}${flags.length ? '\n      ' + flags.join('\n      ') : ''}`);
}
console.log(`em dashes: ${report.em}`); if (report.em) problems++;
console.log(`js errors: ${errors.length}`); errors.forEach(e => console.log('  ' + e)); problems += errors.length;
console.log(problems ? `${problems} problem(s)` : 'all clean');
process.exit(problems ? 1 : 0);
