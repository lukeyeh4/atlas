-- AI Supply Chain Atlas — database schema (PostgreSQL 15+, written for Supabase)
--
-- The shared reference data now hard-coded in index.html (regions, sites,
-- flows), plus the sourced location inputs in data/locales.json (countries
-- and subdivisions), with per-value confidence and source so sourced figures
-- can replace the samples one value at a time.
--
-- There are no accounts. The public reads; only the maintainer writes, through
-- the Supabase dashboard or migrations. Visitors' own edits never reach the
-- database — they stay in the browser (localStorage, Export / Import).
--
-- The whole baseline is ~31 sites, ~25 regions, 64 countries and ~130
-- subdivisions: the app reads it in a single request through the
-- `atlas_baseline` view and never queries per node. See docs/database.md.

-- ---------------------------------------------------------------- types ----

create type stage as enum ('raw', 'chip', 'infra', 'model', 'delivery');

-- How much to trust a value. `sample` is everything the app ships with today.
create type confidence as enum ('measured', 'disclosed', 'estimated', 'projected', 'sample');

-- -------------------------------------------------------------- sources ----

create table source (
  id           bigint generated always as identity primary key,
  key          text unique,         -- 'ember', 'aqueduct', ...: the `src` keys in data/locales.json
  title        text not null,
  url          text,
  publisher    text,
  published_on date,
  accessed_on  date
);

-- ------------------------------------------------------------- regions -----
-- A grid region. Its numeric inputs live in region_input, one row per value.

create table region (
  id   text primary key,          -- 'us-pjm', 'tw', ...
  name text not null
);

-- ci  grid carbon intensity, gCO2/kWh     dec  annual decarbonisation rate
-- wue water usage effectiveness, L/kWh    ws   water stress, 0-1
-- fos fossil share of generation, 0-1
create table region_input (
  region_id   text not null references region on delete cascade,
  key         text not null check (key in ('ci', 'dec', 'wue', 'ws', 'fos')),
  value       double precision not null check (value >= 0),
  confidence  confidence not null default 'sample',
  source_id   bigint references source on delete set null,
  as_of       date,
  primary key (region_id, key)
);

-- --------------------------------------------------------------- sites -----
-- A modeled node, or a candidate location when stage is null (the dashed
-- rings in the app). Keeping both in one table means a location keeps its id
-- when it becomes a node and when it is removed again — as the app does.

create table site (
  id        text primary key,       -- 'hsin', 'ashb', 'queret', ...
  name      text not null,
  place     text not null,
  stage     stage,                  -- null = candidate location
  lon       double precision not null check (lon between -180 and 180),
  lat       double precision not null check (lat between -90 and 90),
  region_id text not null references region,
  note      text
);

create index site_region_idx on site (region_id);

-- p   IT / process load, MW     u    utilisation, 0-1     pue facility overhead
-- g   annual growth             pop  downwind population within ~100 km, millions
create table site_input (
  site_id     text not null references site on delete cascade,
  key         text not null check (key in ('p', 'u', 'pue', 'g', 'pop')),
  value       double precision not null check (value >= 0),
  confidence  confidence not null default 'sample',
  source_id   bigint references source on delete set null,
  as_of       date,
  primary key (site_id, key)
);

-- --------------------------------------------------------------- flows -----
-- Directed supply links. The primary key serves downstream lookups;
-- flow_to_idx serves upstream ones.

create table flow (
  from_site text not null references site on delete cascade,
  to_site   text not null references site on delete cascade,
  share     numeric(4, 3) check (share between 0 and 1),  -- share of supply, when known
  source_id bigint references source on delete set null,
  primary key (from_site, to_site),
  check (from_site <> to_site)
);

create index flow_to_idx on flow (to_site);

-- ------------------------------------------------------------- locales -----
-- Location inputs for any place on the map, keyed by ISO code as Mapbox
-- returns it: country by ISO 3166-1 alpha-2 ('US'), subdivision by full
-- ISO 3166-2 ('US-TX'). The app resolves subdivision -> country. Same shape
-- as data/locales.json; see docs/locale-contract.md.
--
-- ci   grid carbon intensity, gCO2/kWh    fos  fossil share of generation, 0-1
-- dec  annual decarbonisation rate, /yr   ws   water stress, 0-1
--      (negative when ci is rising)       pm25 annual mean PM2.5, µg/m³
-- wue  on-site water per kWh, L/kWh: climate estimate for a new site
-- wue_disclosed  an operator's own figure for its fleet or region there
--
-- Unknown values have no row; there are no nulls or placeholders.

create table country (
  iso2 text primary key check (iso2 ~ '^[A-Z]{2}$'),
  name text not null
);

create table country_value (
  country     text not null references country on delete cascade,
  key         text not null check (key in ('ci', 'fos', 'dec', 'ws', 'wue', 'wue_disclosed', 'pm25')),
  value       double precision not null check (key = 'dec' or value >= 0),
  confidence  confidence not null default 'sample',
  source_id   bigint references source on delete set null,
  year        smallint,
  basis       text,               -- 'generation', 'consumption', 'lifecycle', 'direct'
  note        text,
  primary key (country, key)
);

create table subdivision (
  code    text primary key check (code ~ '^[A-Z]{2}-[A-Z0-9]{1,3}$'),
  country text not null references country,
  name    text not null,
  check (left(code, 2) = country)
);

