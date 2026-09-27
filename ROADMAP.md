# AI Supply Chain Atlas — Roadmap

Status as of 2026-09-27. Current build: v0.12.2, a single HTML file served
from GitHub Pages on a Mapbox globe. Location data comes from the database
side through `data/locales.json`, `data/node-types.json` and `data/cells/`
(contract: `docs/locale-contract.md`). Finished work is in `CHANGELOG.md`,
not here.

---

## Blocking questions

These change the design, not just the implementation. Answering them early
avoids rework.

1. **Who opens this?** A researcher tracing dependencies, a policy audience, or
   an engineer picking a region. The panel's default content changes with the
   answer.
2. **Marginal or average grid carbon intensity?** Average is what the model
   uses now and keeps the app as drawn. Marginal is the more honest number for
   "what does *adding* this load cause", but it needs hourly data and a
   different time control than a year scrubber.
3. **Are flows company-specific or aggregate?** Aggregate trade flows are
   obtainable. Per-company sourcing mostly is not, and the map gets much
   emptier if we insist on it.
4. **Does air pollution deserve its own view?** It is the one impact that
   depends on downwind population rather than facility location. A plume layer
   is a different kind of map from a choropleth.

---

## Next

### Places: make each location its own
Every site, built-in or added, now takes type inputs and location values
the same way (v0.9.0). What's left is finer location data and site scale.
- Cells carry people within 100 km (v0.7.0) and basin water stress
  (v0.9.1). Cooling water and PM2.5 stay at country level on purpose: the
  climate formula spans only 1.17–1.57 L/kWh, so gridding it adds false
  precision, and background PM2.5 matters less than emissions and exposure
  (see blocking question 4).
- [ ] **Grid-region level** (point-in-polygon on grid-region shapes) ahead of
      subdivision, so a point in Virginia resolves to PJM.
- [ ] Optionally the place's Wikipedia summary under its profile, reached
      through the Wikidata id Mapbox already returns.
- [ ] **Site scale** beyond data centers: data centers have a size slider
      (v0.10.0); every other type still shares one size (all fabs 195 MW),
      and built-in sites start at their type's typical size. Decide
      whether sites carry a sourced size or count of facilities, and where
      that lives (a per-site file would be a new contract section).

### Scenarios
- [ ] **Flesh out the presets.** Each one currently applies a single blunt
      rule (halve grid carbon, move campuses to Sweden, double power). Give
      each a stated basis, a horizon year, and sourced parameters.
- [ ] Fleet-wide totals (energy, carbon, water, air vs baseline); the panel
      only reports per site today.
- [ ] Scenarios that users define: pick sites, pick a target grid or scale.
- [ ] **Scenario compare**: two full states of the world side by side. "What
      if this workload ran in Region A vs B" at fleet scale, which is the
      question the original notes opened with.

### Location data (`data/locales.json`)
Ordered by how likely each is to work, surest first. Coverage checked
2026-09-27 against the live sources.
- [x] **Validate in the build.** Turn the contract checks into a step in
      `build_all.py`, so a rebuild can't produce a file the app rejects. No
      new data.
- [x] **Every country, not just 64.** A place in any other country gets no
      inputs and can't be modelled. The bulk sources already cover most of
      the world, keyed by ISO3: Ember CI, fossil share and trend for 213
      countries; World Bank PM2.5 (2023) for ~217; ERA5 climate (for WUE) for
      any country; Aqueduct water stress for 164. Mostly script work.
      Operator WUE disclosures stay hand-researched (29 countries).
