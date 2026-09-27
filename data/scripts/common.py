"""Shared paths and helpers for the data builders."""
import csv, json, os, re, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data'
SOURCES = DATA / 'sources'
CACHE = DATA / '.cache'


def download(url, name):
    """Fetch url into data/.cache/name once; return the local path."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / name
    if not path.exists():
        print(f'downloading {url}')
        req = urllib.request.Request(url, headers={'User-Agent': 'ai-supply-chain-atlas data builder'})
        with urllib.request.urlopen(req, timeout=600) as r, open(path.with_suffix('.part'), 'wb') as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
        path.with_suffix('.part').rename(path)
    return path


def load(name):
    return json.load(open(SOURCES / name, encoding='utf-8'))


def save(name, obj):
    json.dump(obj, open(SOURCES / name, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


def clean(x):
    return '' if x is None else ' '.join(str(x).split())


def write_csv(name, header, rows, footer=()):
    """Write data/<name> with whitespace-normalized cells; footer rows follow a blank line."""
    with open(DATA / name, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow([clean(x) for x in r])
        if footer:
            w.writerow([])
            for r in footer:
                w.writerow(r)
    print(f'wrote data/{name} ({len(rows)} rows)')


def app_names():
    """Region and site display names from index.html, keyed by id."""
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    names = {}
    for rid, n in re.findall(r"'([a-z-]+)':\s*\{n:'([^']+)'", html):
        names[rid] = n
    for sid, n, p in re.findall(r"\{id:'([a-z]+)',\s*n:'([^']+)',\s*p:'([^']+)',\s*s:", html):
        names[sid] = f'{n}, {p}'
    return names
