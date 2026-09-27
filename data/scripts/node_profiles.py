"""Node-type profiles: typical inputs for each kind of node.

Derived from the site and company research in data/sources. Location-driven
inputs (grid, water stress, WUE, population) are not here — they come from
where the node is placed. Writes data/node-profiles.csv.
"""
from common import load, write_csv

S = {**load('sites-upstream.json')['sites'], **load('sites-downstream.json')['sites']}
FAB_W = load('water.json')['fab_water']
PAM = load('power-assembly-materials.json')['types']
PIL = load('power-inference-lab.json')['types']
WT = load('water-types.json')['types']

def site(s, key):
    r = S[s][key]
    return f"{s} {r['value']} ({r.get('year')}, {r.get('confidence')})", r.get('url') or ''

def points(block, val, label):
    out = []
    for p in block['points']:
        if p.get(val) is None: continue
        name = p.get('company') or p.get('name') or ''
        out.append((f"{name} {p.get('scope', '')} {p[val]} ({p.get('year')})".replace('  ', ' '), p.get('url') or ''))
    return out

rows = []
def row(stage, typ, param, default, low, high, unit, conf, basis, evidence=()):
    evs = [site(*e) if isinstance(e, tuple) and len(e) == 2 and e[0] in S else e for e in evidence]
    evs = [e if isinstance(e, tuple) else (e, '') for e in evs]
    rows.append([stage, typ, param, default, low, high, unit, conf, basis,
                 '; '.join(e[0] for e in evs), ' '.join(sorted({e[1] for e in evs if e[1]}))])

def water(stage, typ, key):
    t = WT[key]
    row(stage, typ, 'water', t['default_l_per_kwh'], t['low'], t['high'], 'L/kWh', 'estimated',
        'Median of company total water withdrawal / energy. ' + t.get('basis', ''), points(t, 'l_per_kwh', key))

CONV = 'Model convention: p is average draw from annual consumption, so utilisation and overhead are already inside it.'
IE_UPUE = 7663000 / (1543 * 8760)  # Ireland metered 2025 DC electricity / installed IT capacity

def conv(stage, typ):
    row(stage, typ, 'u', 1, '', '', '0-1', 'estimated', CONV)
    row(stage, typ, 'pue', 1, '', '', 'x', 'estimated', CONV)

# ---- raw: mine
row('raw', 'mine', 'p', 64, 18.4, 220, 'MW', 'estimated',
    'Geometric mean of the two sourced mines; a judgement across very different scales (lithium, grid-only vs. giant copper, self-generated).',
    [('green', 'p'), ('grasb', 'p')])
conv('raw', 'mine')
row('raw', 'mine', 'g', 0.073, -0.032, 0.26, '/yr', 'estimated', 'Median of four sourced growth figures (one is planned capacity).',
    [('green', 'g'), ('grasb', 'g'), ('bayan', 'g'), ('spruce', 'g')])
water('raw', 'mine', 'mine')

# ---- raw: materials, gases & wafers
m = PAM['materials_gases']
row('raw', 'materials & wafers', 'p', m['p_default_mw'], m['p_low'], m['p_high'], 'MW', 'estimated',
    'Silicon wafer plants only (company totals / plant count). Specialty-gas and quartz plants not found. ' + m.get('basis', ''),
    points(m, 'p_mw', 'materials'))
conv('raw', 'materials & wafers')
row('raw', 'materials & wafers', 'g', m['g_default'], '', '', '/yr', 'estimated', 'Median company electricity growth.', points(m, 'g', 'materials'))
water('raw', 'materials & wafers', 'materials_gases')

# ---- chip: front-end fab
row('chip', 'fab', 'p', 195, 173, 269, 'MW', 'estimated',
    'Mean of single-fab sites (Hiroshima 173, Chandler electricity-only ~216). Whole science-park clusters run 1,420-2,047 MW; company upper bounds: SK hynix 1,441, Samsung Korea 2,867.',
    [('hiro', 'p'), ('chand', 'p'), ('hsin', 'p'), ('tainan', 'p')])
conv('chip', 'fab')
row('chip', 'fab', 'g', 0.053, 0.023, 0.082, '/yr', 'estimated', 'Median of six fab growth figures (four are company-wide).',
    [('hsin', 'g'), ('tainan', 'g'), ('hiro', 'g'), ('chand', 'g'), ('ptaek', 'g'), ('icheon', 'g')])
row('chip', 'fab', 'water', FAB_W[0]['value'], 4.70, FAB_W[0]['value'], 'L/kWh', 'estimated',
    'TSMC total water intake / total electricity (2025; 2024 = 4.70). Withdrawal, not consumption.', [f"TSMC {FAB_W[0]['year']}"])

# ---- chip: packaging & test
row('chip', 'packaging & test', 'p', 146, '', '', 'MW', 'disclosed', 'One sourced site (ASE Kaohsiung).', [('kaoh', 'p')])
conv('chip', 'packaging & test')
row('chip', 'packaging & test', 'g', 0.024, '', '', '/yr', 'disclosed', 'ASE Kaohsiung.', [('kaoh', 'g')])
water('chip', 'packaging & test', 'packaging')

# ---- chip: equipment & optics
row('chip', 'equipment & optics', 'p', 40, '', 60.6, 'MW', 'estimated',
    'Upper bound: ASML EU renewable electricity 2025 (all EU sites incl. Veldhoven) = 40 MW; ASML group 60.6, ZEISS group 59.',
    [('veld', 'p'), ('ober', 'p')])
