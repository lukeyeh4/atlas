# AI Supply Chain Atlas — Changelog

A map-first tool for visualizing the AI supply chain, from quartz to inference,
with the environmental load of each node.

v0.1–v0.3 lived in published artifacts. From v0.4 the app is `index.html` in
this repo, served from GitHub Pages. v0.4 is dated 2026-09-26; v0.5 onward, 2026-09-27.

---

## v0.12.1 — Key
- **The stage toggles sit inside a "Key" that opens sideways** in the top
  bar, as the stage row always did, and folds away to a single "Key"
  button at the right (chevron ‹ to open leftward, › to fold). It starts
  open; open or folded is remembered per viewer.
- **Connections sub-group** after a thin divider: a small "Connections"
  label that unfolds to two toggles in the same style as the stages, each
  with its arc's dashed line and marker as the icon: **Goods** and
  **Compute** (full description on hover). Hiding a kind removes its arcs
  and markers from the globe. It starts unfolded on wide screens (1500 px
  and up), folded otherwise, and remembers the viewer's choice.
- Folded, the button reads **"Key · 2 hidden"** in accent whenever a stage
  or connection kind is hidden, so a filtered map is never a surprise. Open,
  it just reads "Key": the toggles show their own state.
- To fit everything in one bar down to 1280 px: key type 9.5 px (9 px below
  1360 px), tighter gaps, search box 220 px (140 px minimum).

## v0.12.0 — Moving markers, coloured by kind
- **A hue per kind of link again**, following the reference: copper goods,
  teal designs/data/models, ochre money, muted violet policy (dotted), steel
  blue feedback (dashed). Tokens in both themes.
- **Globe arcs are coloured by what they carry**: into chip making or
  infrastructure it's physical goods (copper); into model building or
  delivery it's compute and models (teal). Zhengzhou → Ashburn is copper,
  Ashburn → San Francisco and Frankfurt teal.
- **Markers travel the arcs** from supplier to customer: small squares for
  goods, dots for compute and models, each with a thin halo so it reads on
  any fill. They follow the great-circle path at an even angular pace (a
  short hop takes 1.6 s, the longest 5 s), one to three per arc, redrawn
  about 30 times a second only while a site's arcs are showing; they hide
  behind the globe's horizon like everything else.
- **Markers ride the diagram's links** in the direction of transfer, shaped
  by kind: square goods, round data, diamond money, a short pill for policy,
  a ring for feedback. One per ~320 units of path at an even pace,
  staggered so they don't march in step. Hovering or pinning a part keeps
  only its links' markers.
- Reduced motion (the system setting): no markers anywhere.

## v0.11.2 — Connections: main chain first, bundled, pinnable
- **Opens on the main chain**: physical goods and designs/data/models only
  (27 links). Money, policy and feedback loops are one legend click away;
  "Reset view" returns to the main chain and releases any pin.
- **Bundled paths.** Links of one kind that leave the same box share one
  point on its edge, and links that share an end share one lane through
  every channel and gap, so a fan-out is one trunk that branches and a
  fan-in one that gathers (Governments' five policy links are now one dotted
  trunk). Only the links shown are routed, so hidden kinds take no lanes and
  the rest spread out. Each kind is drawn as one group, so overlapping
  trunks don't darken.
- **Click to pin.** Clicking a part (or Enter/Space on it) keeps its links
  highlighted while the pointer moves on; the bar reads "Pinned · Data
  centers". Click it again, click anywhere else in the diagram, or press
  Escape to release; a second Escape closes. Pins survive legend toggles.

## v0.11.1 — Connections, redrawn for reading
- **Metro-map routing.** Links travel only through the channels between
  columns and the gaps between rows, never across a box, turning with
  rounded corners. Every link gets its own lane in each channel and gap it
  uses, and its own point along a box's edge (ordered by where the other
  end sits), so parallel links run side by side instead of converging.
  Forward links leave right and enter left; links within a column and
  backward links enter on the right.
