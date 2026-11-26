-- RAG en tu Supabase (extra de la sesión 4): la tabla de trozos y la búsqueda por parecido.
--
-- Dónde: en el panel de tu proyecto, SQL Editor, New query. Pégalo entero y pulsa Run.
-- Se puede ejecutar más de una vez sin romper nada.
--
-- Una regla que no se cambia: 768 dimensiones. Es el tamaño de vector que piden
-- cargar_textos.py y tu MCP a gemini-embedding-2 (output_dimensionality = 768).
-- Si cambias el número aquí, cámbialo en los tres sitios; si no, todo da
-- "expected 768 dimensions, not ...".
--
-- Sigue la documentación de Supabase del 26/11/2026:
--   https://supabase.com/docs/guides/ai/vector-columns
--   https://supabase.com/docs/guides/ai/semantic-search
--   https://supabase.com/docs/guides/ai/vector-indexes/hnsw-indexes
--   https://supabase.com/docs/guides/api/securing-your-api (grants y RLS)


-- 1. La extensión pgvector. En Supabase se llama "vector" y va en el esquema extensions.
--    (Es lo mismo que Database, Extensions, buscar "vector" y activarla.)
create extension if not exists vector with schema extensions;


-- 2. La tabla: un trozo de texto por fila, con su fuente y su vector.
create table if not exists public.trozos (
  id bigint primary key generated always as identity,
  fuente text not null,     -- el documento, como lo citarías: "Guía de alquiler, Ministerio de Vivienda (2025)"
  pagina int,               -- la página del PDF de donde sale el trozo (vacía en .txt y .md)
  posicion int not null,    -- el número del trozo dentro de su documento: 0, 1, 2...
  url text,                 -- dónde se puede leer el original
  licencia text,            -- con qué licencia lo usas: "CC BY 4.0", "reutilización de información pública"...
  texto text not null,      -- el trozo, unos 800 caracteres
  embedding extensions.vector(768) not null,
  creado_en timestamptz not null default now(),
  unique (fuente, posicion)
);


-- 3. El índice para buscar por parecido (HNSW con distancia coseno, el que recomienda
--    Supabase). Con unos cientos de trozos no se nota; con miles, sí.
create index if not exists trozos_embedding_idx
  on public.trozos using hnsw (embedding extensions.vector_cosine_ops);


-- 4. Quién puede qué. Leer, cualquiera (los textos son públicos: por eso los elegiste
--    con una licencia que lo permite). Escribir, solo tu script de carga, con una
--    clave secreta que no sale de tu terminal.
alter table public.trozos enable row level security;

revoke all on table public.trozos from anon, authenticated;
grant select on table public.trozos to anon, authenticated;
grant select, insert, update, delete on table public.trozos to service_role;

drop policy if exists "Los trozos se leen sin login" on public.trozos;
create policy "Los trozos se leen sin login" on public.trozos
  for select to anon, authenticated
  using (true);


-- 5. La búsqueda: los trozos más parecidos a la pregunta, del más al menos parecido.
--    Tu MCP la llama por la API de Supabase (/rest/v1/rpc/buscar_trozos) con la clave
--    publicable. "parecido" va de -1 a 1: cuanto más cerca de 1, más se parece.
--    security invoker: se ejecuta con los permisos de quien llama, así que la RLS de
--    arriba se aplica también aquí.
create or replace function public.buscar_trozos(
  pregunta_embedding extensions.vector(768),
  cuantos int default 5
)
returns table (
  fuente text,
  pagina int,
  posicion int,
  url text,
  texto text,
  parecido double precision
)
language sql
stable
security invoker
set search_path = public, extensions
as $$
  select
    t.fuente,
    t.pagina,
    t.posicion,
    t.url,
    t.texto,
    1 - (t.embedding <=> pregunta_embedding) as parecido
  from public.trozos as t
  order by t.embedding <=> pregunta_embedding
  limit least(greatest(cuantos, 1), 20);
$$;

revoke execute on function public.buscar_trozos(extensions.vector, int) from public;
grant execute on function public.buscar_trozos(extensions.vector, int) to anon, authenticated, service_role;


-- 6. Que la API de Supabase vea la función nueva ya (si no, puede tardar un poco y dar
--    "Could not find the function public.buscar_trozos in the schema cache").
notify pgrst, 'reload schema';


-- Para comprobar después de cargar tus textos (pégalas una a una):
--   select fuente, count(*) as trozos, min(pagina), max(pagina) from public.trozos group by fuente;
--   select vector_dims(embedding) from public.trozos limit 1;    -- tiene que decir 768
