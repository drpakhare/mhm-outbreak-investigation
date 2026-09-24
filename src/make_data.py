"""Build the illustrative canteen outbreak dataset used by the deck and the widgets.

Illustrative figures, constructed for teaching. Deterministic: same seed, same data.
Hours are counted from Monday 00:00. Lunch was served Monday 12:30 to 14:00.
Default case definition: a staff member with 3 or more loose stools in 24 hours,
onset between Monday 12:00 and Wednesday 12:00 (hours 12 to 60).
Run:  python3 src/make_data.py   -> data/canteen.json and widgets/canteen-data.js
"""
import json, random, pathlib
random.seed(20260924)
root = pathlib.Path(__file__).resolve().parent.parent

# (biryani, raita, pulao): (ill, well). Built so that raita has no effect once
# you stratify by biryani, and pulao looks protective only because it replaces biryani.
cells = {
    (1, 1, 1): (3, 5),  (1, 1, 0): (34, 43), (1, 0, 1): (1, 1),  (1, 0, 0): (4, 5),
    (0, 1, 1): (1, 21), (0, 1, 0): (0, 3),   (0, 0, 1): (3, 45), (0, 0, 0): (2, 9),
}
people = []
for (b, r, p), (ill, well) in cells.items():
    for k in range(ill):  people.append(dict(biryani=b, raita=r, pulao=p, _ill=1))
    for k in range(well): people.append(dict(biryani=b, raita=r, pulao=p, _ill=0))
random.shuffle(people)
cases = [x for x in people if x['_ill']]
wells = [x for x in people if not x['_ill']]
assert len(people) == 180 and len(cases) == 48

def assign(group, food, n):
    idx = random.sample(range(len(group)), n)
    for i, x in enumerate(group): x[food] = 1 if i in idx else 0
assign(cases, 'dal', 40);   assign(wells, 'dal', 110)
assign(cases, 'salad', 20); assign(wells, 'salad', 50)
assign(cases, 'sweet', 17); assign(wells, 'sweet', 43)

# Onset of cases, 4-hour bins from Monday 12:00 (point-source shape).
bins = [0, 1, 4, 9, 13, 10, 6, 3, 1, 1, 0]
onsets = []
for j, n in enumerate(bins):
    for _ in range(n): onsets.append(12 + 4 * j + random.randint(0, 3) + random.choice([0, .25, .5, .75]))
# the six ill people who did not eat biryani get onsets spread across the window
random.shuffle(onsets)
nonb = [c for c in cases if not c['biryani']]
bir = [c for c in cases if c['biryani']]
onsets.sort()
spread = [onsets[i] for i in (2, 9, 20, 30, 40, 46)]
rest = [o for i, o in enumerate(onsets) if i not in (2, 9, 20, 30, 40, 46)]
random.shuffle(rest)
for c, o in zip(nonb, spread): c['onset'] = o
for c, o in zip(bir, rest): c['onset'] = o

for c in cases:
    c.update(stools=random.choice([3, 4, 4, 5, 6, 6, 7, 8, 10]),
             vomit=int(random.random() < .4), fever=int(random.random() < .65),
             cramps=int(random.random() < .85))

# Non-cases: most well, some with symptoms that a loose case definition would catch.
random.shuffle(wells)
wb = [w for w in wells if w['biryani']]; wn = [w for w in wells if not w['biryani']]
mild = wb[:10] + wn[:4]
vomit_only = wb[10:12] + wn[4:8]
outside = wn[8:12]
for w in wells:
    w.update(stools=0, vomit=0, fever=0, cramps=0, onset=None)
for w in mild:
    w.update(stools=random.choice([1, 2]), cramps=int(random.random() < .5), onset=random.randint(20, 50))
for w in vomit_only:
    w.update(vomit=1, onset=random.randint(16, 48))
for i, w in enumerate(outside):  # background diarrhoea, unrelated to the lunch
    w.update(stools=random.choice([3, 4, 5]), cramps=1, onset=[-14, -6, 78, 90][i])

