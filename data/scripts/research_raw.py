"""Every value from the first research round, one row per value.

Reads sources/grid.json, water.json, sites-upstream.json, sites-downstream.json
and countries.json. Writes data/research-raw.csv.
"""
import json
from common import load, write_csv, clean, app_names

names = app_names()
rows = []


def add(dataset, etype, eid, metric, v, extra=''):
    rows.append([dataset, etype, eid, names.get(eid, eid), metric, v.get('value'), v.get('unit', ''),
                 v.get('year'), v.get('confidence', ''), v.get('scope') or v.get('basis') or '', v.get('source', ''),
                 v.get('url', ''), ' | '.join(x for x in [clean(v.get('raw')), clean(v.get('note')), extra] if x)])


for f, ds, et, key in [('grid.json', 'grid', 'region', 'regions'), ('water.json', 'water', 'region', 'regions'),
                       ('sites-upstream.json', 'sites-upstream', 'site', 'sites'),
                       ('sites-downstream.json', 'sites-downstream', 'site', 'sites')]:
    for eid, rec in load(f)[key].items():
        for m, v in rec.items():
            if isinstance(v, dict):
                add(ds, et, eid, m, v)

c = load('countries.json')
for name, vals in c['countries'].items():
    for i, m in enumerate(['ci', 'ws', 'aq']):
        v = dict(c['sources'][m])
        v['value'] = vals[i]
        ex = c['exceptions'].get(name, {}).get(m)
        if ex:
            v.update(ex)
            v.setdefault('note', 'exception to dataset source')
        add('countries', 'country', name, m, v)

for fw in load('water.json')['fab_water']:
    add('fab-water', 'company', fw['id'], 'water_per_kwh', fw, clean(json.dumps(fw.get('inputs', ''))))

write_csv('research-raw.csv', ['dataset', 'entity_type', 'entity_id', 'entity_name', 'metric', 'value', 'unit', 'year',
                               'confidence', 'scope_or_basis', 'source', 'url', 'note'], rows)
