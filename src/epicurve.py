"""Draw the epidemic curve SVGs from data/canteen.json and insert them into the deck.
Replaces everything between <!--EPI:name--> and <!--/EPI--> markers in the slide file.
Run: python3 src/epicurve.py
"""
import json, re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
people = json.loads((root / 'data' / 'canteen.json').read_text())['people']
cases = [p for p in people if p['stools'] >= 3 and p['onset'] is not None and 12 <= p['onset'] < 60]

H0, H1, BIN = -12, 60, 4                     # Sunday 12:00 to Wednesday 12:00, hours from Monday 00:00
X0, W, BASE = 70, 1066, 330
nb = (H1 - H0) // BIN
bw = W / nb
BOX, GAP = 21, 2

def x(h): return X0 + (h - H0) / (H1 - H0) * W

def svg(variant):
    counts = [0] * nb
    for p in cases: counts[int((p['onset'] - H0) // BIN)] += 1
    s = [f'<svg class="epi" viewBox="0 0 1152 392" role="img" aria-label="Epidemic curve: {len(cases)} cases by 4-hour onset interval, one peak on Tuesday morning">']
    if variant == 'window':
        a, b = 31.5 - 36, 31.5 - 12
        s.append(f'<rect class="win" x="{x(a):.1f}" y="18" width="{x(b)-x(a):.1f}" height="{BASE-18}"/>')
        s.append(f'<text class="lbl" x="{(x(a)+x(b))/2:.1f}" y="46" text-anchor="middle">Likely exposure</text>')
        s.append(f'<text class="lbl dimt" x="{(x(a)+x(b))/2:.1f}" y="70" text-anchor="middle">12 to 36 h before</text>')

    # y grid
    for v in (5, 10):
        y = BASE - v * (BOX + GAP)
        s.append(f'<line class="grid" x1="{X0}" x2="{X0+W}" y1="{y:.1f}" y2="{y:.1f}"/>')
        s.append(f'<text class="tick" x="{X0-12}" y="{y+6:.1f}" text-anchor="end">{v}</text>')
    s.append(f'<text class="tick" x="{X0-12}" y="{BASE+6}" text-anchor="end">0</text>')
    # one box per case
    for i, n in enumerate(counts):
        for k in range(n):
            s.append(f'<rect class="case" x="{X0 + i*bw + GAP:.1f}" y="{BASE - (k+1)*(BOX+GAP) + GAP:.1f}" width="{bw - 2*GAP:.1f}" height="{BOX}" rx="2"/>')
    if variant == 'window':
        s.append(f'<line class="halo" x1="{x(31.5):.1f}" x2="{x(31.5):.1f}" y1="18" y2="{BASE}"/>')
        s.append(f'<line class="med" x1="{x(31.5):.1f}" x2="{x(31.5):.1f}" y1="18" y2="{BASE}"/>')
        s.append(f'<text class="lbl" x="{x(31.5)+10:.1f}" y="40">Median onset, Tue 07:30</text>')
        s.append(f'<line class="lunch" x1="{x(13.25):.1f}" x2="{x(13.25):.1f}" y1="130" y2="{BASE}"/>')
        s.append(f'<circle class="lunchdot" cx="{x(13.25):.1f}" cy="130" r="6"/>')
        s.append(f'<text class="lbl" x="{x(13.25):.1f}" y="116" text-anchor="middle">Mon lunch</text>')
    s.append(f'<line class="axis" x1="{X0}" x2="{X0+W}" y1="{BASE}" y2="{BASE}"/>')
    for h, lab in [(-12, 'Sun 12:00'), (0, 'Mon 00:00'), (12, 'Mon 12:00'), (24, 'Tue 00:00'), (36, 'Tue 12:00'), (48, 'Wed 00:00'), (60, 'Wed 12:00')]:
        s.append(f'<line class="axis" x1="{x(h):.1f}" x2="{x(h):.1f}" y1="{BASE}" y2="{BASE+8}"/>')
        anchor = 'start' if h == H0 else 'end' if h == H1 else 'middle'
        s.append(f'<text class="tick" x="{x(h):.1f}" y="{BASE+32}" text-anchor="{anchor}">{lab}</text>')
    s.append(f'<text class="tick dimt" x="{X0}" y="{BASE+60}">Each box is one case. Onset of diarrhoea, 4-hour intervals.</text>')
    s.append('</svg>')
    return '\n'.join(s)

deck = root / 'slides' / 'outbreak-investigation.html'
html = deck.read_text()
for name in ('plain', 'window'):
    html = re.sub(rf'<!--EPI:{name}-->.*?<!--/EPI-->', lambda m: f'<!--EPI:{name}-->\n{svg(name)}\n<!--/EPI-->', html, flags=re.S)
deck.write_text(html)
print('curves inserted', len(cases), 'cases')