roles = [('Staff nurse', 34), ('Resident doctor', 22), ('Housekeeping', 14), ('Lab technician', 10),
         ('Admin staff', 12), ('Security', 8)]
wards = {'Staff nurse': ['Medicine', 'Surgery', 'NICU', 'Emergency', 'OT complex'],
         'Resident doctor': ['Medicine', 'Surgery', 'Paediatrics', 'Emergency'],
         'Housekeeping': ['Medicine', 'Surgery', 'NICU', 'OT complex'],
         'Lab technician': ['Laboratory'], 'Admin staff': ['Admin block'], 'Security': ['Main gate', 'Emergency']}
role_pool = [r for r, w in roles for _ in range(w)]
def fmt(h):
    if h is None: return ''
    days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    d = int((h + 24) // 24); hh = h + 24 - d * 24
    return f"{days[d]} {int(hh):02d}:{int(round((hh % 1) * 60)):02d}"

# order ids by onset so the line list reads naturally
people.sort(key=lambda x: (not x['_ill'], x['onset'] is None, x['onset'] if x['onset'] is not None else 0))
out = []
for i, x in enumerate(people, 1):
    role = random.choice(role_pool)
    ill = x['_ill']
    culture = ''
    if ill:
        culture = random.choices(['Salmonella', 'No growth', 'Not sent'], [18, 4, 26])[0]
    out.append(dict(
        id=f"C{i:03d}", age=random.randint(24, 33) if role == 'Resident doctor' else random.randint(22, 56), sex=random.choice('MF' if role != 'Staff nurse' else 'FFFFM'),
        role=role, ward=random.choice(wards[role]),
        onset=x['onset'], onset_label=fmt(x['onset']),
        stools=x['stools'], vomit=x['vomit'], fever=x['fever'], cramps=x['cramps'],
        admitted=int(ill and x['stools'] >= 7 and random.random() < .6),
        culture=culture,
        ate=dict(biryani=x['biryani'], raita=x['raita'], pulao=x['pulao'], dal=x['dal'], salad=x['salad'], sweet=x['sweet'])))

def is_case(p): return p['stools'] >= 3 and p['onset'] is not None and 12 <= p['onset'] < 60
cs = [p for p in out if is_case(p)]
assert len(cs) == 48, len(cs)
foods = ['biryani', 'raita', 'pulao', 'dal', 'salad', 'sweet']
print('food  ate_ill ate_n  AR   not_ill not_n  AR   RR')
for f in foods:
    a = sum(1 for p in out if p['ate'][f] and is_case(p)); n1 = sum(1 for p in out if p['ate'][f])
    c = sum(1 for p in out if not p['ate'][f] and is_case(p)); n0 = 180 - n1
    print(f"{f:7s} {a:3d} {n1:4d} {a/n1:5.1%}  {c:3d} {n0:4d} {c/n0:5.1%} {a/n1/(c/n0):5.2f}")
print('admitted', sum(p['admitted'] for p in out), 'culture+', sum(p['culture'] == 'Salmonella' for p in out))
from collections import Counter
print('bins', [sum(1 for p in cs if 12 + 4*j <= p['onset'] < 16 + 4*j) for j in range(12)])
print('median onset h', sorted(p['onset'] for p in cs)[24])
print('roles of cases', Counter(p['role'] for p in cs))
print('NICU cases', sum(1 for p in cs if p['ward'] == 'NICU'))

meta = dict(note='Illustrative figures, constructed for teaching.', served=240, interviewed=180,
            lunch_start=12.5, lunch_end=14, foods=dict(biryani='Chicken biryani', raita='Raita', pulao='Veg pulao',
            dal='Dal', salad='Salad', sweet='Gulab jamun'))
(root / 'data').mkdir(exist_ok=True)
(root / 'data' / 'canteen.json').write_text(json.dumps(dict(meta=meta, people=out), indent=1))
(root / 'widgets' / 'canteen-data.js').write_text('window.CANTEEN = ' + json.dumps(dict(meta=meta, people=out)) + ';\n')
