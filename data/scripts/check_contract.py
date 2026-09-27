"""Check data/locales.json, data/cells/ and data/node-types.json against
docs/locale-contract.md; exit non-zero on any problem, so build_all.py stops
before files the app would reject are committed.

    python3 data/scripts/check_contract.py
"""
import json, math, re, sys
from common import DATA

KEYS = {'ci', 'fos', 'dec', 'ws', 'wue', 'wue_disclosed', 'pm25'}
CONF = {'measured', 'disclosed', 'estimated', 'projected'}
FIELDS = {'v', 'conf', 'src', 'year', 'basis', 'note'}
RANGE = {'fos': (0, 1), 'ws': (0, 1), 'dec': (-1, 1)}      # everything else: >= 0
RES, TILE = 0.25, 10
CODE = {'countries': re.compile(r'^[A-Z]{2}$'), 'subdivisions': re.compile(r'^[A-Z]{2}-[A-Z0-9]{1,3}$')}


def problems(d, cited=()):
    """Problems in locales.json; `cited` are source ids the cell tiles use."""
    if d.get('v') != 1:
        yield f"v is {d.get('v')!r}, expected 1"
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(d.get('built', ''))):
        yield 'built is not a date'
    used = set(cited)
    for level in ('countries', 'subdivisions'):
        for code, e in d.get(level, {}).items():
            at = f'{level}.{code}'
            if not CODE[level].match(code):
                yield f'{at}: bad code'
            if level == 'subdivisions' and code[:2] not in d['countries']:
                yield f'{at}: no country entry {code[:2]}'
            if not isinstance(e.get('n'), str) or not e['n'].strip():
                yield f'{at}: missing name'
            for k, x in e.items():
                if k == 'n':
                    continue
                if k not in KEYS:
                    yield f'{at}.{k}: unknown key'
                    continue
                if not isinstance(x, dict) or set(x) - FIELDS:
                    yield f'{at}.{k}: unexpected fields {sorted(set(x) - FIELDS) if isinstance(x, dict) else x}'
                    continue
                v = x.get('v')
                if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
                    yield f'{at}.{k}: v is {v!r}'
                else:
                    lo, hi = RANGE.get(k, (0, math.inf))
                    if not lo <= v <= hi:
                        yield f'{at}.{k}: v {v} outside {lo}..{hi}'
                if x.get('conf') not in CONF:
                    yield f"{at}.{k}: conf {x.get('conf')!r}"
                if x.get('src') not in d.get('sources', {}):
                    yield f"{at}.{k}: src {x.get('src')!r} not in sources"
                used.add(x.get('src'))
                if '\n' in str(x.get('note', '')):
                    yield f'{at}.{k}: note has a line break'
    for s, x in d.get('sources', {}).items():
        if not x.get('title') or not str(x.get('url', '')).startswith('http'):
            yield f'sources.{s}: needs a title and an http(s) url'
        if s not in used:
            yield f'sources.{s}: unused'


