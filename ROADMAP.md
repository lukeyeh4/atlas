# AI Supply Chain Atlas — Roadmap

Status as of 2026-09-27. Current build: v0.12.1, a single HTML file served
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

### Node editing
- [ ] Edit a node's inputs in the panel (utilization, PUE) beyond data
      center size, which has a slider (v0.10.0).
- [ ] Draw and edit flows for added nodes. Right now a new node has no chain.
- [ ] Persist edits. Nothing survives a reload today. The database branch
      built this (`atlas.edits.v1` in localStorage, with export/import) on
      the pre-globe d3 map; port it to the current app.

### Connections diagram
- [ ] Click a part to show its sites on the map (the count is already there).
- [ ] Per-site connections: the diagram is by part, not by site.

### Layers
- [ ] Click a country to see its exact values (grid carbon, water stress,
      air quality, etc.).
- [ ] **Land and cooling** is a placeholder: no data bound, paints neutral.
- [ ] Accessibility pass on the ramps: check each layer's endpoints for
      contrast in both themes, and don't rely on hue alone.
- [ ] Border hierarchy: US state lines now read stronger than country
      borders over the fills. Country borders should match or outweigh them.
- [ ] State or province lines beyond the US, if a layer needs them.
- [ ] Optional thin major rivers between zoom 3 and 6, where streets water
      is hidden.
- [ ] Flat map is Mercator, so high latitudes are enlarged. Revisit an
      equal-area flat projection if Mapbox adds hillshade support for it.

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
