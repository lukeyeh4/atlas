"""One row per country with every location input the model needs.

Reads the merged records from country_data.py. Writes data/country-inputs.csv.
"""
from common import load, write_csv
from country_data import records

g, w = load('country-grid.json'), load('country-wue.json')
ws_src, pm_src = load('country-ws.json'), load('country-pm25.json')

HEADER = ['country', 'iso2', 'ci_gco2_kwh', 'ci_year', 'fossil_share', 'fossil_year', 'decarb_rate_per_yr', 'decarb_note',
          'water_stress_0_1', 'water_stress_note', 'wue_best_l_kwh', 'wue_best_basis',
          'wue_disclosed_l_kwh', 'wue_disclosed_scope', 'wue_disclosed_operator', 'wue_disclosed_year', 'wue_disclosed_url',
          'wue_climate_l_kwh', 'wetbulb_c', 'wue_climate_note', 'pm25_ugm3', 'exceptions']


def get(x, k='value'):
    return (x or {}).get(k)


rows = []
for r in records():
    ws, ww, dw = r['ws'] or {}, r['climate'] or {}, r['disclosed'] or {}
    ws_note = f"Not in Aqueduct 4.0; {ws['confidence']}: {ws['method']}" if ws.get('override') else ''

    # A disclosed WUE beats the climate formula, except a stated zero (AWS
    # reporting no cooling water in an air-cooled region), which says nothing
    # about the local market.
    dv = dw.get('value')
    if dv is not None and dv > 0:
        best, basis = dv, f"disclosed ({dw.get('scope')})"
    elif ww:
        best, basis = ww.get('wue'), 'climate formula' + (' (operator stated zero cooling water)' if dv == 0 else '')
    else:
        best, basis = None, ''

    rows.append([r['name'], r['iso2'], get(r['ci']), get(r['ci'], 'year'), get(r['fos']), get(r['fos'], 'year'),
                 get(r['dec']), get(r['dec'], 'note'), ws.get('value'), ws_note, best, basis,
                 dv, dw.get('scope', ''), dw.get('operator', ''), dw.get('year', ''), dw.get('url', ''),
                 ww.get('wue'), ww.get('wetbulb_c'), ww.get('note', ''), get(r['pm25']),
                 ' | '.join(f"{m}: {e.get('source', '')} ({e.get('year', '')})" for m, e in r['exceptions'].items())])

write_csv('country-inputs.csv', HEADER, rows, footer=[
    ['SOURCES', 'column', 'source', 'url', 'year', 'confidence'],
    ['', 'ci_gco2_kwh, fossil_share, decarb_rate_per_yr', g['source'] + '; latest year up to 2024; decarb = compound annual decline of CI from 2015, derived by us', g['url'], 2024, 'estimated (CI is modelled: generation x lifecycle factors) / measured (fossil share)'],
    ['', 'water_stress_0_1', ws_src['source'] + '. Taiwan and Singapore from national data (see water_stress_note).', ws_src['url'], ws_src['year'], ws_src['confidence']],
    ['', 'wue_disclosed_l_kwh', 'Operator disclosures: AWS 2026 regional fact sheets (2025 data), Microsoft region fact sheets (some are design values for unbuilt regions), Meta 2025 data index, Teraco, IMDA Singapore. Check wue_disclosed_scope.', '', '2021-2025', 'disclosed'],
    ['', 'wue_climate_l_kwh', 'Cooling-tower WUE from annual-mean wet-bulb: ' + w['formula']['expression'] + ' — ' + w['formula']['citation']
     + '. Wet-bulb: ' + w['wetbulb_source']['source'] + '. WEAK: spans only ~1.17-1.57.', w['formula']['url'], w['wetbulb_source'].get('year_range', ''), 'estimated'],
    ['', 'wue_best_l_kwh', 'Disclosed value when present and above zero, else climate formula.', '', '', ''],
    ['', 'pm25_ugm3', pm_src['source'] + '. Taiwan from its environment ministry (see exceptions).', pm_src['url'], 2023, pm_src['confidence']],
])
