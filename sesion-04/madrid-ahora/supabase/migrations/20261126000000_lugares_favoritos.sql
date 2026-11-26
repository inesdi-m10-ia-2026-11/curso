-- Los lugares favoritos de cada usuario de Madrid ahora (versión Supabase).
-- La RLS hace que cada usuario vea y toque solo sus filas, también a través del MCP.

create table public.lugares_favoritos (
  id bigint generated always as identity primary key,
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  nombre text not null check (char_length(nombre) between 2 and 80),
  creado timestamptz not null default now(),
  unique (user_id, nombre)
);

alter table public.lugares_favoritos enable row level security;

create policy "Cada usuario lee sus lugares"
  on public.lugares_favoritos for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "Cada usuario guarda sus lugares"
  on public.lugares_favoritos for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy "Cada usuario borra sus lugares"
  on public.lugares_favoritos for delete to authenticated
  using ((select auth.uid()) = user_id);

grant select, insert, delete on public.lugares_favoritos to authenticated;
