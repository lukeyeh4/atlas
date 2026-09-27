# AI Supply Chain Atlas — Roadmap

Status as of 2026-09-26. Current build: v0.4.0, a single-file app on GitHub
Pages. Ordered roughly by what unblocks the most.

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
5. **Browser or sandbox?** If people can move a workload between regions and
   watch numbers change, this needs an editable scenario model, not just a
   viewer. The add/remove node work in v0.3.2 is the first step toward that.

---

## Next

### Real data
- [ ] Replace sample inputs with sourced figures. Two objects to fill:
      `REGIONS` (grid CI, decarbonization rate, WUE, water stress, fossil
      share) and each site's `in: {p, u, pue, g, pop}`. Nothing else changes.
- [ ] Add a `confidence` field per value — measured / disclosed / estimated /
      projected — and render it as a visible mark, not a tooltip. Most of this
      data will be estimated and hiding that would mislead.
- [ ] Cite per-value sources in the panel.
- [ ] Country records currently carry `[grid CI, water stress, air quality]`.
      Air quality is a sample index; bind real PM2.5 or AQI data.

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
- [ ] **Water stress by state and province.** Aqueduct 4.0's province sheet,
      in the same download, scores ~2,980 provinces (Arizona 0.88 against the
      US's 0.52). Needs a crosswalk from GADM province ids to ISO 3166-2: by
      name for the US, China, India and Australia, a published crosswalk for
      the rest. The same file has 2030/2050/2080 projections, for when time
      returns.
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

### Node editing
- [ ] Edit a node's inputs in the panel (power, utilization, PUE), not just
      add and remove it. The model already recomputes on every render.
- [ ] Let an added node be placed anywhere, not only on the three seeded
      placeholder cities — click-to-place on the map.
- [ ] Draw and edit flows for added nodes. Right now a new node has no chain.
- [ ] **Radial node menu.** Clicking a node opens a radial sub-menu around it
      with three actions: **Remove**, **Change type** (switch stage) and
      **Relocate** (move the node on the map).
- [ ] **Auto-populate connections.** When a node's type changes or a new node
      is added, create its upstream and downstream flows automatically from
      the stage order (raw → chip → infra → model → delivery), e.g. linking
      to the nearest nodes in the adjacent stages.
- [x] Persist edits across reloads (browser storage, v0.4.0).
- [ ] Export / import edits as a JSON file, to back them up or move them
      between browsers. Edits are already stored as a small diff, so the file
      format is ready.

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
- [ ] **Land and cooling** is a placeholder — no data bound, paints neutral.
- [ ] Decide whether layers should be comparable across years the way the
      carbon layer was before the scrubber came out.
- [ ] Accessibility pass on the ramps: check each layer's endpoints for
      contrast in both themes, and don't rely on hue alone.

### Map
- [ ] **Find a more accurate map provider.** The basemap is Natural Earth
      110m, too coarse for site-level work: Singapore has no polygon, and
      dense clusters (Taiwan, Korea) sit on generalized coastlines. Options to
      weigh: higher-resolution Natural Earth (50m/10m) at the cost of page
      size, or a tiled provider (MapLibre GL with OpenStreetMap-based vector
      tiles, Mapbox, Protomaps) now that the app is no longer bound by the
      artifact CSP. Keep the Natural Earth projection look and theme support
      in mind.

### Time
- [ ] The year scrubber was removed from the bottom bar in v0.3.2, but all the
      year math is still in `metrics()` and `ciFor()`. Decide whether time
      returns as a control, a small-multiple, or not at all.
- [ ] If it returns: projections need to be visually distinct from observed
      values everywhere, not just in the year readout.

---

## Later

- [ ] **Scenario compare** — two full states of the world side by side, not
      just two sites. "What if this workload ran in Region A vs B" at fleet
      scale, which is the question the original notes opened with.
- [ ] **Stage totals** — the removed bottom-bar totals were useful; they may
      belong in the panel or a dedicated summary view rather than the chrome.
- [ ] **Flow weight** — arcs could carry share of supply as stroke weight once
      `edge.share` has real values.
- [ ] **Concentration risk** — the notes flag Taiwan at 70–90% of some links.
      A view that surfaces single points of failure would use data already in
      the flow graph.
- [ ] **Mobile** — the panel works at phone width but has not been designed
      for it. Direction C's list layout may be the better small-screen answer.
- [ ] **Export** — share a view, or hand off the computed table.
- [ ] **Move to a repo** if this outgrows a single file. Vite + React was the
      alternative considered; the component split was sketched as
      `components/map`, `components/panel`, `components/chrome`, `data/`,
      `model/`, `hooks/`.

---

## Known gaps in the current build

- All model inputs are illustrative. The panel says so on every node; there is
  no longer a global badge (removed in v0.3.2).
- Air quality is an exposure **index**, not a physical unit. It is normalized
  against the largest site in view, so it moves when the fleet changes.
- Metric bars are scaled against the largest site, which also means they move
  when nodes are added or removed.
- Added nodes have no upstream or downstream links.
- Saved edits live in one browser. Clearing site data loses them; Export is
  the backup once it exists.
- Singapore has no polygon at 110m resolution, so the Jurong mark sits on open
  water. Expected at this geometry resolution.
- Dense clusters (Taiwan, Korea) overlap at world zoom now that marks are
  bold. Zoom separates them; collision-aware placement is unimplemented.
