# Database plan

Status: **prepared, not provisioned.** The schema and seed are in the repo; no
hosted database exists yet and the app runs without one.

**There are no accounts and no login.** That settles the split:

| Data | Lives in | Written by |
|---|---|---|
| Reference data — sites, regions, flows, country layers, sources | Database (later); `index.html` today | The maintainer only |
| A visitor's own edits — nodes added or removed | Their browser (`localStorage`) | That visitor |

A visitor's edits never go to the database. Without accounts, a table that
visitors write to would be writable by anyone on the internet: no ownership,
open to vandalism and spam.

## Where things stand

| Piece | State |
|---|---|
| Edits persist across reloads | Done — `localStorage`, key `atlas.edits.v1` |
| Export / import edits as JSON | Roadmap — the format below is ready for it |
| Schema for the reference data | Written — [`db/schema.sql`](../db/schema.sql) |
| Seed from the app's data | Written — [`db/seed-from-index.mjs`](../db/seed-from-index.mjs) → `db/seed.sql` |
| Hosted database | Not yet |

## The edits format

The app saves only a diff against the reference data:

```json
{
  "v": 1,
  "added":   { "queret": { "s": "infra", "in": { "p": 200, "u": 0.75, "pue": 1.2, "g": 0.1, "pop": 3 } } },
  "removed": { "hsin": true }
}
```

- `added` — a candidate location (or a removed site) turned into a node, with its stage and inputs.
- `removed` — a built-in site reverted to a candidate location.

localStorage holds this one object, and a future Export / Import would use it
unchanged. It is re-validated on every read (`cleanEdits()`), so stale or
hand-edited data can't break the page. The reference data is keyed by stable
ids, so saved edits still apply after the reference numbers are updated.

## Recommended: Supabase (hosted Postgres), read-only to the public

- **The app stays a static page on GitHub Pages.** The browser reads the
  database directly over HTTPS with the public `anon` key; no server of our
  own.
- **Public read, maintainer write.** Row-level security allows everyone to
  select and nobody to write. The maintainer writes through the Supabase
  dashboard or SQL editor, which uses the service role.
- **Postgres**, so the schema is portable if we leave.
- The free tier covers this data many times over.

## Why the schema is efficient

The data is small: 32 sites, 3 candidate locations, 25 regions, 37 flows,
248 countries and 126 subdivisions (states, provinces) keyed by ISO code. The costs to avoid are round trips, not table scans.

1. **One read for the whole map.** The `atlas_baseline` view returns
   everything the app draws as a single JSON document, shaped like the
   constants in `index.html`. No per-node queries.
2. **Per-value provenance without wide tables.** `site_input`, `region_input`,
   `country_value` and `subdivision_value` hold one row per value with its `confidence`
   (`measured / disclosed / estimated / projected / sample`) and `source_id`.
   That is the roadmap's confidence mark and citations. Real figures can
   replace samples one value at a time. The locale tables are already real:
   they are seeded from `data/locales.json`, and the view returns them in the
   same shape ([`docs/locale-contract.md`](locale-contract.md)).
3. **Indexes only where a query needs them.** The `flow` primary key serves
   downstream lookups and `flow_to_idx` serves upstream ones. Partial indexes
   on `source_id` keep deleting a source cheap.
4. **Integrity in the database.** Enums for stage and confidence, key and
   range checks on every value, and foreign keys from sites to regions and
   from flows to sites.

Verified locally on Postgres 18 (PGlite) with Supabase's default grants to
`anon`:
- the schema and seed load;
- the view round-trips the app's data (32 sites, 3 candidates, 25 regions, 37 flows) and reproduces `data/locales.json` exactly (248 countries, 126 subdivisions, 45 sources);
- `anon` can read the view;
- `anon`'s inserts are refused, and its updates and deletes touch 0 rows.

## Going live — steps

1. Create a Supabase project. Copy its URL and `anon` key; both are safe to
   ship in the page.
2. In the SQL editor, run `db/schema.sql`, then `db/seed.sql`.
   Regenerate the seed after changing data in `index.html`:
   `node db/seed-from-index.mjs > db/seed.sql` (it also reads `data/locales.json`).
3. In `index.html`, fetch `atlas_baseline` once at boot, over plain `fetch` to
   the REST endpoint; no client library is needed. Use it in place of the
   inline `SITES` / `REGIONS` / `FLOWS` / `COUNTRY` constants, and keep the
   inline copy as the offline fallback.
4. From then on, update reference numbers in the dashboard, not in
   `index.html`.

## Is a database needed at all?

Not yet, honestly. With one maintainer and data this small, the reference data
could equally be a `data/baseline.json` file in the repo: edited by commit,
served by GitHub Pages' CDN, with review and history for free. The database
earns its place when:

- someone other than the maintainer edits values without touching the repo;
- the sourced dataset grows past what is comfortable to hand-edit;
- the data is queried outside the app (analysis, other tools).

Either way the same schema shapes the data. The seed script already extracts
it from `index.html`, so moving to a JSON file first costs nothing.

## Sharing without accounts

Export / Import (on the roadmap) would share a scenario as a file. A lighter
option is encoding the edits diff in the URL (`#e=<base64>`): a few hundred
bytes, a shareable link, still no accounts and no server.
