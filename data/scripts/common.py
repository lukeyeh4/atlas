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


# ISO 3166-1 alpha-2 by Natural Earth name, for every country in countries.json.
ISO2 = {
    'United States of America': 'US', 'Canada': 'CA', 'Mexico': 'MX', 'Brazil': 'BR', 'Argentina': 'AR',
    'Chile': 'CL', 'Colombia': 'CO', 'Peru': 'PE', 'Venezuela': 'VE', 'United Kingdom': 'GB', 'Ireland': 'IE',
    'France': 'FR', 'Germany': 'DE', 'Netherlands': 'NL', 'Belgium': 'BE', 'Spain': 'ES', 'Portugal': 'PT',
    'Italy': 'IT', 'Switzerland': 'CH', 'Austria': 'AT', 'Poland': 'PL', 'Czechia': 'CZ', 'Sweden': 'SE',
    'Norway': 'NO', 'Finland': 'FI', 'Denmark': 'DK', 'Iceland': 'IS', 'Greece': 'GR', 'Romania': 'RO',
    'Ukraine': 'UA', 'Russia': 'RU', 'Turkey': 'TR', 'Kazakhstan': 'KZ', 'China': 'CN', 'India': 'IN',
    'Japan': 'JP', 'South Korea': 'KR', 'Taiwan': 'TW', 'Mongolia': 'MN', 'Vietnam': 'VN', 'Thailand': 'TH',
    'Malaysia': 'MY', 'Indonesia': 'ID', 'Philippines': 'PH', 'Singapore': 'SG', 'Bangladesh': 'BD',
    'Pakistan': 'PK', 'Saudi Arabia': 'SA', 'United Arab Emirates': 'AE', 'Iran': 'IR', 'Iraq': 'IQ',
    'Israel': 'IL', 'Egypt': 'EG', 'Morocco': 'MA', 'Algeria': 'DZ', 'Nigeria': 'NG', 'South Africa': 'ZA',
    'Kenya': 'KE', 'Ethiopia': 'ET', 'Ghana': 'GH', 'Tanzania': 'TZ', 'Angola': 'AO', 'Australia': 'AU',
    'New Zealand': 'NZ',
}

GEONAMES_URL = 'https://download.geonames.org/export/dump/countryInfo.txt'
NAME_FIXES = {'PS': 'Palestine'}


def countries():
    """{ISO3: (ISO2, display name)} for every country GeoNames lists.

    The bulk sources key by ISO3; the app keys by ISO2. Names are Natural
    Earth's for the countries in ISO2 above, GeoNames' common names otherwise.
    """
    ne = {v: k for k, v in ISO2.items()}
    out = {}
    for line in open(download(GEONAMES_URL, 'geonames-countries.txt'), encoding='utf-8'):
        if line.startswith('#'):
            continue
        f = line.rstrip('\n').split('\t')
        if f[0] in ('AN', 'CS'):                 # dissolved: Netherlands Antilles, Serbia and Montenegro
            continue
        out[f[1]] =(f[0], ne.get(f[0]) or NAME_FIXES.get(f[0]) or f[4].strip())
    return out

