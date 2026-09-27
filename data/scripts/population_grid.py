"""Population on a 0.25° grid, for "people within 100 km" of any node.

Aggregates GHSL 2025 population (30 arc-second, ~1 km) and checks the coarse
grid against 1 km sums at the upstream sites. Downloads ~480 MB once.
Needs numpy, tifffile and imagecodecs (pip install numpy tifffile imagecodecs).

Writes data/population-grid-025.csv (lat, lon, population).
"""
import csv, json, math, zipfile
import numpy as np, tifffile
from common import DATA, CACHE, download, load

GHSL = ('https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_POP_GLOBE_R2023A/'
        'GHS_POP_E2025_GLOBE_R2023A_4326_30ss/V1-0/GHS_POP_E2025_GLOBE_R2023A_4326_30ss_V1_0.zip')
RES = 0.25
F = int(round(RES * 120))                      # fine cells per coarse cell
NX, NY = int(360 / RES), int(180 / RES)

# Upstream sites, for the check against 1 km sums in sources/ghsl-1km-site-sums.json.
SITES = {'spruce': (35.915, -82.065), 'bayan': (41.78, 109.97), 'yamag': (33.95, 131.25), 'green': (-33.86, 116.06),
         'grasb': (-4.05, 137.11), 'hsin': (24.78, 121.01), 'tainan': (23.11, 120.27), 'ptaek': (37.02, 127.05),
         'icheon': (37.21, 127.48), 'veld': (51.405, 5.415), 'ober': (48.785, 10.10), 'kaoh': (22.72, 120.30),
         'hiro': (34.44, 132.75), 'chand': (33.27, -111.88)}


def aggregate():
    zpath = download(GHSL, 'ghsl-pop-2025-30ss.zip')
    with zipfile.ZipFile(zpath) as z:
        name = next(n for n in z.namelist() if n.endswith('.tif'))
        tif = CACHE / name
        if not tif.exists():
            z.extract(name, CACHE)
    grid = np.zeros((NY, NX))
    with tifffile.TiffFile(tif) as t:
        page = t.pages[0]
        tags = page.geotiff_tags
        x0, y0 = tags['ModelTiepoint'][3], tags['ModelTiepoint'][4]
        dx = tags['ModelPixelScale'][0]
        r_off, c_off = int(round((90 - y0) / dx)), int(round((x0 + 180) / dx))
        for data, idx, shape in page.segments():
            if data is None:
                continue
            seg = np.asarray(data).reshape(shape[-3], shape[-2]).astype(np.float64)
            seg[seg < 0] = 0
            r0, c0 = idx[-3] + r_off, idx[-2] + c_off
            rows = (np.arange(r0, r0 + seg.shape[0]) // F).clip(0, NY - 1)
            cols = (np.arange(c0, c0 + seg.shape[1]) // F).clip(0, NX - 1)
            np.add.at(grid, (rows[:, None], cols[None, :]), seg)
    return grid


def pop_within(grid, lat, lon, R=100.0):
    """People within R km of (lat, lon), in millions — the sum the app will do."""
    dlat = R / 111.32 + RES
    dlon = R / (111.32 * max(math.cos(math.radians(lat)), 0.01)) + RES
    r0 = max(int((90 - (lat + dlat)) / RES), 0)
    r1 = min(int((90 - (lat - dlat)) / RES) + 1, NY)
    cs = [c % NX for c in range(int((lon - dlon + 180) / RES), int((lon + dlon + 180) / RES) + 1)]
    sub = grid[r0:r1][:, cs]
    LA, LO = np.meshgrid(90 - (np.arange(r0, r1) + 0.5) * RES,
                         np.array([-180 + (c + 0.5) * RES for c in cs]), indexing='ij')
    p1, p2 = math.radians(lat), np.radians(LA)
    a = np.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * np.cos(p2) * np.sin(np.radians(LO - lon) / 2) ** 2
    return float(sub[2 * 6371.0 * np.arcsin(np.sqrt(a)) <= R].sum()) / 1e6


if __name__ == '__main__':
    grid = aggregate()
    print('world population in grid: %.3f bn' % (grid.sum() / 1e9))
    ref = load('ghsl-1km-site-sums.json')
    for k, (la, lo) in SITES.items():
        v = pop_within(grid, la, lo)
        print(f'  {k:7} 0.25° {v:7.3f}M   1 km {ref[k]:7.3f}M   ratio {v / ref[k]:.3f}')
    with open(DATA / 'population-grid-025.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['lat', 'lon', 'population'])
        n = 0
        for r, c in zip(*np.nonzero(grid >= 1)):
            w.writerow([90 - (r + 0.5) * RES, -180 + (c + 0.5) * RES, int(round(grid[r, c]))])
            n += 1
    print(f'wrote data/population-grid-025.csv ({n} cells)')
