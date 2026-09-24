# Outbreak investigation for hospital managers

**Live site:** https://drpakhare.github.io/mhm-outbreak-investigation/

A 60-minute reveal.js session for Masters in Hospital Management students, built in the
house style of `intro-economic-evaluation-health`. It follows one illustrative outbreak
(Salmonella from a staff-canteen chicken biryani) through every step of an investigation.

## Layout
- `index.html`: landing page linking the slides and both labs (served by GitHub Pages from `main`, root)
- `slides/outbreak-investigation.html`: the deck (25 slides, speaker notes on every slide; press S for speaker view)
- `widgets/`: two student labs using the same 180-interview dataset
  - `case-definition.html`: change the case definition, watch the epi curve and relative risk
  - `attack-rate-lab.html`: 2 by 2 tables per dish, stratify by biryani to see confounding
- `data/canteen.json`: the illustrative line list (made by `src/make_data.py`, deterministic)
- `src/epicurve.py`: redraws the two epi-curve SVGs in the deck from the data
- `src/chk.mjs`: checker (slide count, overflow past 700 px, text under 14 pt, em dashes, JS errors)
- `src/bundle.py`: writes single-file offline copies to `dist/` (not committed)
- `vendor/reveal.js`: reveal.js 5 (MIT), trimmed to the core and the notes plugin
- `assets/css/tokens.css`, `assets/css/slides.css`: **reconstructed** from the style brief.
  Replace with the originals from the economics repo for an exact match.

## Check
    npm install
    python3 -m http.server 8765 &
    node src/chk.mjs outbreak-investigation     # must print "all clean"

All outbreak figures are illustrative, constructed for teaching.
