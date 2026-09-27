"""Every country's location inputs, merged from the bulk sources and the
hand-researched overrides. Shared by country_inputs.py (CSV) and locales.py
(the app's JSON), so both apply the same rules.

Bulk, keyed by ISO2: country-grid.json (ember.py), country-wue.json
(country_wue.py), country-ws.json (water_stress.py), country-pm25.json
(pm25.py). Overrides, keyed by Natural Earth name: countries.json
`exceptions` and water-disclosed.json.
"""
from common import countries, load

CI_YEAR = 2024


def records():
    """One dict per country with at least one value, sorted by name.

    Each value is {'value', 'year', ...} or absent. Overrides carry
    'override': True plus their own source, url and confidence.
    """
    g, w = load('country-grid.json')['countries'], load('country-wue.json')['countries']
    ws, pm = load('country-ws.json')['countries'], load('country-pm25.json')['countries']
    ex_all, d = load('countries.json')['exceptions'], load('water-disclosed.json')
    names = dict(countries().values())

    out = []
    for iso2 in set(g) | set(w) | set(ws) | set(pm):
        name = names[iso2]
        ex, grid = ex_all.get(name, {}), g.get(iso2, {})
        r = {'iso2': iso2, 'name': name, 'ci': grid.get('ci'), 'fos': grid.get('fos'), 'dec': grid.get('dec'),
             'climate': w.get(iso2), 'ws': ws.get(iso2), 'pm25': pm.get(iso2),
             'disclosed': d['wue'].get(name), 'exceptions': ex}
        if r['ws'] is None and name in d['water_stress']:
            alt = d['water_stress'][name]
            r['ws'] = {'value': alt['value'], 'year': alt['year'], 'override': True, 'confidence': alt['confidence'],
                       'source': alt['source'], 'url': alt['url'], 'method': alt['method']}
        if 'aq' in ex:
            a = ex['aq']
            r['pm25'] = {'value': a['value'], 'year': a['year'], 'override': True, 'confidence': a['confidence'],
                         'source': a['source'], 'url': a['url']}
        out.append(r)
    return sorted(out, key=lambda r: r['name'])
