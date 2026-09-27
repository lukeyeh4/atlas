"""Grid fossil share and decarbonisation rate from Ember's bulk yearly data.

Writes data/sources/country-grid.json (every country Ember covers, keyed by
ISO2) and data/sources/grid-us-states.json (50 states + DC).
"""
import collections, csv
from common import countries as country_codes, download, save

EMBER_URL = 'https://ember-energy.org/data/yearly-electricity-data/'
EMBER_CSV = 'https://storage.googleapis.com/emb-prod-bkt-publicdata/public-downloads/yearly_full_release_long_format.csv'
US_URL = 'https://ember-energy.org/data/us-electricity-data/'
US_CSV = 'https://storage.googleapis.com/emb-prod-bkt-publicdata/public-downloads/us_yearly_full_release_long_format.csv'
Y0, Y1 = 2015, 2024

def decline(c0, c1, years):
    """Compound annual rate of decline; negative when intensity rose."""
    return 1 - (c1 / c0) ** (1 / years)


def read(path, area_col, area_type):
    ci, fs, code = collections.defaultdict(dict), collections.defaultdict(dict), {}
    for x in csv.DictReader(open(path, encoding='utf-8')):
        if x[area_type[0]] != area_type[1] or not x['Value']:
            continue
        a, y = x[area_col], int(x['Year'])
        code[a] = x.get('State code') or x.get('ISO 3 code', '')
        if x['Variable'] == 'CO2 intensity':
            ci[a][y] = float(x['Value'])
        elif x['Variable'] == 'Fossil' and x['Unit'] == '%' and x['Category'] == 'Electricity generation':
            fs[a][y] = float(x['Value'])
    return ci, fs, code


def countries():
    ci, fs, iso3 = read(download(EMBER_CSV, 'ember-yearly.csv'), 'Area', ('Area type', 'Country or economy'))
    codes = country_codes()
    out = {}
    for a in sorted(fs, key=lambda a: codes[iso3[a]][0]):
        iso2, name = codes[iso3[a]]
        c, f = ci.get(a, {}), fs[a]
        r = {'name': name}
        fy = max((y for y in f if y <= Y1), default=None)
        if fy:
            r['fos'] = {'value': round(f[fy] / 100, 4), 'year': fy, 'note': f'Fossil share of generation {f[fy]}% ({fy}).'}
        y1 = max((y for y in c if Y0 < y <= Y1), default=None)    # Ukraine stops at 2022
        if y1:
            r['ci'] = {'value': c[y1], 'year': y1}
            if c.get(Y0):
                r['dec'] = {'value': round(decline(c[Y0], c[y1], y1 - Y0), 4), 'year': y1,
                            'note': f'CI {Y0} {c[Y0]} -> {y1} {c[y1]} gCO2/kWh; compound annual decline over {y1 - Y0} yrs, derived by us.'}
        out[iso2] = r
    save('country-grid.json', {'source': 'Ember Yearly Electricity Data (bulk long-format CSV)', 'url': EMBER_URL, 'countries': out})
    print(f'country-grid.json: {len(out)} countries')


def us_states():
    ci, fs, code = read(download(US_CSV, 'ember-us-yearly.csv'), 'State', ('State type', 'state'))
    out = {}
    for s in sorted(ci):
        c, f = ci[s], fs[s]
        if Y0 not in c or Y1 not in c:
            continue
        out[s] = {'code': code[s],
                  'ci': {'value': c[Y1], 'year': Y1},
                  'fos': {'value': round(f[Y1] / 100, 4), 'year': Y1},
                  'dec': {'value': round(decline(c[Y0], c[Y1], Y1 - Y0), 4) if c[Y0] > 0 else None,
                          'note': f'CI {Y0} {c[Y0]} -> {Y1} {c[Y1]} gCO2/kWh; compound annual decline, derived by us.'}}
    save('grid-us-states.json', {'source': 'Ember US Electricity Data (state-level yearly, long format)', 'url': US_URL,
                                 'basis': 'lifecycle; generation-based (in-state generation, excludes imports)', 'states': out})
    print(f'grid-us-states.json: {len(out)} states')


if __name__ == '__main__':
    countries()
    us_states()
