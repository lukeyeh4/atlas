"""Annual mean PM2.5 exposure per country from the World Bank (WDI).

Population-weighted mean annual exposure (GBD / IHME, satellite + model), the
latest year each country has. Regional aggregates are dropped.

Writes data/sources/country-pm25.json, keyed by ISO2.
"""
import json
from common import countries as country_codes, download, save

API = 'https://api.worldbank.org/v2/country/all/indicator/EN.ATM.PM25.MC.M3?format=json&per_page=20000&date=2010:2030'

if __name__ == '__main__':
    codes = country_codes()
    _, rows = json.load(open(download(API, 'wdi-pm25.json'), encoding='utf-8'))
    out = {}
    for r in rows:
        c, v = r['countryiso3code'], r['value']
        if c not in codes or v is None:
            continue
        iso2, y = codes[c][0], int(r['date'])
        if y > out.get(iso2, {}).get('year', 0):
            out[iso2] = {'value': round(v, 1), 'year': y}
    save('country-pm25.json', {
        'source': 'World Bank WDI EN.ATM.PM25.MC.M3 (population-weighted mean annual PM2.5 exposure; underlying data GBD 2023 / IHME, satellite+model derived)',
        'url': 'https://data.worldbank.org/indicator/EN.ATM.PM25.MC.M3', 'confidence': 'estimated',
        'countries': dict(sorted(out.items()))})
    print(f'country-pm25.json: {len(out)} countries')
