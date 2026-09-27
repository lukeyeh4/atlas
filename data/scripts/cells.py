"""Location values on a 0.25° grid, in 10° tiles: data/cells/.

Shape fixed by docs/locale-contract.md ("Location cells"). Each layer is a
0.25° array (NaN = unknown); a cell is written when any layer knows it.

  pop  people within 100 km of the cell centre, millions. Sums
       population-grid-025.csv (population_grid.py) over every cell whose
       centre is within 100 km, the same rule as population_grid.pop_within().
       Cells with fewer than 500 people within 100 km are left out.

Writes data/cells/{S}_{W}.json and data/cells/index.json. Needs numpy.
"""
import csv, json, math, shutil
import numpy as np
from common import CELL_META as META, DATA

RES, TILE, R_KM, EARTH_KM = 0.25, 10, 100.0, 6371.0
NX, NY = int(360 / RES), int(180 / RES)
OUT = DATA / 'cells'


def population():
    """Population per 0.25° cell; row 0 is the northernmost band."""
    g = np.zeros((NY, NX))
    for r in csv.DictReader(open(DATA / 'population-grid-025.csv')):
        g[int((90 - float(r['lat'])) / RES), int((float(r['lon']) + 180) / RES)] = float(r['population'])
    return g


def within(grid, km=R_KM):
    """Sum of grid over cells whose centre is within km of each cell centre."""
    lat = 90 - (np.arange(NY) + 0.5) * RES
    h = math.sin(km / EARTH_KM / 2) ** 2
    reach = int(math.ceil(km / (math.pi * EARTH_KM / 180) / RES)) + 1
    cum = np.concatenate([np.zeros((NY, 1)), np.cumsum(np.concatenate([grid, grid], axis=1), axis=1)], axis=1)
    out = np.zeros_like(grid)
    for r in range(NY):
        p1 = math.radians(lat[r])
        for r2 in range(max(r - reach, 0), min(r + reach + 1, NY)):
            p2 = math.radians(lat[r2])
            room = h - math.sin((p2 - p1) / 2) ** 2
            if room < 0:
                continue
            cc = math.cos(p1) * math.cos(p2)
            s = room / cc if cc > 1e-12 else 2.0
            k = NX // 2 if s >= 1 else int(math.degrees(2 * math.asin(math.sqrt(s))) / RES + 1e-9)
            if 2 * k + 1 >= NX:
                out[r] += grid[r2].sum()
                continue
            # Circular window [c - k, c + k] on the doubled row.
            start = (np.arange(NX) - k) % NX
            out[r] += cum[r2, start + 2 * k + 1] - cum[r2, start]
    return out


def layers():
    pop = within(population()) / 1e6
    pop[pop < 0.0005] = np.nan
    return {'pop': np.round(pop, 3)}


def write(lay):
    keys = list(lay)
    stack = np.stack([lay[k] for k in keys])
    known = ~np.all(np.isnan(stack), axis=0)
    tiles = {}
    for r, c in zip(*np.nonzero(known)):
        la, lo = 90 - (r + 0.5) * RES, -180 + (c + 0.5) * RES
        tid = f'{math.floor(la / TILE) * TILE}_{math.floor(lo / TILE) * TILE}'
        vals = [None if math.isnan(v) else float(v) for v in stack[:, r, c]]
        tiles.setdefault(tid, {})[f'{la:.3f},{lo:.3f}'] = vals
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for tid, cells in tiles.items():
        doc = {'v': 1, 'tile': tid, 'res': RES, 'keys': keys, 'meta': {k: META[k] for k in keys},
               'cells': dict(sorted(cells.items()))}
        (OUT / f'{tid}.json').write_text(json.dumps(doc, separators=(',', ':')) + '\n')
    (OUT / 'index.json').write_text(json.dumps({'v': 1, 'res': RES, 'tiles': sorted(tiles)}, separators=(',', ':')) + '\n')
    size = sum(p.stat().st_size for p in OUT.iterdir())
    print(f'wrote data/cells/ ({len(tiles)} tiles, {int(known.sum())} cells, {size / 1e6:.1f} MB, keys {keys})')


if __name__ == '__main__':
    write(layers())
