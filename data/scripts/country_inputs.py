"""One row per country with every location input the model needs.

Reads sources/countries.json, country-grid.json (ember.py), country-wue.json
(country_wue.py) and water-disclosed.json. Writes data/country-inputs.csv.
"""
from common import load, write_csv

c, g, w, d = load('countries.json'), load('country-grid.json'), load('country-wue.json'), load('water-disclosed.json')
src = c['sources']

HEADER = ['country', 'ci_gco2_kwh', 'ci_year', 'fossil_share', 'fossil_year', 'decarb_rate_per_yr', 'decarb_note',
          'water_stress_0_1', 'water_stress_note', 'wue_best_l_kwh', 'wue_best_basis',
          'wue_disclosed_l_kwh', 'wue_disclosed_scope', 'wue_disclosed_operator', 'wue_disclosed_year', 'wue_disclosed_url',
          'wue_climate_l_kwh', 'wetbulb_c', 'wue_climate_note', 'pm25_ugm3', 'exceptions']

rows = []
for name, (ci, ws, aq) in c['countries'].items():
    ex = c['exceptions'].get(name, {})
    gw, ww, dw = g['countries'][name], w['countries'][name], d['wue'].get(name) or {}

    ws_note = ''
    if ws is None and name in d['water_stress']:
        alt = d['water_stress'][name]
        ws, ws_note = alt['value'], f"Not in Aqueduct 4.0; {alt['confidence']}: {alt['method']}"

    # A disclosed WUE beats the climate formula, except a stated zero (AWS
    # reporting no cooling water in an air-cooled region), which says nothing
    # about the local market.
    dv = dw.get('value')
    if dv is not None and dv > 0:
        best, basis = dv, f"disclosed ({dw.get('scope')})"
    else:
        best, basis = ww.get('wue'), 'climate formula' + (' (operator stated zero cooling water)' if dv == 0 else '')

    rows.append([name, ci, ex.get('ci', {}).get('year', src['ci']['year']), gw['fos']['value'], gw['fos']['year'],
                 gw['dec']['value'], gw['dec']['note'], ws, ws_note, best, basis,
                 dv, dw.get('scope', ''), dw.get('operator', ''), dw.get('year', ''), dw.get('url', ''),
                 ww.get('wue'), ww.get('wetbulb_c'), ww.get('note', ''), aq,
                 ' | '.join(f"{m}: {e.get('source', '')} ({e.get('year', '')})" for m, e in ex.items())])

write_csv('country-inputs.csv', HEADER, rows, footer=[
    ['SOURCES', 'column', 'source', 'url', 'year', 'confidence'],
    ['', 'ci_gco2_kwh', src['ci']['source'], src['ci']['url'], src['ci']['year'], src['ci']['confidence']],
    ['', 'fossil_share, decarb_rate_per_yr', g['source'] + '; decarb = compound annual decline of CI 2015-2024, derived by us', g['url'], 2024, 'measured / estimated'],
    ['', 'water_stress_0_1', src['ws']['source'] + '. Taiwan and Singapore from national data (see water_stress_note).', src['ws']['url'], src['ws']['year'], src['ws']['confidence']],
    ['', 'wue_disclosed_l_kwh', 'Operator disclosures: AWS 2026 regional fact sheets (2025 data), Microsoft region fact sheets (some are design values for unbuilt regions), Meta 2025 data index, Teraco, IMDA Singapore. Check wue_disclosed_scope.', '', '2021-2025', 'disclosed'],
    ['', 'wue_climate_l_kwh', 'Cooling-tower WUE from annual-mean wet-bulb: ' + w['formula']['expression'] + ' — ' + w['formula']['citation']
     + '. Wet-bulb: ' + w['wetbulb_source']['source'] + '. WEAK: spans only ~1.17-1.57.', w['formula']['url'], w['wetbulb_source'].get('year_range', ''), 'estimated'],
    ['', 'wue_best_l_kwh', 'Disclosed value when present and above zero, else climate formula.', '', '', ''],
    ['', 'pm25_ugm3', src['aq']['source'], src['aq']['url'], src['aq']['year'], src['aq']['confidence']],
])
