# AI Supply Chain Atlas

A map-first tool for exploring the AI supply chain — from quartz and specialty
gases through fabs, data centers and model training to inference at the edge —
with the environmental load of each node.

**Live:** https://lukeyeh4.github.io/atlas/
*(live once GitHub Pages finishes its first build)*

![Quiet Atlas](docs/screenshot.png)

---

## What it does

- **31 sites** at real coordinates across five stages: raw inputs, chip making,
  infrastructure, model building, delivery.
- **Mapbox globe** — dark, muted basemap with faint terrain relief. A 3D globe
  at world zoom that flattens to a web map as you zoom in; real coastlines,
  borders and labels at every scale. US state lines fade in as you zoom
  toward a region.
- **A working model** of each site's yearly load:

  | | |
  |---|---|
  | Energy | `E = P_IT · 8760 · u · PUE`  (MWh/yr) |
  | Carbon | `C = E · CI`  (tCO₂e) |
  | Water | `W = E · WUE`  (m³) |
  | Air | `A = E · fossil share · downwind population`  (index, 0–100) |

- **Regional layers** — grid carbon intensity (yellow), water stress (blue),
  air quality (gray). One at a time, painted onto Mapbox country boundaries
  under a faint hillshade, so flat ground keeps the legend colour and relief
  only nudges it.
- **Add and remove nodes.** Three placeholder cities sit on the map as dashed
  rings; pick a stage to turn one into a modeled node. Right-click any land to
  drop a new placeholder there. Removing any node reverts it to a placeholder
  rather than deleting the location.
- **Context menu** — right-click (or long-press) a site, a placeholder, land
  or water for the actions that fit: open, compare with the selected site, go
  upstream, zoom, copy coordinates, add or remove. `Shift+F10` opens it for
  the selected site.
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

It is a single HTML file. Serve the folder and open it:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

External dependencies: Mapbox GL JS v3 (basemap, terrain, country and state
boundaries), d3 v7 from cdnjs, and two Google Fonts. It needs a network
connection. The v0.3 claude.ai artifact can't load Mapbox (its sandbox blocks
external tile servers), so the globe only runs from Pages or a local server.

The Mapbox public token is set near the top of the map section in
`index.html`. Restrict it to the Pages URL (and `localhost` for development)
in the Mapbox account's token settings.

## Files

| | |
|---|---|
| `index.html` | The whole app — markup, styles, data and model |
| `countries.json` | Natural Earth 110m geometry used by v0.3. No longer loaded since the Mapbox basemap; kept for reference |
| `CHANGELOG.md` | Every version so far, with the reasoning |
| `ROADMAP.md` | Blocking questions and planned work |

## Credits

Basemap, terrain and country boundaries © [Mapbox](https://www.mapbox.com/about/maps/)
© [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors.
Typefaces: Source Serif 4 and IBM Plex Mono.
