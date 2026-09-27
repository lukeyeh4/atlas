# AI Supply Chain Atlas

A map-first tool for exploring the AI supply chain — from quartz and specialty
gases through fabs, data centers and model training to inference at the edge —
with the environmental load of each node.

**Live:** https://lukeyeh4.github.io/atlas/

![Quiet Atlas](docs/screenshot.png)

---

## What it does

- **32 sites** at real coordinates across five stages: raw materials, chip making,
  infrastructure, model building, delivery. Each has a facility type (fab,
  mine, training data center, AI lab, …) and takes its inputs from that type
  and its location values from its coordinates.
- **Mapbox globe** with faint terrain relief, flattening to a web map as you
  zoom in; a switch flips between globe and flat.
- **A working model** of each site's yearly load:

  | | |
  |---|---|
  | Energy | `E = P · 8760 · u · PUE`  (MWh/yr) |
  | Carbon | `C = E · CI`  (tCO₂e) |
  | Water | `W = E · process water rate`, or for data centers `P · 8760 · u · WUE`  (m³) |
  | Air | `A = E · fossil share · people within 100 km`  (index, 0–100) |

- **Sourced location data**, looked up most specific first: a 0.25° cell
  (people within 100 km, river-basin water stress) → state or province
  (grid carbon, fossil share, trend, water stress) → country. The panel lists
  every value with where it came from, its confidence and a link to its
  source.
- **Any city.** Search finds real cities (Mapbox geocoding) as well as the
  built-in sites; right-click any land to drop a point, named from reverse
  geocoding. Add a node there by stage and facility type; data center size
  is adjustable.
- **Map layers**, each explained in plain words:
  - **Places**: power emissions (grid carbon), water scarcity, and air
    pollution (PM2.5), painted by country and by state for the US.
    Hovering names the place.
  - **Each site**: power used, water used, and air pollution produced,
    drawn as circles sized by each site's modelled value.
- **Globe arcs** show a selected site's supply chain, coloured by what they
  carry (physical goods, or designs, data and models), with small markers
  travelling in the direction of transfer.
- **Connections**: the whole system as a diagram. Stages are columns, with
  five kinds of link and chokepoints marked. Click a step or a link for a
  plain-language explanation, what moves, and the step's sites on the map
  with their yearly totals.
- **Scenarios**: fast grid decarbonisation, training moves to the Nordics,
  data center boom. Moved sites take their new names. Any edit makes the
  scenario **Custom**; choosing Baseline clears every edit. **Compare
  locations** shows the same node at eleven reference places.
- **Stats**: totals for everything on the map against baseline and the
  world, a live counter since the page opened, and breakdowns by stage,
  site, country and scenario.
- **Key**: a menu to show or hide stages and kinds of connection.
- **Search** cities with `/` or `⌘K`; zoom and re-center buttons;
  right-click (or long-press) for context actions.

## The data

Location values, facility types and population cells are built from public
sources (Ember, WRI Aqueduct, GHSL, World Bank, operator disclosures and
others) by the scripts in `data/scripts/`; `data/README.md` explains each
file, its sources and its known limits. The app reads three generated files,
whose shape is fixed by [`docs/locale-contract.md`](docs/locale-contract.md):

| File | What |
|---|---|
| `data/locales.json` | Grid, water and air values for 248 countries and 126 states/provinces |
| `data/node-types.json` | Typical inputs for nine facility types |
| `data/cells/` | People within 100 km and basin water stress on a 0.25° grid, in 10° tiles |

Where a value is missing the app falls back to the next level, and offline
it falls back to the inline sample values in `index.html`. Scenario
parameters and some node inputs are still illustrative; the panel marks
each value's confidence.

## Running it

A single HTML file plus its data files. Serve the folder and open it:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

External dependencies: Mapbox GL JS v3 (basemap, terrain, boundaries,
geocoding), d3 v7 and topojson-client (cdnjs / jsDelivr), US state shapes
from us-atlas, and three Google Fonts. It needs a network connection.

The Mapbox public token is set near the top of the map section in
`index.html`. Restrict it to the Pages URL (and `localhost` for development)
in the Mapbox account's token settings.

To rebuild the data: `python3 data/scripts/build_all.py` (see
`data/README.md`).

## Files

| | |
|---|---|
| `index.html` | The whole app — markup, styles, model, map and diagram |
| `data/` | Generated data the app reads, the sources it's built from, and the build scripts |
| `docs/locale-contract.md` | The agreed shape of the data files: the interface between data and app |
| `docs/database.md` | The database plan (Postgres, read-only to the public) |
| `db/schema.sql` | Postgres schema for that database, keyed by ISO code |
| `db/seed-from-index.mjs` | Generates `db/seed.sql` from `index.html` and `data/locales.json` |
| `countries.json` | Natural Earth 110m geometry from v0.3; no longer loaded, kept for reference |
| `CHANGELOG.md` | Every version, with the reasoning |
| `ROADMAP.md` | Blocking questions and planned work |

## Credits

Basemap, terrain, boundaries and geocoding © [Mapbox](https://www.mapbox.com/about/maps/)
© [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors.
US state shapes: [us-atlas](https://github.com/topojson/us-atlas) (US Census
Bureau). Data sources are credited per value in the app and in
`data/README.md`. Typefaces: IBM Plex Sans, IBM Plex Mono and Source Serif 4.
