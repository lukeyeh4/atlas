# AI Supply Chain Atlas — Roadmap

Status as of 2026-09-26. Current build: v0.4.1, a single HTML file served
from GitHub Pages on a Mapbox globe. Ordered roughly by what unblocks the most.

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
- [ ] **City search with locale data** — waiting on the database work. Plan:
      Mapbox geocoding for cities in search (curated sites listed first);
      each result carries country and state codes. Look values up from the
      most specific level down: grid region (point-in-polygon on grid-region
      shapes) → state/province (`US-TX`) → country (`US`), and show which
      level each value came from. Data keyed by those codes; debounce
      queries to stay inside the Mapbox free tier.

### Node editing
- [ ] Edit a node's inputs in the panel (power, utilization, PUE), not just
      add and remove it. The model already recomputes on every render.
- [x] Let an added node be placed anywhere — right-click the map, "Add node
      here" (v0.4.1).
- [ ] Name placed points. They're "New site n" until reverse geocoding lands
      with the city search work.
- [ ] Draw and edit flows for added nodes. Right now a new node has no chain.
- [ ] Persist edits. Nothing survives a reload today.
      (An artifact runtime capability could hold this; see
      the `artifact-capabilities` skill.)

### Layers
- [ ] **Land and cooling** is a placeholder — no data bound, paints neutral.
- [ ] Decide whether layers should be comparable across years the way the
      carbon layer was before the scrubber came out.
- [ ] Accessibility pass on the ramps: check each layer's endpoints for
      contrast in both themes, and don't rely on hue alone.
- [ ] Border hierarchy: US state lines (v0.4.1) now read stronger than
      country borders over the fills. Country borders should match or
      outweigh them.
- [ ] State or province lines beyond the US, if a layer needs them.
- [ ] Optional thin major rivers between zoom 3 and 6, where streets water
      is hidden.

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
- Dense clusters (Taiwan, Korea) overlap at world zoom now that marks are
  bold. Zoom separates them; collision-aware placement is unimplemented.
- Points placed from the context menu are named "New site n", and countries
  without a `REGIONS` entry get a country-average region built from sample
  `COUNTRY` values.
- The compare view drops units: 4.77 (TWh) sits beside 391 (GWh) unlabeled.
- The Mapbox token is public in `index.html`; it must be URL-restricted in
  the Mapbox account.
- The README screenshot still shows the v0.3 flat map.