# ISO 3166-2 suffixes by the names the grid sources use. US states use their
# postal code, which ISO matches (incl. US-DC).
# India uses the pre-2023 codes (TG, CT, OR, UT), which is what Mapbox returns.
# ISO recoded these on 2023-11-23 to TS, CG, OD, UK.
SUBDIVISION = {
    'China': {
        'Beijing': 'BJ', 'Tianjin': 'TJ', 'Hebei': 'HE', 'Shanxi': 'SX', 'Inner Mongolia': 'NM', 'Liaoning': 'LN',
        'Jilin': 'JL', 'Heilongjiang': 'HL', 'Shanghai': 'SH', 'Jiangsu': 'JS', 'Zhejiang': 'ZJ', 'Anhui': 'AH',
        'Fujian': 'FJ', 'Jiangxi': 'JX', 'Shandong': 'SD', 'Henan': 'HA', 'Hubei': 'HB', 'Hunan': 'HN',
        'Guangdong': 'GD', 'Guangxi': 'GX', 'Hainan': 'HI', 'Chongqing': 'CQ', 'Sichuan': 'SC', 'Guizhou': 'GZ',
        'Yunnan': 'YN', 'Tibet': 'XZ', 'Shaanxi': 'SN', 'Gansu': 'GS', 'Qinghai': 'QH', 'Ningxia': 'NX',
        'Xinjiang': 'XJ',
    },
    'India': {
        'Andaman and Nicobar': 'AN', 'Andhra Pradesh': 'AP', 'Arunachal Pradesh': 'AR', 'Assam': 'AS', 'Bihar': 'BR',
        'Chandigarh': 'CH', 'Chhattisgarh': 'CT', 'Dadra and Nagar Haveli and Daman and Diu': 'DH', 'Delhi': 'DL',
        'Goa': 'GA', 'Gujarat': 'GJ', 'Haryana': 'HR', 'Himachal Pradesh': 'HP', 'Jammu and Kashmir': 'JK',
        'Jharkhand': 'JH', 'Karnataka': 'KA', 'Kerala': 'KL', 'Ladakh': 'LA', 'Lakshadweep': 'LD',
        'Madhya Pradesh': 'MP', 'Maharashtra': 'MH', 'Manipur': 'MN', 'Meghalaya': 'ML', 'Mizoram': 'MZ',
        'Nagaland': 'NL', 'Odisha': 'OR', 'Puducherry': 'PY', 'Punjab': 'PB', 'Rajasthan': 'RJ', 'Sikkim': 'SK',
        'Tamil Nadu': 'TN', 'Telangana': 'TG', 'Tripura': 'TR', 'Uttar Pradesh': 'UP', 'Uttarakhand': 'UT',
        'West Bengal': 'WB',
    },
    # WA-SWIS is the Perth grid; it stands in for all of WA (see locales.py).
    'Australia': {'NSW': 'NSW', 'QLD': 'QLD', 'VIC': 'VIC', 'SA': 'SA', 'TAS': 'TAS', 'WA-SWIS': 'WA', 'NT': 'NT'},
}


def iso_3166_2(country, name, code=''):
    """Full ISO 3166-2 code for a grid-source subregion, or '' if unknown."""
    if country == 'United States of America':
        return f'US-{code}'
    suffix = SUBDIVISION.get(country, {}).get(name)
    return f'{ISO2[country]}-{suffix}' if suffix else ''


# Per-layer metadata for data/cells/ tiles (cells.py), and the sources they
# cite, which locales.py lists in locales.json `sources`.
CELL_SOURCES = {
    'ghsl-2025': {'title': 'GHSL GHS-POP R2023A, 2025 epoch, 30 arc-second (JRC), summed within 100 km on a 0.25° grid',
                  'url': 'https://human-settlement.emergency.copernicus.eu/ghs_pop2023.php'},
    'aqueduct-basin': {'title': 'WRI Aqueduct 4.0 baseline annual water stress by sub-basin (bws), score 0-5 divided by 5, '
                                'sampled at 0.25° cell centres',
                       'url': 'https://www.wri.org/data/aqueduct-global-maps-40-data'},
}
CELL_META = {
    'pop': {'conf': 'estimated', 'src': 'ghsl-2025', 'year': 2025,
            'note': 'People within 100 km of the cell centre; GHSL 2025 is modelled from census data.'},
    'ws': {'conf': 'estimated', 'src': 'aqueduct-basin', 'year': 2023,
           'note': "Water stress of the cell's river sub-basin (1979-2019 hydrology); arid, low-use basins score 1. "
                   'Upstream inflow counts as local supply, so river-fed dry cities (Las Vegas) can read low.'},
}
# What a cell missing from the tiles means, per key (index.json `absent`).
# Only pop: cells are left out below a threshold. Other keys stay unknown.
CELL_ABSENT = {
    'pop': {'v': 0, 'conf': 'estimated', 'src': 'ghsl-2025', 'note': 'Fewer than 500 people within 100 km'},
}
