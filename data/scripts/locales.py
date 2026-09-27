"""Location inputs keyed by ISO code, for the app: data/locales.json.

The file is the interface to the app; its shape is fixed by
docs/locale-contract.md. Countries come from country_data.py (shared with
country_inputs.py); subdivisions from the same sources as subnational_grid.py.
Each value keeps its own confidence and source.
Unknown values are left out, never written as null or zero.
"""
import datetime, json

from common import DATA, iso_3166_2, load
from country_data import CI_YEAR, records

g, w = load('country-grid.json'), load('country-wue.json')
ws_src, pm_src = load('country-ws.json'), load('country-pm25.json')
us, cn, ia = load('grid-us-states.json'), load('grid-china-provinces.json'), load('grid-india-australia.json')

SOURCES = {
    'ember': {'title': g['source'], 'url': g['url']},
    'aqueduct': {'title': 'WRI Aqueduct 4.0 country rankings, baseline water stress', 'url': ws_src['url']},
    'wdi-pm25': {'title': pm_src['source'], 'url': pm_src['url']},
    'wue-climate': {'title': 'Cooling-tower WUE at annual-mean wet-bulb (Shumba et al. 2025; Sen Gupta et al. 2024) on ERA5 climate',
                    'url': w['formula']['url'].split(' ; ')[0]},
    'ember-us': {'title': us['source'], 'url': us['url']},
    'ember-india': {'title': ia['india']['sources']['ember_india_yearly']['name'],
                    'url': ia['india']['sources']['ember_india_yearly']['page']},
    'mee': {'title': 'MEE & NBS provincial electricity CO2 emission factors (2021-2023 editions)',
            'url': cn['sources']['mee_2023']['url']},
    'nbs-generation': {'title': 'NBS 2024 above-scale generation by province (via BJX compilation)',
                       'url': cn['sources']['nbs_2024_generation']['url']},
    'openelectricity': {'title': ia['australia']['sources']['openelectricity_v3']['name'],
                        'url': 'https://data.opennem.org.au/v3/stats/au/NEM/NSW1/energy/all.json'},
    'nga-2025': {'title': ia['australia']['sources']['nga_2025']['name'], 'url': ia['australia']['sources']['nga_2025']['url']},
}
used = set()


def val(v, conf, src, year=None, basis=None, note=None):
    """One contract value, or None when v is unknown."""
    if v is None or conf is None:
        return None
    assert src in SOURCES, src
    used.add(src)
    out = {'v': v, 'conf': conf, 'src': src}
    for k, x in (('year', year), ('basis', basis), ('note', note)):
        if x not in (None, ''):
            out[k] = x
    return out


def entry(name, **values):
    return {'n': name, **{k: x for k, x in values.items() if x is not None}}


def slug(s):
    return ''.join(ch if ch.isalnum() else '-' for ch in s.lower()).strip('-')


# ------------------------------------------------------------ countries ----

WS_NOTE = {
    'Taiwan': 'national water use over runoff, scored on the Aqueduct curve.',
    'Singapore': "WRI's 2015 score for 2040; natural freshwater only, ignores NEWater and desalination.",
}
countries = {}
for r in records():
    name, iso = r['name'], r['iso2']
    ci, fos, dec, ws, ww, dw, pm = (r[k] or {} for k in ('ci', 'fos', 'dec', 'ws', 'climate', 'disclosed', 'pm25'))

    # Ember's CO2 intensity is generation times lifecycle factors: modelled,
    # so estimated, as for US and Indian states.
    ci_v = val(ci.get('value'), 'estimated', 'ember', ci.get('year'), 'lifecycle',
               'Latest year Ember publishes for this country.' if ci.get('year', CI_YEAR) < CI_YEAR else None)

    if ws.get('override'):
        key = f'ws-{iso.lower()}'
        SOURCES[key] = {'title': ws['source'].split(':')[0], 'url': ws['url']}
        ws_v = val(ws['value'], ws['confidence'], key, ws['year'], note='Not in Aqueduct 4.0; ' + WS_NOTE[name])
    else:
        ws_v = val(ws.get('value'), ws_src['confidence'], 'aqueduct', ws_src['year'])

    # `wue` is the climate estimate: a property of the place. An operator's
    # disclosure describes its own fleet or region, not a new site there, so
    # it goes in `wue_disclosed` (including stated zeros). Design values for
    # regions not yet running are projections.
    wue_v = None
    if ww:
        note = f"Cooling-tower estimate at annual-mean wet-bulb {ww['wetbulb_c']} °C"
        if ww.get('clamped'):
            note += '; clamped at the formula floor, so free cooling is not reflected'
        wue_v = val(ww.get('wue'), 'estimated', 'wue-climate', basis='direct', note=note)

    wue_d = None
    dv = dw.get('value')
    if dv is not None:
        key = f'wue-{slug(dw["operator"])}-{iso.lower()}'
        SOURCES[key] = {'title': f"{dw['operator']}, {dw['region_code']} ({dw['scope']})", 'url': dw['url']}
        unbuilt = 'not yet in operation' in (dw.get('source', '') + dw.get('note', '')).lower()
        where = dw['region_code'] if dw['scope'] == 'design' else dw['scope']
        wue_d = val(dv, 'projected' if unbuilt else 'disclosed', key, dw.get('year'), 'direct',
                    f"{dw['operator']} {where}" + ('; design value, not yet in operation' if unbuilt
                                                   else '; no cooling water used' if dv == 0 else ''))

    if pm.get('override'):
        key = f'pm25-{iso.lower()}'
        SOURCES[key] = {'title': pm['source'].split(',')[0], 'url': pm['url']}
        pm_v = val(pm['value'], pm['confidence'], key, pm['year'],
                   note='Station average; not comparable to the modelled values used elsewhere.')
    else:
        pm_v = val(pm.get('value'), pm_src['confidence'], 'wdi-pm25', pm.get('year'))

    countries[iso] = entry(
        name, ci=ci_v,
        fos=val(fos.get('value'), 'measured', 'ember', fos.get('year'), 'generation'),
        dec=val(dec.get('value'), 'estimated', 'ember', note=dec.get('note')),
        ws=ws_v, wue=wue_v, wue_disclosed=wue_d, pm25=pm_v)