conv('chip', 'equipment & optics')
row('chip', 'equipment & optics', 'g', 0.079, 0.049, 0.109, '/yr', 'estimated', 'Mean of ASML and ZEISS company-wide growth.',
    [('veld', 'g'), ('ober', 'g')])
water('chip', 'equipment & optics', 'equipment')

# ---- infra: training data center
row('infra', 'data center (training)', 'p', 200, 200, 1200, 'MW', 'estimated',
    'Only sourced single campus: Abilene ~200 MW operational (Apr 2026), 1.2 GW planned by end-2026. IEA: AI-focused hyperscale sites are 100 MW+.',
    [('abil', 'p')])
row('infra', 'data center (training)', 'pue', 1.3, 1.08, 1.56, 'x', 'projected',
    'Crusoe design range 1.2-1.4 for Abilene; Google campuses 1.08-1.10; Uptime 2024 industry average 1.56.',
    [('abil', 'pue'), ('dalles', 'pue'), ('cbluff', 'pue')])
row('infra', 'data center (training)', 'u', round(IE_UPUE / 1.3, 3), '', '', '0-1', 'estimated',
    f'Ireland metered: 2025 data-center electricity / installed IT capacity = u x PUE = {IE_UPUE:.3f}; divided by this profile PUE. Vacancy-based occupancy (~0.95) overstates energy ~2.6x.',
    [('dubl', 'u'), ('dubl', 'p')])
row('infra', 'data center (training)', 'g', 0.10, 0.089, 0.42, '/yr', 'measured',
    'Ireland metered electricity growth. Market capacity growth elsewhere: median 0.23 (Ashburn .37, Frankfurt .23, Mumbai .42).',
    [('dubl', 'g'), ('ashb', 'g'), ('frank', 'g'), ('saopa', 'g'), ('mumb', 'g')])
row('infra', 'data center (training)', 'water', '', '', '', 'L/kWh', '', 'Use the location WUE (region, else country), applied to IT energy: W = E / PUE x WUE.')

# ---- infra: hardware assembly
a = PAM['assembly']
row('infra', 'hardware assembly', 'p', a['p_default_mw'], a['p_low'], a['p_high'], 'MW', 'estimated',
    'Median per-plant electricity of server/ODM makers (company totals / plant count, and Quanta per-plant). Megasites like Foxconn Zhengzhou or Quanta Shanghai (63 MW) sit well above. ' + a.get('basis', ''),
    points(a, 'p_mw', 'assembly'))
conv('infra', 'hardware assembly')
row('infra', 'hardware assembly', 'g', a['g_default'], -0.29, 0.92, '/yr', 'estimated',
    'Median company electricity growth; AI-server makers grow far faster (Wistron +21%, Wiwynn +92%).', points(a, 'g', 'assembly'))
water('infra', 'hardware assembly', 'assembly')

# ---- model: AI lab
l = PIL['ai_lab']
row('model', 'AI lab (offices)', 'p', l['p_default_mw'], l['p_low'], l['p_high'], 'MW', 'estimated',
    'Office floor area x US office energy benchmark (EIA CBECS 13.6 kWh/sq ft/yr); cross-checked with Alphabet office electricity per employee. Training compute is counted at data centers. ' + l.get('basis', ''),
    points(l, 'p_mw', 'lab'))
conv('model', 'AI lab (offices)')
row('model', 'AI lab (offices)', 'g', l['g_default'], '', 0.63, '/yr', 'estimated', 'Floor-area growth of OpenAI SF 2023-2026 (Anthropic implies 0.63). Startup rate; will not persist.')
row('model', 'AI lab (offices)', 'water', '', '', '', 'L/kWh', '', 'Not researched; office water is small next to data centers.')

# ---- delivery: inference data center
i = PIL['inference_dc']
row('delivery', 'data center (inference)', 'p', i['p_default_mw'], i['p_low'], i['p_high'], 'MW', 'estimated',
    'CoreWeave ~850 MW across 43 sites (~20 MW/site); IEA conventional data centre 10-25 MW; Digital Realty ~9.4 MW/facility. No inference-only site disclosed.',
    points(i, 'p_mw', 'inference'))
row('delivery', 'data center (inference)', 'pue', 1.56, 1.08, 1.56, 'x', 'estimated', 'Uptime Institute 2024 global average (colocation-heavy).',
    [('frank', 'pue')])
row('delivery', 'data center (inference)', 'u', round(IE_UPUE / 1.56, 3), '', '', '0-1', 'estimated',
    f'Ireland metered u x PUE = {IE_UPUE:.3f}, divided by PUE 1.56.', [('dubl', 'u')])
row('delivery', 'data center (inference)', 'g', i['g_default'], 0.10, 0.30, '/yr', 'projected',
    'IEA Base Case growth of accelerated-server electricity 2024-2030 (all data centers: 0.15; Ireland metered: 0.10).')
row('delivery', 'data center (inference)', 'water', '', '', '', 'L/kWh', '', 'Use the location WUE, applied to IT energy.')

# Location-driven, listed so nothing is forgotten.
row('all', 'all', 'pop', '', '', '', 'millions', 'estimated',
    'Location-driven, not a type property: sum data/population-grid-025.csv cells within 100 km of the node (GHSL 2025; within ~5% of 1 km sums at 12 of 14 test sites).')

write_csv('node-profiles.csv', ['stage', 'node_type', 'input', 'default', 'low', 'high', 'unit', 'confidence',
                                 'basis', 'evidence', 'source_urls'], rows)
