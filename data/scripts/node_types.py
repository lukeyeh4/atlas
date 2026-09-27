"""Facility-type defaults for the app: data/node-types.json.

Shape fixed by docs/locale-contract.md ("Facility types"). Reads
data/node-profiles.csv (node_profiles.py). Each value gets its own source
entry, pointing at its first cited URL (the CSV lists them all); values with
no URL point at the CSV itself. Types with no process-water rate (data
centers, AI lab) have no `water`: the app uses the location wue instead.
"""
import csv, datetime, json, re
from common import DATA

CSV_URL = 'https://github.com/lukeyeh4/atlas/blob/main/data/node-profiles.csv'
TYPES = {  # CSV node_type -> (id, display name)
    'mine': ('mine', 'Mine'),
    'materials & wafers': ('materials', 'Materials & wafers'),
    'fab': ('fab', 'Fab'),
    'packaging & test': ('packaging', 'Packaging & test'),
    'equipment & optics': ('equipment', 'Equipment & optics'),
    'data center (training)': ('dc-training', 'Data center (training)'),
    'hardware assembly': ('assembly', 'Hardware assembly'),
    'AI lab (offices)': ('lab', 'AI lab'),
    'data center (inference)': ('dc-inference', 'Data center (inference)'),
}
LABEL = {'p': 'power', 'u': 'utilisation', 'pue': 'PUE', 'g': 'growth', 'water': 'process water'}
CONVENTION = 'Model convention'


def first_sentence(s):
    """Up to the first full stop outside brackets that starts a new sentence."""
    s, depth = s.strip(), 0
    for i, ch in enumerate(s):
        depth += {'(': 1, ')': -1}.get(ch, 0)
        if ch == '.' and depth == 0 and re.match(r'\s+[A-Z]', s[i + 1:]):
            return s[:i + 1]
    return s


def short(s, n=160):
    return s if len(s) <= n else s[:n - 1].rstrip() + '…'


types, sources = {}, {}
for r in csv.DictReader(open(DATA / 'node-profiles.csv', encoding='utf-8')):
    if r['node_type'] not in TYPES or not r['default']:
        continue
    tid, name = TYPES[r['node_type']]
    t = types.setdefault(tid, {'n': name, 'stage': r['stage']})
    k = r['input']
    if r['basis'].startswith(CONVENTION):
        src = 'model-convention'
        sources[src] = {'title': 'Model convention: p is average draw from annual consumption, '
                                 'so utilisation and overhead are already inside it', 'url': CSV_URL}
    else:
        src = f'{tid}-{k}'
        urls = r['source_urls'].split()
        sources[src] = {'title': short(f"{name} {LABEL[k]}: {r['evidence'] or first_sentence(r['basis'])}"),
                        'url': urls[0] if urls else CSV_URL}
    x = {'v': float(r['default'])}
    for b in ('low', 'high'):
        if r[b]:
            x[b] = float(r[b])
    x.update(conf=r['confidence'], src=src)
    if k == 'water':
        x['basis'] = 'withdrawal'
    if src != 'model-convention':
        x['note'] = short(first_sentence(r['basis']), 200)
    t[k] = x

doc = {'v': 1, 'built': datetime.date.today().isoformat(), 'types': types, 'sources': dict(sorted(sources.items()))}
(DATA / 'node-types.json').write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'wrote data/node-types.json ({len(types)} types, {len(sources)} sources)')