# --------------------------------------------------------- subdivisions ----

subdivisions = {}

for s, r in us['states'].items():
    subdivisions[iso_3166_2('United States of America', s, r['code'])] = entry(
        s,
        ci=val(r['ci']['value'], 'estimated', 'ember-us', r['ci']['year'], 'generation',
               'Lifecycle, in-state generation; excludes imports.'),
        fos=val(r['fos']['value'], 'measured', 'ember-us', r['fos']['year'], 'generation'),
        dec=val(r['dec']['value'], 'estimated', 'ember-us', note=r['dec']['note']))

for p, r in cn['provinces'].items():
    ci, fos, dec = r.get('ci') or {}, r.get('fos') or {}, r.get('dec') or {}
    subdivisions[iso_3166_2('China', p)] = entry(
        'Tibet (Xizang)' if p == 'Tibet' else p,
        ci=val(ci.get('value'), ci.get('confidence'), 'mee', ci.get('year'), 'consumption',
               'Direct CO2, includes imported power.'),
        fos=val(fos.get('value'), fos.get('confidence'), 'nbs-generation', fos.get('year'), 'generation',
                'Above-scale plants only; overstates fossil where rooftop solar is large.'),
        dec=val(dec.get('value'), dec.get('confidence'), 'mee', note='2021–2023 only; swings with hydro years.'))

for s, r in ia['india']['states'].items():
    ci, fos, dec = r.get('ci') or {}, r.get('fos') or {}, r.get('dec') or {}
    subdivisions[iso_3166_2('India', s)] = entry(
        s,
        ci=val(ci.get('value'), ci.get('confidence'), 'ember-india', ci.get('year'), 'generation',
               'Lifecycle, in-state generation; the state draws on the national grid.'),
        fos=val(fos.get('value'), fos.get('confidence'), 'ember-india', fos.get('year'), 'generation'),
        dec=val(dec.get('value'), dec.get('confidence'), 'ember-india', note='CAGR 2019–2024, derived.'))

AU_SRC = {'NT': 'nga-2025'}
AU_NOTE = {
    'WA-SWIS': 'South West Interconnected System (Perth); north-west WA is not covered.',
    'NT': 'Darwin–Katherine system only.',
    'TAS': 'Generation-based; consumed power is ~124–200 g with imports.',
}
for s, r in ia['australia']['regions'].items():
    ci, fos, dec = r.get('ci') or {}, r.get('fos') or {}, r.get('dec') or {}
    src = AU_SRC.get(s, 'openelectricity')
    subdivisions[iso_3166_2('Australia', s)] = entry(
        {'NSW': 'New South Wales', 'QLD': 'Queensland', 'VIC': 'Victoria', 'SA': 'South Australia',
         'TAS': 'Tasmania', 'WA-SWIS': 'Western Australia', 'NT': 'Northern Territory'}[s],
        ci=val(ci.get('value'), ci.get('confidence'), src, ci.get('year'),
               'consumption' if s == 'NT' else 'generation', AU_NOTE.get(s)),
        fos=val(fos.get('value'), fos.get('confidence'), src, fos.get('year'), 'generation'),
        dec=val(dec.get('value'), dec.get('confidence'), src))

# ACT sits inside the NEM's NSW region and has no grid figures of its own.
subdivisions['AU-ACT'] = {'n': 'Australian Capital Territory', **{
    k: {**x, 'note': 'NEM NSW region values (ACT is part of it).'}
    for k, x in subdivisions['AU-NSW'].items() if k != 'n'}}

# ---------------------------------------------------------------- write ----

assert all(len(k) == 2 for k in countries), 'bad country code'
assert all('-' in k for k in subdivisions), 'bad subdivision code'
out = {
    'v': 1,
    'built': datetime.date.today().isoformat(),
    'countries': dict(sorted(countries.items())),
    'subdivisions': dict(sorted(subdivisions.items())),
    'sources': {k: SOURCES[k] for k in sorted(used)},
}
with open(DATA / 'locales.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    f.write('\n')
print(f'wrote data/locales.json ({len(countries)} countries, {len(subdivisions)} subdivisions, {len(used)} sources)')