def cell_problems(sources, cited):
    """Problems in data/cells/; adds the source ids tiles cite to `cited`."""
    folder = DATA / 'cells'
    try:
        index = json.load(open(folder / 'index.json', encoding='utf-8'))
    except FileNotFoundError:
        return
    if index.get('v') != 1 or index.get('res') != RES:
        yield 'cells/index.json: expected v 1 and res 0.25'
    for k, x in index.get('absent', {}).items():
        if not isinstance(x, dict) or set(x) - FIELDS or x.get('conf') not in CONF or x.get('src') not in sources \
                or isinstance(x.get('v'), bool) or not isinstance(x.get('v'), (int, float)):
            yield f'cells/index.json: absent.{k} is not a valid value'
        cited.add(x.get('src') if isinstance(x, dict) else None)
    files = {p.stem for p in folder.glob('*.json')} - {'index'}
    if set(index.get('tiles', [])) != files:
        yield f"cells/index.json: tiles list differs from files ({len(index.get('tiles', []))} listed, {len(files)} files)"
    for tid in sorted(files):
        t = json.load(open(folder / f'{tid}.json', encoding='utf-8'))
        at = f'cells/{tid}'
        if t.get('v') != 1 or t.get('tile') != tid or t.get('res') != RES:
            yield f'{at}: v, tile or res wrong'
        keys, meta = t.get('keys', []), t.get('meta', {})
        for k in keys:
            m = meta.get(k, {})
            if m.get('conf') not in CONF or m.get('src') not in sources:
                yield f'{at}: meta.{k} needs a known conf and a src in locales.json sources'
            cited.add(m.get('src'))
        s0, w0 = (int(x) for x in tid.split('_'))
        for key, vals in t.get('cells', {}).items():
            lat, lon = (float(x) for x in key.split(','))
            if not (s0 <= lat < s0 + TILE and w0 <= lon < w0 + TILE) or (lat / RES) % 1 != 0.5 or (lon / RES) % 1 != 0.5:
                yield f'{at}: cell {key} is not a cell centre in this tile'
                break
            if len(vals) != len(keys) or all(v is None for v in vals) or \
                    any(v is not None and (isinstance(v, bool) or not isinstance(v, (int, float))) for v in vals):
                yield f'{at}: cell {key} has bad values {vals}'
                break


TYPE_IDS = {'mine', 'materials', 'fab', 'packaging', 'equipment', 'dc-training', 'assembly', 'lab', 'dc-inference'}
STAGES = {'raw', 'chip', 'infra', 'model', 'delivery'}
TYPE_FIELDS = {'v', 'low', 'high', 'conf', 'src', 'basis', 'note'}


def type_problems(d):
    """Problems in node-types.json."""
    if d.get('v') != 1 or not re.match(r'^\d{4}-\d{2}-\d{2}$', str(d.get('built', ''))):
        yield 'node-types.json: needs v 1 and a built date'
    types, sources, used = d.get('types', {}), d.get('sources', {}), set()
    if set(types) != TYPE_IDS:
        yield f'node-types.json: types {sorted(set(types) ^ TYPE_IDS)} missing or unknown'
    for tid, t in types.items():
        at = f'types.{tid}'
        if not isinstance(t.get('n'), str) or t.get('stage') not in STAGES:
            yield f'{at}: needs a name and a stage'
        for k in {'p', 'u', 'pue', 'g'} - set(t):
            yield f'{at}: missing {k}'
        if tid.startswith('dc-') and 'water' in t:
            yield f'{at}: data centers take water from the location wue'
        for k, x in t.items():
            if k in ('n', 'stage'):
                continue
            if k not in {'p', 'u', 'pue', 'g', 'water'} or not isinstance(x, dict) or set(x) - TYPE_FIELDS:
                yield f'{at}.{k}: unknown key or fields'
                continue
            nums = [x.get(f) for f in ('low', 'v', 'high') if f in x]
            if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in nums) or nums != sorted(nums):
                yield f'{at}.{k}: needs numbers with low <= v <= high'
            if x.get('conf') not in CONF or x.get('src') not in sources:
                yield f'{at}.{k}: needs a known conf and a src in sources'
            used.add(x.get('src'))
    for s, x in sources.items():
        if not x.get('title') or not str(x.get('url', '')).startswith('http'):
            yield f'node-types sources.{s}: needs a title and an http(s) url'
        if s not in used:
            yield f'node-types sources.{s}: unused'


if __name__ == '__main__':
    d = json.load(open(DATA / 'locales.json', encoding='utf-8'))
    cited = set()
    found = list(cell_problems(d.get('sources', {}), cited)) + list(problems(d, cited))
    found += list(type_problems(json.load(open(DATA / 'node-types.json', encoding='utf-8'))))
    for p in found:
        print('  ' + p)
    if found:
        sys.exit(f'contract check: {len(found)} problems')
    print('locales.json, cells and node-types.json: match the contract')
