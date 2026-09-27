"""Baseline water stress per country from WRI Aqueduct 4.0.

Score 0-5 (bws, all-sector weighting 'Tot') divided by 5. Countries Aqueduct
reports as NoData (-9999) are left out; Taiwan and Singapore are filled by
hand in water-disclosed.json.

Writes data/sources/country-ws.json, keyed by ISO2.
"""
import re, zipfile
import xml.etree.ElementTree as ET
from common import countries as country_codes, download, save

URL = 'https://files.wri.org/aqueduct/aqueduct-4-0-country-rankings.zip'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


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
    out = {}
    for r in sheet(download(URL, 'aqueduct-4-0-country-rankings.zip'), 'country_baseline'):
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
