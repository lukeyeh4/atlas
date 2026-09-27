"""Check data/locales.json against docs/locale-contract.md; exit non-zero on
any problem, so build_all.py stops before a file the app would reject is
committed.

    python3 data/scripts/check_locales.py
"""
import json, math, re, sys
from common import DATA

KEYS = {'ci', 'fos', 'dec', 'ws', 'wue', 'wue_disclosed', 'pm25'}
CONF = {'measured', 'disclosed', 'estimated', 'projected'}
FIELDS = {'v', 'conf', 'src', 'year', 'basis', 'note'}
RANGE = {'fos': (0, 1), 'ws': (0, 1), 'dec': (-1, 1)}      # everything else: >= 0
CODE = {'countries': re.compile(r'^[A-Z]{2}$'), 'subdivisions': re.compile(r'^[A-Z]{2}-[A-Z0-9]{1,3}$')}


def problems(d):
    if d.get('v') != 1:
        yield f"v is {d.get('v')!r}, expected 1"
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(d.get('built', ''))):
        yield 'built is not a date'
    used = set()
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


if __name__ == '__main__':
    found = list(problems(json.load(open(DATA / 'locales.json', encoding='utf-8'))))
    for p in found:
        print('  ' + p)
    if found:
        sys.exit(f'locales.json: {len(found)} problems')
    print('locales.json: matches the contract')
