"""Grid inputs for states, provinces and grids in the US, China, India and Australia.

Reads sources/grid-us-states.json (ember.py), grid-china-provinces.json and
grid-india-australia.json. Writes data/subnational-grid.csv.
"""
from common import iso_3166_2, load, write_csv

HEADER = ['country', 'subregion', 'code', 'iso_3166_2', 'ci_gco2_kwh', 'ci_year', 'ci_basis', 'fossil_share', 'fossil_year',
          'decarb_rate_per_yr', 'decarb_note', 'confidence_ci', 'source', 'url', 'note']
rows = []

us = load('grid-us-states.json')
for s, r in us['states'].items():
    rows.append(['United States of America', s, r['code'], r['ci']['value'], r['ci']['year'], us['basis'],
                 r['fos']['value'], r['fos']['year'], r['dec']['value'], r['dec']['note'], 'estimated',
                 us['source'], us['url'], ''])

for p, r in load('grid-china-provinces.json')['provinces'].items():
    ci, fos, dec = r.get('ci') or {}, r.get('fos') or {}, r.get('dec') or {}
    rows.append(['China', p, r.get('name_zh', ''), ci.get('value'), ci.get('year'), ci.get('basis', ''),
                 fos.get('value'), fos.get('year'), dec.get('value'), dec.get('note', ''), ci.get('confidence', ''),
                 ci.get('source') or fos.get('source', ''), ci.get('url') or fos.get('url', ''),
                 ' | '.join(x for x in [ci.get('note', ''), 'fossil share: ' + fos['note'] if fos.get('note') else ''] if x)])

ia = load('grid-india-australia.json')
for country, block, key in [('India', ia['india'], 'states'), ('Australia', ia['australia'], 'regions')]:
    for s, r in block[key].items():
        ci, fos, dec = r.get('ci') or {}, r.get('fos') or {}, r.get('dec') or {}
        rows.append([country, s, '', ci.get('value'), ci.get('year'), ci.get('basis', ''),
                     fos.get('value'), fos.get('year'), dec.get('value'), dec.get('note', ''), ci.get('confidence', ''),
                     ci.get('source', ''), ci.get('url', ''), ci.get('note', '')])

rows = [r[:3] + [iso_3166_2(*r[:3])] + r[3:] for r in rows]

write_csv('subnational-grid.csv', HEADER, rows, footer=[['CAVEATS']] + [['', c] for c in [
    'Bases differ by country: US and India = Ember lifecycle, generation-based; China = MEE direct CO2, consumption-based (includes imports); Australia = OpenElectricity direct, generation-based.',
    'Generation-based values mislead for importing regions: Tasmania shows 4 g but consumed electricity is ~124-200 g; India hydro states (~24 g) and small importers (Delhi, Goa, Chandigarh) draw on the ~620-710 g national grid.',
    'India coal states may be 15-25% low (Ember applies a generic coal factor; CEA measured all-India direct average is 710 g).',
    'China decarb rate uses only 2021-2023 and swings with hydro years and trade; indicative only. China fossil share is 2024 above-scale generation (excludes most rooftop solar, includes biomass) so it runs high. Tibet has no official factor.',
    'Pacific NW / hydro US states can show negative decarb rates from hydro-year noise.',
    'iso_3166_2: India uses the pre-2023 codes Mapbox returns (IN-TG, IN-CT, IN-OR, IN-UT; ISO now IN-TS, IN-CG, IN-OD, IN-UK). WA-SWIS is coded AU-WA though it covers only the Perth grid.',
]])
