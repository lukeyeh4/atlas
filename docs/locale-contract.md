# Locale data contract

Status: **v1, agreed shape; not yet produced.** Both branches carry this file
unchanged. Change it only by agreement, and bump `v` when a change would break
the other side.

## Why

A city on the map — searched, or dropped with right-click — reaches the app
from Mapbox as ISO codes:

```
{ name: "Abilene", c: [-99.73, 32.45], iso1: "US", iso2: "US-TX" }
```

The app looks its location inputs up by those codes, most specific first:

```
subdivision (US-TX) → country (US) → none
```

and shows which level each value came from. The curated grid regions
(`REGIONS` in `index.html`, e.g. `us-pjm`) stay as they are for the built-in
sites; they are not part of v1.

## Ownership

| | Owns | Never touches |
|---|---|---|
| Database side | `data/`, `db/`, producing `data/locales.json` | `index.html` |
| App side | `index.html`, reading `data/locales.json` | `data/`, `db/` |

The file is the only interface. The app never parses the CSVs.

## The file: `data/locales.json`

Generated (e.g. `data/scripts/locales.py`, run from `build_all.py`),
committed, served by GitHub Pages next to `index.html`. The app fetches it
once at boot; if it is missing or fails to parse, the app falls back to its
inline sample `COUNTRY` table.

```json
{
  "v": 1,
  "built": "2026-09-27",
  "countries": {
    "US": {
      "n": "United States of America",
      "ci":   {"v": 383.8, "conf": "estimated", "year": 2024, "src": "ember"},
      "fos":  {"v": 0.5812, "conf": "estimated", "year": 2024, "src": "ember"},
      "dec":  {"v": 0.03, "conf": "estimated", "src": "ember", "note": "CAGR 2015–2024, derived"},
      "ws":   {"v": 0.521, "conf": "estimated", "src": "aqueduct"},
      "wue":  {"v": 0.08, "conf": "disclosed", "year": 2025, "src": "aws-fact-sheets"},
      "pm25": {"v": 7.0, "conf": "measured", "src": "who-pm25"}
    }
  },
  "subdivisions": {
    "US-TX": {
      "n": "Texas",
      "ci":  {"v": 0, "conf": "estimated", "year": 2024, "src": "ember-us", "basis": "generation"},
      "fos": {"v": 0, "conf": "estimated", "year": 2024, "src": "ember-us"},
      "dec": {"v": 0, "conf": "estimated", "src": "ember-us"}
    }
  },
  "sources": {
    "ember": {"title": "Ember yearly electricity data", "url": "https://ember-energy.org/data/"}
  }
}
```

(Values above illustrate the shape, not real figures.)

### Keys

Codes are **as Mapbox returns them**, since that is what the app has in hand:

- `countries` — ISO 3166-1 alpha-2, upper case: `US`, `CN`, `TW`. Matches
  `iso_3166_1` on Mapbox country boundaries and place labels, and
  `context.country.country_code` (upper-cased) from Mapbox geocoding v6.
- `subdivisions` — full ISO 3166-2: `US-TX`, `CN-GD`, `IN-MH`, `AU-NSW`.
  Matches `iso_3166_2` on place labels and `context.region.region_code_full`
  from geocoding. Note current codes: China uses letter codes (`CN-GD`, not
  `CN-44`); Telangana is `IN-TG`. India's 2023 ISO recoding (`IN-TS`,
  `IN-CG`, `IN-OD`, `IN-UK`) is not what Mapbox returns today; the file uses
  the older `TG / CT / OR / UT` and the app aliases the new codes onto them.

### Values

| Key | Meaning | Unit | Level |
|---|---|---|---|
| `ci` | grid carbon intensity | gCO₂/kWh | country, subdivision |
| `fos` | fossil share of generation | 0–1 | country, subdivision |
| `dec` | annual decarbonisation rate | fraction/yr (may be negative) | country, subdivision |
| `ws` | water stress | 0–1 | country (subdivision later) |
| `wue` | on-site water per kWh — location-based climate estimate (cooling-tower assumption, so an upper bound where free cooling is used) | L/kWh | country |
| `wue_disclosed` | optional — an operator's own disclosed or design figure for that country; display only, not a location property | L/kWh | country |
| `pm25` | annual mean PM2.5 | µg/m³ | country |

Each value is an object:

| Field | Required | |
|---|---|---|
| `v` | yes | number |
| `conf` | yes | `measured` / `disclosed` / `estimated` / `projected` |
| `src` | yes | a key in `sources` |
| `year` | no | data year |
| `basis` | no | short tag, e.g. `generation`, `consumption`, `lifecycle`, `direct` |
| `note` | no | one line, shown in the panel |

Rules:

- **Omit unknown values.** No `null`, no zero placeholders, no `sample`
  values — a missing key makes the app fall back to the next level.
- `n` (display name) is required on every entry.
- A subdivision entry never needs to repeat its country's values.
- Grids that don't match a subdivision map onto the one they serve and say so
  in `note`: `WA-SWIS` → `AU-WA`; ACT is in the NEM NSW region, so `AU-ACT`
  may carry NSW's values with a note.

## App behaviour (for reference)

`localeFor({iso1, iso2})` returns, per key, `{v, conf, src, level}` where
`level` is the code it came from (`US-TX` or `US`). The grid keys `ci`,
`fos` and `dec` travel together: they come from the most specific level
that has **all three**, so a subdivision's grid values are only used when
it has the full set; otherwise the panel lists them as not used. Other keys
fall back one by one. The panel labels each
value with that level and its confidence. Unknown at every level → the value
is shown as missing and the node can't be modelled on it.

## Versioning

- Adding a new optional field or value key: no bump.
- Renaming or removing a key, or changing a unit or code system: bump `v`.
  The app refuses a file whose `v` it doesn't know and uses its fallback.
