# AI Supply Chain Atlas — Changelog

A map-first tool for visualizing the AI supply chain, from quartz to inference,
with the environmental load of each node.

All work to date lives in published artifacts (single-file HTML, no repo yet).
Dates are the session date, 2026-09-26.

---

## v0.3 — Quiet Atlas, full build
**Artifact:** https://claude.ai/artifact/9beLBKGJksuNZJVMdSXr3V

The chosen direction, built out as a working app. Current versions below are
revisions of this same artifact.

### v0.3.0 — first full build
- Real basemap: Natural Earth 110m country geometry, embedded inline (the
  artifact CSP blocks external tile servers, so no Mapbox/Leaflet).
  Natural Earth projection via `d3.geoNaturalEarth1`, pan and zoom to 9x.
- 31 sites at real coordinates across five stages: raw inputs, chip making,
  infrastructure, model building, delivery.
- Working metric model on sample inputs:
  - `E = P_IT · 8760 · u · PUE` — energy, MWh/yr
  - `C = E · CI` — carbon, tCO2e
  - `W = E · WUE` — on-site water, m³
  - `A = E · fossil share · downwind population` — air exposure, index 0–100
- Per-region inputs (grid carbon intensity, decarbonization rate, WUE, water
  stress, fossil share) and per-site inputs (power, utilization, PUE, growth,
  downwind population).
- Inspector panel: identity, coordinates, metrics with optional formulas,
  the inputs actually used, and clickable upstream/downstream chain links.
- Search over sites, regions, stages and notes. `/` or ⌘K to focus.
- Compare mode: pick a second site, see per-metric deltas.
- Year scrubber 2020–2036 with capacity growth, PUE improvement and grid
  decarbonization; totals for energy and carbon across visible sites.
- Regional layers: grid carbon intensity, water stress.

### v0.3.1 — category glyphs
- Replaced uniform dot marks with bold per-stage glyphs, halo outlined
  (`paint-order: stroke fill`, non-scaling stroke).
- Glyphs double as the legend in the stage filter row, in search results,
  and in the panel eyebrow — no separate legend box.
- Selected marks sort to the front so they clear neighbours in dense clusters.

### v0.3.2 — declutter and node editing
- Marks are now black fill with a white outline in both themes.
- Delivery glyph changed to a box with a tape band.
- Bottom bar cut to two controls: layer menu and its scale. Removed the year
  scrubber, the TWh / Mt CO2e totals, and the sample-inputs badge.
- Layer menu gained placeholder entries, tagged as such.
- Three placeholder cities (Querétaro, Johannesburg, Riyadh) render as dashed
  rings with a plus. Selecting one offers **Add node** with a stage picker;
  the new node starts from default sample inputs for that stage.
- **Remove** on any node — including the original 31 — reverts the location to
  a placeholder ring rather than deleting it, so it can be re-added as a
  different type. Flows to a removed node hide and return on re-add.

### v0.3.3 — square glyphs and layer palettes  ← current
- Every glyph normalized to an exact 15 × 15 bounding box, so all five marks
  carry the same visual weight.
- Each layer now has its own muted ramp, defined as theme-aware CSS tokens:
  - grid carbon intensity → **yellow / ochre**
  - water stress → **blue**
  - air quality → **gray**
  - land and cooling → **green** (still a placeholder, no data bound)
- Air quality is now a live layer: a sample air-quality index was added as a
  third value on every country record.

---

## v0.2 — three minimal directions
**Artifact:** https://claude.ai/artifact/83rEsv7DsjLQ8DRNzm4qXY

Response to "too cluttered." Three directions on one page, each with the same
live map and real coordinates:

- **A · Quiet atlas** — map is the page, one line of chrome, detail slides in
  from the left on selection. *Chosen.*
- **B · Night instrument** — dark ground, one floating control strip, detail
  as a card pinned to the mark with a leader line, live cursor lat/long.
- **C · Ledger** — nothing floats on the map; a typographic list on the left
  is both the filter and the inspector.

Cut from v0.1 in all three: the legend (one mark type, nothing to decode), the
year scrubber, the layer dropdown, the persistent flow layer, the chip rows,
and the annotation callouts. Flows now draw only for the selected site.

---

## v0.1 — annotated wireframe
**Artifact:** https://claude.ai/artifact/7iajzrPJ3amDx7cK5Grwyv

Grayscale wireframe from the original sketch. Top bar, five-stage filter,
hatched placeholder basemap, inspector panel, legend, year scrubber, plus
secondary frames for flow view, region compare and mobile. Seven keyed
annotations and a data-contract table. No values bound.

---

## Standing decisions

| Decision | Where it landed |
|---|---|
| Basemap | Embedded Natural Earth vector geometry, not tiles (CSP) |
| Stage encoding | Glyph **shape**, never color — color belongs to the data layer |
| Legend | None; the stage filter row carries the glyphs |
| Flows | Drawn only for the selected node, never as a persistent layer |
| Regional layers | One at a time |
| Values | All model inputs are sample data, labeled in the panel |
| Typography | Source Serif 4 for names and reading, IBM Plex Mono for data |
| Accent | Single teal, used only for selection and chain relationships |
