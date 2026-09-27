"""Baseline water stress on a 0.25° grid, from WRI Aqueduct 4.0 sub-basins.

Samples the Aqueduct 4.0 baseline annual layer (sub-basins split at
province borders) at each cell centre; where the centre misses every
polygon (coastal cells), at four points inside the cell, first hit wins.
Value = bws score 0-5 divided by 5, the same scale as the country ws.
'Arid and low water use' basins carry Aqueduct's score of 5 (1.0); 'No Data'
basins are left out, and so are countries whose country ws is hand-researched
because Aqueduct misleads there (water-disclosed.json: Taiwan, Singapore), so
those cells fall back to the country value. Downloads ~260 MB once.
Needs shapely and pyogrio (pip install shapely pyogrio).

Writes data/water-stress-grid-025.csv (lat, lon, ws).
"""
import csv, zipfile
import numpy as np
import shapely
from pyogrio.raw import read
from common import CACHE, DATA, countries, download, load

URL = 'https://files.wri.org/aqueduct/aqueduct-4-0-water-risk-data.zip'
GDB = 'Aqueduct40_waterrisk_download_Y2023M07D05/GDB/Aq40_Y2023D07M05.gdb'
RES = 0.25
NX, NY = int(360 / RES), int(180 / RES)
EXCLUDED = -1.0          # inside a hand-researched country: a hit, but no value


def basins():
    folder = CACHE / 'aqueduct40'
    if not (folder / GDB).exists():
        with zipfile.ZipFile(download(URL, 'aqueduct-4-0-water-risk-data.zip')) as z:
            z.extractall(folder, [n for n in z.namelist() if n.startswith(GDB)])
    meta, _, geom, fields = read(folder / GDB, layer='baseline_annual', columns=['bws_score', 'gid_0'])
    f = dict(zip(meta['fields'], fields))
    keep = f['bws_score'] >= 0                          # -9999 = No Data
    iso3 = {name: c3 for c3, (_, name) in countries().items()}
    hand = {iso3[n] for n in load('water-disclosed.json')['water_stress']}
    values = np.where(np.isin(f['gid_0'], list(hand)), EXCLUDED, f['bws_score'] / 5)
    return shapely.from_wkb(geom[keep]), values[keep]


def sample(tree, values, lat, lon):
    """Value of the polygon containing each point, NaN where none does."""
    out = np.full(lat.shape, np.nan)
    pt, poly = tree.query(shapely.points(lon, lat), predicate='intersects')
    first, at = np.unique(pt, return_index=True)        # a point on a shared edge takes one side
    out[first] = values[poly[at]]
    return out


if __name__ == '__main__':
    polys, values = basins()
    tree = shapely.STRtree(polys)
    rows, cols = np.meshgrid(np.arange(NY), np.arange(NX), indexing='ij')
    lat, lon = 90 - (rows.ravel() + 0.5) * RES, -180 + (cols.ravel() + 0.5) * RES
    ws = sample(tree, values, lat, lon)
    for dy, dx in ((0.0625, 0.0625), (0.0625, -0.0625), (-0.0625, 0.0625), (-0.0625, -0.0625)):
        miss = np.isnan(ws)
        ws[miss] = sample(tree, values, lat[miss] + dy, lon[miss] + dx)
    ws[ws == EXCLUDED] = np.nan
    known = ~np.isnan(ws)
    with open(DATA / 'water-stress-grid-025.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['lat', 'lon', 'ws'])
        for la, lo, v in zip(lat[known], lon[known], ws[known]):
            w.writerow([la, lo, round(float(v), 3)])
    print(f'wrote data/water-stress-grid-025.csv ({int(known.sum())} cells)')