- [x] **Water stress below country level.** Done per 0.25° cell from Aqueduct
      4.0 sub-basins (see below), which is finer than by province (Phoenix
      1.0, Ashburn 0.03, against the US's 0.52). Aqueduct also has
      2030/2050/2080 projections, for when time returns.
- [ ] **Grid gaps with data already in hand.** Tasmania's trend from its
      consumption-based series (229.7 → 124.4 g/kWh, 2015–2023). Tibet's CI
      from the Southwest regional grid figure (247.2 g/kWh, 2023) as a
      stand-in; its trend needs the 2021–2022 regional figures (unchecked).
      Both mix bases, so each needs a note. Under the all-three rule, each
      fix moves the place back onto its own grid.
- [ ] **Canadian provinces.** The national average hides hydro Quebec and
      fossil Alberta. Canada's National Inventory Report (Annex 13) publishes
      electricity intensity by province and year; Statistics Canada has
      generation by fuel. Researched by hand.
- [ ] **Grid gaps that need new research.** Northern Territory fossil share
      and trend; Chandigarh and Dadra & Nagar Haveli–Daman & Diu fossil share;
      Lakshadweep trend. Small places with thin sources.
- [ ] **Japanese regions.** Emission factors are published per utility, not
      per prefecture, so each prefecture maps to its utility area; a few
      straddle two.
- [ ] **US consumption-based intensity.** State values count in-state
      generation, so importers such as Virginia look cleaner than the power
      they use. EPA's eGRID is by grid subregion, not state: fixing it means
      weighting subregions per state, or keying US values by grid region,
      which the contract would need a new level for.

Per-point values (`data/cells/`, 0.25° tiles), so each city differs from its
neighbours, not just its state:
- [x] `pop` — people within 100 km, from the GHSL grid already built.
- [x] `ws` — Aqueduct 4.0 sub-basin water stress (baseline annual file).
- [ ] `wue` — not planned: the formula spans only 1.17–1.57 L/kWh, so a finer
      grid adds little.
- [ ] `pm25` — not planned for now: see Air pollution; background PM2.5 matters
      less than emissions and exposure.
- [x] `data/node-types.json` — facility-type defaults from `node-profiles.csv`.

### Air pollution
Most of the chain's air pollution is emitted at the power plants that supply
it, not at the facilities, so this starts with the grid, not with wind.
Relates to blocking question 4. In order:
- [ ] **Physical units.** Replace the air-quality index (normalized against
      the largest site, so it moves when nodes change) with a quantity:
      tonnes of SO₂ / NOₓ / PM2.5 per year, and population exposed.
- [ ] **Emissions from electricity, where it is generated.** Per-grid
      emissions per kWh (Ember, EPA eGRID for the US) times each node's
      energy, with exposure from the population around that grid's power
      plants rather than around the node.
- [ ] **On-site combustion flag** for facility types that burn fuel on site
      (self-generating mines, data centers on gas turbines, e.g. xAI Memphis).
      Only these get a local-exposure term.
- [ ] Wind — not planned. Wind-rose weighting would sharpen only the on-site
      term, by perhaps 1.5–2×, less than the uncertainty in emissions; real
      dispersion models (InMAP, EASIUR) exist for the US only. Revisit only
      if self-generating sites become a focus.

### Node editing
- [ ] Edit a node's inputs in the panel (utilization, PUE) beyond data
      center size, which has a slider (v0.10.0).
- [ ] Draw and edit flows for added nodes. Right now a new node has no chain.
- [ ] **Radial node menu.** Clicking a node opens a radial sub-menu around it
      with three actions: **Remove**, **Change type** (switch stage) and
      **Relocate** (move the node on the map).
- [ ] **Auto-populate connections.** When a node's type changes or a new node
      is added, create its upstream and downstream flows automatically from
      the stage order (raw → chip → infra → model → delivery), e.g. linking
      to the nearest nodes in the adjacent stages.
- [ ] Persist edits. Nothing survives a reload today. The database branch
      built this (`atlas.edits.v1` in localStorage, a small diff against the
      reference data) on the pre-globe d3 map; port it to the current app.
- [ ] Then export / import edits as a JSON file, to back them up or move them
      between browsers.

### Connections diagram
- [ ] Click a part to show its sites on the map (the count is already there).
- [ ] Per-site connections: the diagram is by part, not by site.

### Database
Prepared, not provisioned — see `docs/database.md`. No accounts, no login:
the database holds reference data only (public read, maintainer write);
visitors' edits stay in their browser.
- [x] Decided: no accounts.
- [ ] Decide between a Supabase database and a `data/baseline.json` file in the
      repo. The same schema shapes either; a database pays off once someone other
      than the maintainer edits values.
- [ ] If Supabase: create the project, run `db/schema.sql` and `db/seed.sql`,
      and load the `atlas_baseline` view at boot, keeping the inline data as an
      offline fallback.
- [ ] Move sourced values and their confidence into `site_input` /
      `region_input` rather than editing `index.html`.
- [ ] Optional: share a scenario as a link by encoding the edits in the URL
      hash. Still no accounts or server.

### Layers
- [ ] Click a country to see its exact values (grid carbon, water stress,
      air quality, etc.).
- [ ] **Land and cooling** is a placeholder: no data bound, paints neutral.
- [ ] Accessibility pass on the ramps: check each layer's endpoints for
      contrast in both themes, and don't rely on hue alone.
- [ ] State or province lines beyond the US, if a layer needs them.
- [ ] Optional thin major rivers between zoom 3 and 6, where streets water
      is hidden.
- [ ] Flat map is Mercator, so high latitudes are enlarged. Revisit an
      equal-area flat projection if Mapbox adds hillshade support for it.

### Map
- [x] **A more accurate map provider**: Mapbox GL globe with vector tiles
      and terrain since v0.4.0 (the Natural Earth 110m basemap is retired).

### Time
- [ ] The year scrubber was removed in v0.3.2, but the year math is still in
      `metrics()`. Decide whether time returns as a control, a
      small-multiple, or not at all. Scenario horizons may decide it.
- [ ] If it returns: projections need to be visually distinct from observed
      values everywhere, not just in the year readout.
- [ ] Decide whether layers should be comparable across years the way the
      carbon layer was before the scrubber came out.

---

## Later

- [ ] **Stage totals**: the removed bottom-bar totals were useful; they may
      belong in the panel or a summary view rather than the chrome.
- [ ] **Flow weight**: arcs could carry share of supply as stroke weight once
      `edge.share` has real values.
- [ ] **Concentration risk**: the notes flag Taiwan at 70–90% of some links.
      A view that surfaces single points of failure would use data already in
      the flow graph.
- [ ] **Mobile**: the panel works at phone width but has not been designed
      for it.
- [ ] **Export**: share a view, or hand off the computed table.
- [ ] **Move to a repo** if this outgrows a single file. Vite + React was the
      alternative considered; the component split was sketched as
      `components/map`, `components/panel`, `components/chrome`, `data/`,
      `model/`, `hooks/`.

---

## Known gaps in the current build

- All sites of one facility type share its typical size; see "Site scale".
- Without the data files (offline), sites fall back to the inline sample
  inputs and `REGIONS`.
- Added and searched points use `data/locales.json` (248 countries, 126
  subdivisions) and, where a tile exists, `data/cells/`; elsewhere they fall back to the curated `REGIONS` or a
  sample country average. Grid values fall back together, so a subdivision
  missing any of them uses the country's grid, and the panel lists the local
  values it passed over.
- A placed point is "New site n" until reverse geocoding answers, and stays
  so offline or away from any city.
- Air quality is an exposure **index**, not a physical unit, normalized
  against the largest baseline site. It and the metric bars move when nodes
  are added or removed, not when a scenario changes.
- Scenarios change the model only; the map layers keep showing the data.
- Added nodes have no upstream or downstream links.
- Dense clusters (Taiwan, Korea) overlap at world zoom; collision-aware
  placement is unimplemented.
- The compare view drops units: 4.77 (TWh) sits beside 391 (GWh) unlabeled.
- The Mapbox token is public in `index.html`; it must be URL-restricted in
  the Mapbox account.
- The README screenshot still shows the v0.3 flat map.
