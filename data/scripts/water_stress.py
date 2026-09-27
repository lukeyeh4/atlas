"""Baseline water stress per country, and per state/province for the
subdivisions in locales.json, from WRI Aqueduct 4.0's rankings.

Score 0-5 (bws, all-sector weighting 'Tot') divided by 5. Countries Aqueduct
reports as NoData (-9999) are left out; Taiwan and Singapore are filled by
hand in water-disclosed.json. Provinces are matched by name; Aqueduct's
borders predate India's 2019-2020 changes, so Ladakh and Dadra and Nagar
Haveli and Daman and Diu get no value.

Writes data/sources/country-ws.json (keyed by ISO2) and
data/sources/subdivision-ws.json (keyed by ISO 3166-2).
"""
import re, zipfile
import xml.etree.ElementTree as ET
from common import SUBDIVISION, countries as country_codes, download, load, save

URL = 'https://files.wri.org/aqueduct/aqueduct-4-0-country-rankings.zip'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
# Aqueduct (GADM) province name -> ours, where they differ.
ALIAS = {'District of Columbia': 'Washington, D.C.', 'Nei Mongol': 'Inner Mongolia', 'Ningxia Hui': 'Ningxia',
         'Xinjiang Uygur': 'Xinjiang', 'Xizang': 'Tibet', 'NCT of Delhi': 'Delhi'}
AU = {'New South Wales': 'NSW', 'Queensland': 'QLD', 'Victoria': 'VIC', 'South Australia': 'SA', 'Tasmania': 'TAS',
      'Western Australia': 'WA', 'Northern Territory': 'NT', 'Australian Capital Territory': 'ACT'}


def province_codes():
    """{(ISO3, our province name): ISO 3166-2} for the subdivisions locales.json has."""
    out = {('USA', s): f"US-{r['code']}" for s, r in load('grid-us-states.json')['states'].items()}
    out.update({('CHN', n): f'CN-{c}' for n, c in SUBDIVISION['China'].items()})
    out.update({('IND', n): f'IN-{c}' for n, c in SUBDIVISION['India'].items()})
    out.update({('AUS', n): f'AU-{c}' for n, c in AU.items()})
    return out


def sheet(path, name):
    """Rows of one sheet in the rankings workbook, as dicts by header."""
    outer = zipfile.ZipFile(path)
    book = zipfile.ZipFile(outer.open(next(n for n in outer.namelist() if n.endswith('.xlsx'))))
    shared = [''.join(t.itertext()) for t in ET.fromstring(book.read('xl/sharedStrings.xml')).findall('m:si', NS)]
    names = [s.get('name') for s in ET.fromstring(book.read('xl/workbook.xml')).find('m:sheets', NS)]
    root = ET.fromstring(book.read(f'xl/worksheets/sheet{names.index(name) + 1}.xml'))
    head = None
    for r in root.iter(f'{{{NS["m"]}}}row'):
        cells = {}
        for c in r.findall('m:c', NS):
            v = c.find('m:v', NS)
            if v is not None:
                cells[re.match(r'[A-Z]+', c.get('r')).group()] = shared[int(v.text)] if c.get('t') == 's' else v.text
        if head is None:
            head = cells
        else:
            yield {head[k]: v for k, v in cells.items() if k in head}


if __name__ == '__main__':
    codes = country_codes()
    path = download(URL, 'aqueduct-4-0-country-rankings.zip')
    out = {}
    for r in sheet(path, 'country_baseline'):
        if r.get('indicator_name') != 'bws' or r.get('weight') != 'Tot' or r.get('gid_0') not in codes:
            continue
        score = float(r['score'])
        if score < 0:
            continue
        out[codes[r['gid_0']][0]] = {'value': round(score / 5, 3), 'score': round(score, 3), 'label': r.get('label', '')}
    save('country-ws.json', {
        'source': 'WRI Aqueduct 4.0 Country Rankings, baseline water stress (bws), all-sector weighting (Tot); score 0-5 divided by 5',
        'url': URL, 'year': 2023, 'confidence': 'estimated',
        'countries': dict(sorted(out.items()))})
    print(f'country-ws.json: {len(out)} countries')

    prov, subs = province_codes(), {}
    for r in sheet(path, 'province_baseline'):
        if r.get('indicator_name') != 'bws' or r.get('weight') != 'Tot':
            continue
        code = prov.get((r.get('gid_0'), ALIAS.get(r.get('name_1'), r.get('name_1'))))
        if code and float(r['score']) >= 0:
            subs[code] = {'value': round(float(r['score']) / 5, 3), 'label': r.get('label', '')}
    save('subdivision-ws.json', {
        'source': 'WRI Aqueduct 4.0 Province Rankings, baseline water stress (bws), all-sector weighting (Tot); score 0-5 divided by 5',
        'url': URL, 'year': 2023, 'confidence': 'estimated', 'subdivisions': dict(sorted(subs.items()))})
    print(f'subdivision-ws.json: {len(subs)} of {len(prov)} subdivisions')
