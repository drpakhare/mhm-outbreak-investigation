"""Make single-file copies of the deck and the labs (all CSS, JS and data inlined)
for sharing as standalone pages. Output goes to dist/.
Usage: python3 src/bundle.py [lab1_url lab2_url]   (optional: links the deck's lab slide to hosted labs)
"""
import re, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
dist = root / 'dist'; dist.mkdir(exist_ok=True)

def inline(path, links=None):
    base = path.parent
    html = path.read_text()
    html = re.sub(r'<link rel="stylesheet" href="([^"]+)">', lambda m: '<style>\n' + (base / m.group(1)).read_text() + '\n</style>', html)
    html = re.sub(r'<script src="([^"]+)"></script>', lambda m: '<script>\n' + (base / m.group(1)).read_text().replace('</script', '<\\/script') + '\n</script>', html)
    for k, v in (links or {}).items():
        html = html.replace(f'href="{k}"', f'href="{v}" target="_blank" rel="noopener"')
    return html

links = {}
if len(sys.argv) == 3:
    links = {'../widgets/case-definition.html': sys.argv[1], '../widgets/attack-rate-lab.html': sys.argv[2]}
deck = inline(root / 'slides' / 'outbreak-investigation.html', links)
deck = deck.replace('<style>\n  /* per-deck', '<style>\n  html, body { background: #ffffff; }\n  /* per-deck', 1)
(dist / 'outbreak-investigation.html').write_text(deck)
for w in ('case-definition', 'attack-rate-lab'):
    (dist / f'{w}.html').write_text(inline(root / 'widgets' / f'{w}.html'))
for f in sorted(dist.iterdir()): print(f.name, f.stat().st_size // 1024, 'KB')
