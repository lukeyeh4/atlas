-- AI Supply Chain Atlas — database schema (PostgreSQL 15+, written for Supabase)
--
-- The shared reference data now hard-coded in index.html (regions, sites,
-- flows, country layers), with per-value confidence and source so sourced
-- figures can replace the samples one value at a time.
--
-- There are no accounts. The public reads; only the maintainer writes, through
-- the Supabase dashboard or migrations. Visitors' own edits never reach the
-- database — they stay in the browser (localStorage, Export / Import).
--
-- The whole baseline is ~31 sites, ~25 regions and ~180 countries: the app
-- reads it in a single request through the `atlas_baseline` view and never
-- queries per node. See docs/database.md.

-- ---------------------------------------------------------------- types ----

create type stage as enum ('raw', 'chip', 'infra', 'model', 'delivery');

-- How much to trust a value. `sample` is everything the app ships with today.
create type confidence as enum ('measured', 'disclosed', 'estimated', 'projected', 'sample');

-- -------------------------------------------------------------- sources ----

create table source (
  id           bigint generated always as identity primary key,
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

-- ---------------------------------------------------- country layers -------
-- Values behind the map's choropleth layers, keyed by Natural Earth name.
-- ci grid carbon intensity gCO2/kWh · ws water stress 0-1 · aq air quality index

create table country_value (
  country     text not null,
  key         text not null check (key in ('ci', 'ws', 'aq')),
  value       double precision not null check (value >= 0),
  confidence  confidence not null default 'sample',
  source_id   bigint references source on delete set null,
  as_of       date,
  primary key (country, key)
);

-- Postgres doesn't index foreign keys on its own; these keep deleting a
-- source cheap.
create index region_input_source_idx  on region_input  (source_id) where source_id is not null;
create index site_input_source_idx    on site_input    (source_id) where source_id is not null;
create index country_value_source_idx on country_value (source_id) where source_id is not null;

-- ------------------------------------------------------------ baseline -----
-- Everything the app needs to draw, as one JSON document shaped like the
-- constants in index.html. One request, no per-node queries.
--   regions:   {id: {n, ci, dec, wue, ws, fos, conf:{key: confidence}}}
--   sites:     [{id, n, p, s, c:[lon,lat], r, note, in:{...}, conf:{...}}]
--   cities:    candidate locations, same shape without s/in
--   flows:     [[from, to, share]]
--   countries: {name: [ci, ws, aq]}

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
    select coalesce(jsonb_object_agg(c.country, c.vals), '{}')
    from (
      select country,
             jsonb_build_array(
               max(value) filter (where key = 'ci'),
               max(value) filter (where key = 'ws'),
               max(value) filter (where key = 'aq')) as vals
      from country_value group by country
    ) c
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
alter table country_value enable row level security;

create policy read_all on source        for select using (true);
create policy read_all on region        for select using (true);
create policy read_all on region_input  for select using (true);
create policy read_all on site          for select using (true);
create policy read_all on site_input    for select using (true);
create policy read_all on flow          for select using (true);
create policy read_all on country_value for select using (true);

grant select on atlas_baseline to anon;
