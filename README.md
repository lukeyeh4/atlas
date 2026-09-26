# AI Supply Chain Atlas

A map-first tool for exploring the AI supply chain — from quartz and specialty
gases through fabs, data centers and model training to inference at the edge —
with the environmental load of each node.

**Live:** https://YOUR-USERNAME.github.io/ai-supply-chain-atlas/
*(update this link once GitHub Pages is enabled)*

![Quiet Atlas](docs/screenshot.png)

---

## What it does

- **31 sites** at real coordinates across five stages: raw inputs, chip making,
  infrastructure, model building, delivery.
- **Real basemap** — Natural Earth 110m country geometry, embedded in the page.
  Natural Earth projection, pan and zoom.
- **A working model** of each site's yearly load:

  | | |
  |---|---|
  | Energy | `E = P_IT · 8760 · u · PUE`  (MWh/yr) |
  | Carbon | `C = E · CI`  (tCO₂e) |
  | Water | `W = E · WUE`  (m³) |
  | Air | `A = E · fossil share · downwind population`  (index, 0–100) |

- **Regional layers** — grid carbon intensity (yellow), water stress (blue),
  air quality (gray). One at a time.
- **Add and remove nodes.** Three placeholder cities sit on the map as dashed
  rings; pick a stage to turn one into a modeled node. Removing any node
  reverts it to a placeholder rather than deleting the location.
- **Compare** two sites for per-metric deltas.
- **Search** with `/` or `⌘K`.

## ⚠️ The numbers are sample data

Coordinates, place names and site descriptions are real. **Every model input —
power, utilization, PUE, grid carbon intensity, WUE, growth, downwind
population, air quality — is an illustrative placeholder, not a measured
figure.** The panel says so on every node. Magnitudes are plausible; nothing
here is sourced.

To bind real data, edit two things near the top of the `<script>` block in
`index.html`:

- `REGIONS` — grid carbon intensity, decarbonization rate, WUE, water stress,
  fossil share
- each site's `in: {p, u, pue, g, pop}`

Nothing else needs to change.

## Running it

It is a single self-contained HTML file. Open `index.html` in a browser, or:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

The only external dependency is d3 v7 from cdnjs and two Google Fonts. The
country geometry is inlined in the page, so it works offline apart from those.

## Files

| | |
|---|---|
| `index.html` | The whole app — markup, styles, data and model |
| `countries.json` | The source geometry, decoded from Natural Earth 110m TopoJSON. Kept for reference; `index.html` has its own inlined copy |
| `CHANGELOG.md` | Every version so far, with the reasoning |
| `ROADMAP.md` | Blocking questions and planned work |

## Credits

Country geometry from [Natural Earth](https://www.naturalearthdata.com/) via
[world-atlas](https://github.com/topojson/world-atlas), public domain.
Typefaces: Source Serif 4 and IBM Plex Mono.