- **Calmer palette.** Only the main flows carry a hue, each softened:
  physical goods (copper), designs/data/models (teal), money (ochre).
  Policy and feedback loops are neutral grey, told apart by dots and
  dashes, and drawn fainter as context until a part is hovered.
- **Open chevron arrowheads** (6 px, stroked in the link's colour) replace
  the filled triangles; the chokepoint diamond is smaller.
- Slightly smaller boxes and type; hovering dims the rest further (links to
  7%, parts to 30%).

## v0.11.0 — Connections diagram
- **Connections**, a button next to Scenario, opens the whole system as a
  diagram over the map: the six stages as columns (raw inputs, tools and
  design, chip making, infrastructure, model building, delivery) and a band
  for data, people and policy. 25 parts, 38 links.
- **Five kinds of link**, each with its own colour and line style so they
  don't rely on hue: physical goods, designs/data/models (solid), money
  (solid), policy and control (dotted), feedback loops (dashed). Legend chips
  toggle each kind; "Reset view" restores all.
- **Chokepoints** carry a small diamond: silicon and quartz, specialty gases,
  critical minerals, substrates, lithography, foundry, HBM, advanced
  packaging, power.
- **What the map models is emphasised slightly**: a teal edge bar, stronger
  title and border, and a count of its sites (Data centers 7, Inference 5,
  Pretraining 4, Foundry 3, HBM 3, …; Power and grid reads "grid", since
  it's modelled as each site's grid). Nodes you add count by facility type;
  removed sites drop out.
- **Hover a part** to trace it: its links and neighbours stay, the rest steps
  back. Escape or ✕ closes. Colours are tokens in both themes.

## v0.10.2 — Quieter by default, clearer on hover
- **Layer fills are muted** to 55% (from 94%), and hovering never changes a
  colour.
- **Hover names the place.** The country or US state under the pointer shows
  its name in full ink with a soft halo (`hover-label`), with or without a
  layer on, from the zoom where country names appear (2.6); below that,
  hovering shows nothing. That country's regular label steps aside while it
  shows. US state names appear only on hover.
- **Other labels are a touch fainter** (`--map-label`, `--map-label-on`), so
  the hovered name stands out.
- Site markers stay at full strength (briefly muted during this release,
  then reverted: they're the data, the fills and labels are the backdrop).
- **The panel folds away detail.** "Location inputs" is now a collapsible
  section like "Compare locations": both closed by default and remembered
  per viewer. The location name moved into its header, so the separate
  "Location inputs · …" line is gone.
- Units lose their dotted underline; the help cursor and the callout remain.

## v0.10.1 — US states on the map, unit callouts, thin scrollbars
- **US states have their own colour** on any layer that has state values:
  grid carbon today (all 50 states and DC, from `data/locales.json`), so
  West Virginia and Vermont no longer share the US average. State shapes are
  us-atlas (Census cartographic boundaries, ~115 KB from jsDelivr) with
  topojson-client, matched by FIPS code; without them the layer stays
  country-level. Water stress is by state too (Aqueduct's own province
  scores, same method as the country value: Arizona 0.88, Virginia 0.51,
  Washington 0.24); Hawaii has no score and takes the US value. Air stays
  country-level. A point still reads its own basin first, so Ashburn shows
  0.03 while Virginia colours at 0.51.
- **Unit callouts** replace the browser's native tooltip. Hovering a
  dotted-underlined unit opens a small box (panel surface, hairline border,
  a hairline stem down to the unit, flipping below near the top): the unit
  and its full name, a rule, then one sentence for scale, e.g. "1 GWh is a
  year of electricity for about 95 US homes", "1 kt is what about 220 petrol
  cars emit in a year", "Coal power is about 1,000; wind, solar and nuclear
  are under 50".
- **Thin scrollbars** (5 px, rule-coloured thumb, no track) on the panel,
  search results and menus.
- **Readable labels over layers.** With a layer on, country and city labels
  switch to a darker ink (`--map-label-on`) with a soft 1.3 px halo in the
  page colour (`--label-halo`), so names read on the darkest fills in both
  themes. With no layer, labels stay quiet and unhaloed as before.
- Compare locations: multiples past ten read "×10+", since they mostly
  reflect a near-zero value where the node is.

## v0.10.0 — Data center size, sourced map layers
- **Size slider for data centers.** Training and inference data centers get
  a "Size" row under the bars: a hairline track with a square accent handle,
  logarithmic so both ends have resolution, and a mono readout. Bounds sit a
  little wider than the sourced typical range: training 50 MW–2 GW (typical
  200, sourced range 200–1,200), inference 5–200 MW (typical 20, sourced
  10–100). "↺ typical 200 MW" resets. Dragging updates the bars live;
  releasing updates everything the size feeds (scale, scenario deltas,
  compare locations). Arrow keys, Home and End work. Other facility types
  keep their typical size.
- **Map layers read `data/locales.json`.** Grid carbon, water stress and air
  quality now colour every country with a sourced value (212, 166 and 201
  countries) instead of the 64-country sample table. Air quality is annual
  PM2.5 in µg/m³ on the same ramp. Countries without a value, mostly small
  territories (and Albania for carbon), stay hatched "no data", as do
  disputed areas. Offline, the sample table still paints.

## v0.9.1 — Water stress by river basin
- Cells now carry **basin water stress** (WRI Aqueduct 4.0, the sub-basin at
  each cell, same 0–1 scale as the country value): 347 tiles, 8.8 MB. Every
  site and searched place reads it locally, e.g. Ashburn 0.03 (low) where
  the US average is 0.52, Austin 0.56, Abilene (Kansas) extremely high.
  Profiles say "in its river basin"; the panel marks it `local`.
- Taiwan and Singapore keep their researched country values on purpose
  (Aqueduct's basins mislead there), as do cells Aqueduct doesn't cover.
- Aqueduct's rules carry through: arid, low-use basins score 1.0, and
  upstream river inflow counts as supply, so river-fed dry cities read low.
- Water stress describes a place; it doesn't change the modelled water
  volume, which is energy × water rate.
- Cooling water and PM2.5 stay at country level by decision, not as a gap
  (earlier entries said they would follow).

## v0.9.0 — Built-in sites on sourced data
- **The 32 built-in sites now get their numbers the way added nodes do**:
  inputs from their facility type in `data/node-types.json`, people within
  100 km from their cell, and grid, water and air from cell → state →
  country. `SITE_META` in `index.html` gives each site its type and ISO
  codes (looked up once from Mapbox, stored, so there's no geocoding per
  page load). The three candidate locations get codes too.
- Types: mines (Spruce Pine, Bayan Obo, Greenbushes, Grasberg), materials
  (Yamaguchi), fabs (Hsinchu, Tainan, Pyeongtaek, Icheon, Hiroshima,
  Chandler), equipment & optics (Veldhoven, Oberkochen), packaging & test
  (Kaohsiung), hardware assembly (Zhengzhou, Taoyuan), training data centers
  (Ashburn, The Dalles, Council Bluffs, Abilene, Dublin, Jurong, Ulanqab),
  AI labs (San Francisco, Seattle, London, Beijing), inference data centers
  (Frankfurt, São Paulo, Mumbai, Tokyo, Lagos).
- Sites of one type now share their size: every fab is 195 MW, every
  training data center 200 MW. Differences between them come from place.
  Ashburn drops from the sample 620 MW (4.77 TWh) to 200 MW (993 GWh).
- The hand-written note stays on each built-in site; its data profile sits
  under it in smaller type.
- The curated grid regions (PJM, ERCOT, …) no longer feed the built-in sites;
  Ashburn uses Virginia's grid until a grid-region level exists. The inline
  sample `REGIONS` and `in` values are kept only as the offline fallback.

## v0.8.0 — Compare locations, unit names
- **Compare locations**, a collapsible section under the bars (›, same mono
  eyebrow as the rest of the panel). It puts the selected node, with the
  same type and inputs, at 11 reference places (Ashburn, Abilene, The
  Dalles, Dublin, Luleå, Frankfurt, Hsinchu, Singapore, Tokyo, Mumbai, São
  Paulo). Each is a real point, so it brings its own grid, cooling water and
  people within 100 km. Rows show carbon, water and air against "here",
  sorted cleanest first; lower is accent, higher is warn, and anything past
  double reads as a multiple (×2.8). Places within 50 km of the node are
  skipped. Open or closed is remembered per viewer.
- **Unit names on hover.** Every abbreviated unit (TWh, kt CO₂e, k m³,
  index, g/kWh, L/kWh, µg/m³, %/yr, ≤100 km, MW) carries its full name;
  water stress explains its 0–1 scale.
- The node-inputs line ("Data center (inference) · typical inputs · P 20 MW
  …") now appears only with **formulas** on, next to the equations it feeds.

## v0.7.0 — Each place its own
- **Location cells.** Placed and searched points look up a 0.25° cell
  (about 25 km) before their state and country: people within 100 km today,
  with cooling water, basin water stress and PM2.5 to follow as the
  database side adds them. Tiles are 10° files under `data/cells/`, fetched
  once each and only when `data/cells/index.json` lists them. The panel
  marks cell values `local`.
- **Two-level add menu.** "Add node" shows the five stages, each with `›`;
  choosing one opens its facility types under "Add node · Chip making",
  indented, with "‹ All stages" to go back. Focus follows, so it works from
  the keyboard. Without `data/node-types.json` a stage adds its sample node
  directly, as before.
- **Facility types.** "Add node" offers nine types from
  `data/node-types.json` (mine, materials & wafers, fab, packaging & test,
  equipment & optics, training data center, hardware assembly, AI lab,
  inference data center) instead of one sample set per stage. A new node
  starts from its type's typical power, utilisation, PUE and growth, and
  from its cell's population.
- **Water by facility type.** Types with a process-water rate (fabs, mines,
  assembly…) use it: `W = E · rate`. Data center types use location cooling
  water on IT energy: `W = P · 8760 · u · WUE`. Curated sites are unchanged.
- **Generated profiles.** Searched and added places describe themselves from
  their own values: "Mixed grid (Texas, 356 g/kWh). 3.4 M people within
  100 km. Medium-high water stress (US average). Moderate air (PM2.5
  7 µg/m³, US average)." Only sourced values are described; each says
  whether it's local or an average. Curated sites keep their notes.
- The "Training moves to Nordics" scenario counts added training data
  centers, not every added infrastructure node.
- Fix: utilisation was capped at 0.95 even for facility types whose inputs
  carry u = 1 by convention; the cap now only limits growth.
- `data/locales.json` now covers 248 countries (database build). Country
  carbon intensity comes from Ember's bulk file and is marked `estimated`.
- The contract (`docs/locale-contract.md`) gains two sections, location
  cells and facility types; additive, still v1.
- `data/cells/` is the database build: 328 tiles, 250,034 cells, 6.7 MB,
  people within 100 km worldwide (GHSL 2025; within 2–4% of exact 1 km sums
  at checked sites). Water, water stress and PM2.5 follow.
- An optional `absent` entry in `data/cells/index.json` says what a missing
  cell means (for population: fewer than 500 people within 100 km); the app
  reads it, and without it a missing cell stays unknown.
- `data/node-types.json` is the database build: nine types, each value
  with its own source; `u` / `pue` = 1 on average-draw types are marked
  `model-convention`. AI labs have no researched water rate, so they fall
  back to location cooling water like data centers.
- Fix: city search hid any city within 25 km of a site already on the map,
  so Phoenix vanished behind Chandler. A result is now hidden only when it
  has the same name within 25 km, or the same Mapbox id.
- Loads under 10 MW show one decimal (1.5 MW, not 2); populations under
  1,000 read "< 1k".

## v0.6.0 — What-if scenarios
- **Scenario menu** in the top bar, next to search: an underlined mono
  button like the layer switch, dropping a small menu. The button turns
  accent while a scenario other than Baseline is on. Arrow keys and Escape
  work in the menu.
- Four presets. Each rewrites inputs just before the model runs; the data is
  never changed, so Baseline restores everything:
  - **Baseline** — inputs as sourced or sampled.
  - **Fast grid decarbonisation** — grid carbon intensity and fossil share
    halved everywhere.
  - **Training moves to Nordics** — data center campuses (Ashburn, The
    Dalles, Council Bluffs, Abilene, Dublin, Jurong, Ulanqab, and any added
    infrastructure node) modelled on Sweden's grid, from
    `data/locales.json` when present. Markers stay put; only the grid moves.
  - **Data center boom (2× power)** — those campuses draw twice the power.
- Under a scenario the panel shows what changed for the selected site
  against baseline ("vs baseline · carbon −89% · water −34% · air −98%"), or
  "No change for this site".
- Metric bars and the air index are now scaled against the **baseline**
  fleet, so a scenario moves them instead of rescaling them away. Under the
  boom, Ashburn's air index reads 145.
- Map layers keep showing the data as sourced, not the scenario.

## v0.5.0 — Real city names, locale data
- **City search.** Past three letters, search also asks Mapbox Geocoding
  (v6, debounced, English names) for cities. Curated sites and locations
  come first; a city within 25 km of one is left out. Choosing a city drops
  a location ring there and opens it.
- **Placed points get real names.** "Add node here" places the point at
  once, then reverse geocoding names it (e.g. "Garwood · Texas, United
  States") and supplies its state code. Offline, or far from any city, it
  stays "New site n".
- **Locale data by ISO code.** Searched and placed points look their inputs
  up in `data/locales.json`: subdivision (`US-TX`) first, then country
  (`US`). The panel lists each input with the level it came from, its
  confidence, and a link to its source; defaulted values are marked
  `default · sample` in the warning colour. Curated sites are unchanged.
- **Contract with the database side:** `docs/locale-contract.md`. The
  database side writes `data/locales.json`; the app only reads it and falls
  back to the sample tables when the file is missing or of an unknown
  version.
- `data/locales.json` is the database side's build: 64 countries, 126
  subdivisions (US 51, IN 36, CN 31, AU 8), 43 sources; every value carries
  its confidence and source. Checked against the contract on arrival.
- WUE is the climate-based estimate and shows as `≤`, since it assumes a
  cooling tower; an operator's own figure, where one exists, is listed
  beneath it as **Operator** and isn't used by the model.
- Grid values travel together: carbon intensity, fossil share and trend
  come from the most specific level that has all three, so a point never
  pairs one grid's carbon with another's fossil share. Where local values
  are passed over, the panel says so ("Not used · Tibet (Xizang) fossil 3%
  — its grid data is incomplete, so the grid comes from China"). Water
  values still fall back one by one.
- India's 2023 ISO codes (`IN-TS`, `IN-CG`, `IN-OD`, `IN-UK`) are aliased to
  the codes Mapbox returns today.
- Geocoding results are shown, never stored, per Mapbox's temporary
  geocoding terms.

## v0.4.2 — Globe / flat switch
- Small segmented switch, top-right of the map: **Globe** or **Flat**.
  Semi-opaque surface with a backdrop blur, same mono labels and 12px line
  icons as the other controls; arrow keys move between the two.
- Flat is Mercator. Mapbox's Natural Earth projection was tried first but
  drops the hillshade ("terrain is not yet supported with alternate
  projections") and rendered unevenly when zoomed; Mercator keeps every
  layer and is what the globe already becomes at close zoom.
- Switching at world scale reframes: flat fits one world width into the
  visible map, globe returns to its world view. Closer in, only the
  projection changes.
- The choice is remembered per viewer in `localStorage`; the page works the
  same without it.
- **Fix: ~30 countries were missing from the map.** Mapbox stores
  `worldview` as a comma list where borders are disputed (e.g.
  `"CN,IN,JP,MA,RS,RU,TR,US"`); the filter only matched `all` or exactly
  `US`, so those polygons were dropped. They showed as open water in the
  context menu and had no regional colour. Affected: Russia, China, India,
  Pakistan, Bhutan, Japan, South Korea, Taiwan, Hong Kong, Vietnam,
  Philippines, Turkey, Syria, Greece, Serbia, Kosovo, Croatia, Ukraine,
  Morocco, Western Sahara, Argentina, Falklands, South Georgia, Kenya,
  South Sudan, and the disputed areas along their borders. The filter now
  tests membership; checked against every country in the tileset and by
  right-clicking 20 of them on both globe and flat.
- **No data** gets its own fill: grey with a fine light 45° hatch
  (`--nodata`, `--nodata-line`, drawn to a 2x canvas pattern and rebuilt on
  theme change). Countries without a `COUNTRY` record and disputed areas
  used to take the low end of the ramp, which read as "cleanest". A matching
  "No data" swatch sits right after cleaner → dirtier in the bottom bar,
  same size and mono label; hidden for the placeholder Land and cooling
  layer.

---

## v0.4.1 — Map context menu
- Right-click (long-press on touch, ContextMenu key or Shift+F10 for the
  selected mark) opens a menu for whatever is under the pointer:
  - **Site** — open details, compare with the selected site, go upstream,
    zoom to, copy coordinates, remove node.
  - **Placeholder** — add node, zoom to, copy coordinates; remove location
    for points placed by hand.
  - **Land** — add node here (the country's grid region, the nearest known
    region when a country has several, or a country average from `COUNTRY`;
    disabled with "No grid data" otherwise), zoom in, copy coordinates.
  - **Water** — zoom in, copy coordinates.
- Same surface, rules, mono labels and hover as the search and layer menus;
  12px line icons in the search glyph's style. Arrow keys, Home/End, Enter,
  Escape. Flips upward near the bottom edge; closes on map move.
- One shared entrance animation for search results, layer menu and context
  menu; off under reduced motion.
- "Copied" confirmation toast, centred in the visible map.
- US state boundaries (streets-v8 `admin_level` 1, `US`). A light line in
  dark mode and a dark one in light mode, via a new `--state-line` token,
  since the border colour vanished against the ramp fills. 0.7–1.4 px,
  fading in linearly from zoom 1.8 to full strength at 4.5.
- Page is ~77 KB with the menu.

---

## v0.4.0 — Mapbox globe
Runs on GitHub Pages rather than as an artifact, so the tile-server
restriction behind the v0.3 inline geometry no longer applies.

- Basemap moved from d3 + inline Natural Earth 110m to Mapbox GL JS v3 with a
  custom dark, muted style: streets-v8 water, borders and labels,
  terrain-dem-v1 hillshade, globe projection with a quiet atmosphere.
- Regional layers paint `mapbox.country-boundaries-v1` by ISO code. Stack is
  ocean → landmass → fill → detail water → hillshade → borders → labels →
  flows, so fills stay close to the legend colour and relief sits on top as a
  faint texture.
  Hillshade backs off (0.6 → 0.32) while a layer is on.
- Coastlines come from the country polygons below zoom 6. Streets water
  (every lake, reservoir and river bank) fades in between zoom 6 and 7.5;
  earlier it read as dark specks across the regional fills.
- `COUNTRY` is now keyed by ISO 3166-1 alpha-2 codes.
- Sites and placeholder cities are Mapbox markers; flows are a line layer,
  antimeridian-safe great circles.
- The map re-centres in the space the panel leaves; picking from search
  eases to the site.
- Map rotation disabled; Mapbox logo and attribution bottom-right.
- Page is ~62 KB, down from ~218 KB, now that the geometry isn't inlined.
- Added the missing `<meta charset>` and viewport tags.

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