-- Subdivisions carry grid values only (ci, fos, dec) for now; ws follows.
create table subdivision_value (
  subdivision text not null references subdivision on delete cascade,
  key         text not null check (key in ('ci', 'fos', 'dec', 'ws', 'wue', 'wue_disclosed', 'pm25')),
  value       double precision not null check (key = 'dec' or value >= 0),
  confidence  confidence not null default 'sample',
  source_id   bigint references source on delete set null,
  year        smallint,
  basis       text,
  note        text,
  primary key (subdivision, key)
);

create index subdivision_country_idx on subdivision (country);

-- Postgres doesn't index foreign keys on its own; these keep deleting a
-- source cheap.
create index region_input_source_idx      on region_input      (source_id) where source_id is not null;
create index site_input_source_idx        on site_input        (source_id) where source_id is not null;
create index country_value_source_idx     on country_value     (source_id) where source_id is not null;
create index subdivision_value_source_idx on subdivision_value (source_id) where source_id is not null;

-- ------------------------------------------------------------ baseline -----
-- Everything the app needs to draw, as one JSON document shaped like the
-- constants in index.html. One request, no per-node queries.
--   regions:   {id: {n, ci, dec, wue, ws, fos, conf:{key: confidence}}}
--   sites:     [{id, n, p, s, c:[lon,lat], r, note, in:{...}, conf:{...}}]
--   cities:    candidate locations, same shape without s/in
--   flows:     [[from, to, share]]
--   countries, subdivisions, sources: as in data/locales.json, e.g.
--     countries: {US: {n, ci: {v, conf, src, year?, basis?, note?}, ...}}
--   Locale values only appear with a source and a confidence other than
--   'sample', as the contract requires.

create view atlas_baseline with (security_invoker = true) as
select jsonb_build_object(
  'regions', (
    select coalesce(jsonb_object_agg(r.id,
             jsonb_build_object('n', r.name) || coalesce(v.vals, '{}')
             || jsonb_build_object('conf', coalesce(v.conf, '{}'))), '{}')
    from region r
    left join lateral (
      select jsonb_object_agg(ri.key, ri.value)      as vals,
             jsonb_object_agg(ri.key, ri.confidence) as conf
      from region_input ri where ri.region_id = r.id
    ) v on true
  ),
  'sites', (
    select coalesce(jsonb_agg(
             jsonb_build_object('id', s.id, 'n', s.name, 'p', s.place, 's', s.stage,
                                'c', jsonb_build_array(s.lon, s.lat), 'r', s.region_id,
                                'note', s.note,
                                'in', coalesce(v.vals, '{}'), 'conf', coalesce(v.conf, '{}'))
             order by s.stage, s.id), '[]')
    from site s
    left join lateral (
      select jsonb_object_agg(si.key, si.value)      as vals,
             jsonb_object_agg(si.key, si.confidence) as conf
      from site_input si where si.site_id = s.id
    ) v on true
    where s.stage is not null
  ),
  'cities', (
    select coalesce(jsonb_agg(
             jsonb_build_object('id', s.id, 'n', s.name, 'p', s.place,
                                'c', jsonb_build_array(s.lon, s.lat), 'r', s.region_id)
             order by s.id), '[]')
    from site s where s.stage is null
  ),
  'flows', (
    select coalesce(jsonb_agg(jsonb_build_array(f.from_site, f.to_site, f.share)
             order by f.from_site, f.to_site), '[]')
    from flow f
  ),
  'countries', (
    select coalesce(jsonb_object_agg(c.iso2, jsonb_build_object('n', c.name) || coalesce(v.vals, '{}')), '{}')
    from country c
    left join lateral (
      select jsonb_object_agg(cv.key, jsonb_strip_nulls(jsonb_build_object(
               'v', cv.value, 'conf', cv.confidence, 'src', s.key,
               'year', cv.year, 'basis', cv.basis, 'note', cv.note))) as vals
      from country_value cv join source s on s.id = cv.source_id
      where cv.country = c.iso2 and cv.confidence <> 'sample' and s.key is not null
    ) v on true
  ),
  'subdivisions', (
    select coalesce(jsonb_object_agg(d.code, jsonb_build_object('n', d.name) || coalesce(v.vals, '{}')), '{}')
    from subdivision d
    left join lateral (
      select jsonb_object_agg(sv.key, jsonb_strip_nulls(jsonb_build_object(
               'v', sv.value, 'conf', sv.confidence, 'src', s.key,
               'year', sv.year, 'basis', sv.basis, 'note', sv.note))) as vals
      from subdivision_value sv join source s on s.id = sv.source_id
      where sv.subdivision = d.code and sv.confidence <> 'sample' and s.key is not null
    ) v on true
  ),
  'sources', (
    select coalesce(jsonb_object_agg(s.key, jsonb_strip_nulls(jsonb_build_object('title', s.title, 'url', s.url))), '{}')
    from source s where s.key is not null
  )
) as data;

-- ------------------------------------------------------ row-level security --
-- Anyone may read. No write policy exists, so only the service role (SQL
-- editor, migrations) can write.

alter table source        enable row level security;
alter table region        enable row level security;
alter table region_input  enable row level security;
alter table site          enable row level security;
alter table site_input    enable row level security;
alter table flow          enable row level security;
alter table country           enable row level security;
alter table country_value     enable row level security;
alter table subdivision       enable row level security;
alter table subdivision_value enable row level security;

create policy read_all on source        for select using (true);
create policy read_all on region        for select using (true);
create policy read_all on region_input  for select using (true);
create policy read_all on site          for select using (true);
create policy read_all on site_input    for select using (true);
create policy read_all on flow          for select using (true);
create policy read_all on country           for select using (true);
create policy read_all on country_value     for select using (true);
create policy read_all on subdivision       for select using (true);
create policy read_all on subdivision_value for select using (true);

grant select on atlas_baseline to anon;
