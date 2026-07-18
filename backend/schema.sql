-- ============================================================
-- BagMech Bengaluru — Supabase schema
-- Run this in Supabase SQL Editor (or `psql` against your DB)
-- ============================================================

-- Optional: keep everything in a dedicated schema if you like.
-- We use "public" here to keep it simple.

create extension if not exists "pgcrypto"; -- for gen_random_uuid()

-- ---------- ZONES ----------
create table if not exists public.zones (
    id           uuid primary key default gen_random_uuid(),
    name         text not null unique,
    eta_minutes  integer not null,
    is_far       boolean not null default false,
    created_at   timestamptz not null default now()
);

-- ---------- BOOKINGS ----------
create table if not exists public.bookings (
    id               uuid primary key default gen_random_uuid(),
    name             text not null,
    phone            text not null,
    zone_id          uuid not null references public.zones(id),
    address          text not null,
    issue            text not null,
    latitude         numeric(9,6),
    longitude        numeric(9,6),
    location_shared  boolean not null default false,
    status           text not null default 'pending'
                       check (status in ('pending','confirmed','in_progress','completed','cancelled')),
    created_at       timestamptz not null default now()
);

create index if not exists idx_bookings_zone_id on public.bookings(zone_id);
create index if not exists idx_bookings_status on public.bookings(status);
create index if not exists idx_bookings_created_at on public.bookings(created_at desc);

-- ---------- SEED ZONES (matches the zoneData in your HTML) ----------
insert into public.zones (name, eta_minutes, is_far) values
    ('Singasandra', 25, false),
    ('Begur', 25, false),
    ('Hosa Road', 25, false),
    ('Electronic City', 25, false),
    ('Kudlu Gate', 25, false),
    ('Somasandra Palya', 25, false),
    ('Choodasandra', 25, false),
    ('Kasavanahalli', 45, true),
    ('Bommanahalli', 25, false),
    ('HSR Layout', 25, false),
    ('Bellandur', 45, true),
    ('Silk Board', 25, false),
    ('BTM Layout', 25, false),
    ('JP Nagar', 45, true),
    ('Jayanagar', 25, false),
    ('MG Road', 45, true)
on conflict (name) do nothing;

-- ---------- ROW LEVEL SECURITY ----------
-- Enable RLS and only allow the backend (via service_role key) to write.
-- Public/anon key can read zones (needed if you ever call Supabase directly
-- from the browser), but bookings should only go through your API.
alter table public.zones enable row level security;
alter table public.bookings enable row level security;

create policy "Public can read zones"
    on public.zones for select
    using (true);

-- No insert/update/delete policies for anon/authenticated on bookings ->
-- only the service_role key (used by your backend, which bypasses RLS)
-- can write. This is intentional.