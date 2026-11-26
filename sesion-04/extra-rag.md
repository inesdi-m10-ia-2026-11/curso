# Extra de la sesión 4: RAG servido por tu MCP

Módulo 10 · Sesión 4 · jueves 26/11/2026 · para quien ya tiene el hito de hoy (parte 5 de `tu-mcp.md`)

> **Si tienes dudas con este reto, pregunta al docente.** El documento está pensado para hacerlo de principio a fin sin ayuda, pero veinte minutos atascado en un error no enseñan nada: pregunta antes.

**Hecho** = tu agente responde una pregunta sobre un texto de tu tema llamando a una herramienta nueva de tu MCP, `buscar_en_textos`, y cita la fuente y la página del trozo que usa. Para las cifras sigue usando tus herramientas de datos, y tú tienes la prueba de que elige bien.

Es la versión completa del **reto 3 (RAG mínimo)** de `tu-mcp.md`. Es ambicioso: entre 90 y 120 minutos.

| Paso | Qué | Dónde | Tiempo |
|---|---|---|---|
| 1 | Qué es RAG y en qué se diferencia de tu MCP | Aquí | 5 min |
| 2 | Eliges un texto de tu tema | El navegador | 10 a 15 min |
| 3 | La base de datos de vectores, en tu Supabase | SQL Editor | 10 a 15 min |
| 4 | Tu clave de Gemini para los vectores | AI Studio y tu terminal | 5 a 10 min |
| 5 | Troceas y cargas el texto: lo organiza tu agente, la carga la lanzas tú | Tu agente y tu terminal | 20 a 25 min |
| 6 | `buscar_en_textos` en tu MCP | Tu agente y Render | 20 a 25 min |
| 7 | La prueba: diez preguntas tuyas y una que necesita las dos cosas | Tu agente | 20 min |
| 8 | "Hecho cuando" y tu decisión | Tu cuaderno | 5 min |

**Lo que necesitas antes de empezar:** tu MCP en Render con token, funcionando con tu agente (partes 3 a 5); tu proyecto de Supabase; Python en tu portátil (el de la sesión 3); y tu cuenta de Google para AI Studio, la misma que necesitas para el lunes. Si hiciste la parte 7 (tu MCP en una Edge Function de Supabase), el paso 6 tiene también ese camino.

Los archivos de apoyo están en el repo `curso`, en [`sesion-04/extra-rag/`](extra-rag/): `trozos.sql`, `cargar_textos.py`, `herramienta_textos.py` (para tu MCP de Render) y `herramienta_textos.ts` (para tu MCP en Supabase). Tu agente los descarga; tú no tienes que copiar nada a mano.

---

## 1. Qué es RAG (5 minutos)

**RAG** es *retrieval augmented generation*: generación aumentada con recuperación. Un modelo de lenguaje no ha leído el informe de tu sector; si le preguntas por él, se lo inventa con mucha seguridad. RAG lo arregla en dos tiempos:

- **Una vez, antes:** troceas el texto, calculas un **vector** (un *embedding*) para cada trozo y lo guardas todo en una base de datos. El vector es una lista de números (aquí, 768) que resume de qué habla el trozo. Dos trozos que dicen cosas parecidas tienen vectores cercanos, aunque usen palabras distintas: "fianza" y "depósito" quedan cerca.
- **En cada pregunta:** calculas el vector de la pregunta, buscas los trozos con el vector más cercano y se los das al modelo, que responde con ellos y dice de dónde salen.

```text
UNA VEZ, en tu terminal
  informe.pdf -> trozos de ~800 caracteres -> Gemini: un vector por trozo -> Supabase: tabla trozos (pgvector)

EN CADA PREGUNTA, en tu MCP
  "¿qué dice el informe sobre X?"
     -> Gemini: el vector de la pregunta (el mismo modelo)
     -> Supabase: los 5 trozos más parecidos (función buscar_trozos)
     -> tu agente responde con esos trozos y cita fuente y página
```

Aquí la búsqueda es **una herramienta de tu MCP**: tu agente decide cuándo llamarla, igual que decide cuándo llamar a `buscar_X`. Eso es lo que vas a medir en el paso 7.

**¿MCP con filas exactas o RAG?** Es la idea 5 de hoy:

| Pregunta | Herramienta | Por qué |
|---|---|---|
| ¿Cuántas filas de mi tabla son de 2025? | `buscar_X` (filas exactas) | Un filtro y una cuenta: la cuenta la hace el código, no el modelo |
| ¿Qué dice el informe sobre cómo se mide X? | `buscar_en_textos` (RAG) | Una pregunta a un texto: no hay columna que filtrar |
| ¿Cuánto predice mi modelo para este caso? | `predecir_Y` | Un cálculo de tu modelo |

Dos límites de RAG que conviene tener claros desde ya:

- **RAG no cuenta ni suma.** Devuelve los 5 trozos más parecidos, no todos los que hablan de algo. "¿Cuántas veces menciona el informe a Madrid?" no se responde bien con RAG.
- **RAG encuentra lo parecido, no lo verdadero.** Si el texto no dice nada de tu pregunta, salen igualmente los 5 trozos "menos lejanos". Por eso tu herramienta devuelve un *parecido* y su descripción pide decir "el texto no lo dice" en lugar de completar de memoria.

---

## 2. Elige tu texto (10 a 15 minutos)

Un texto que responda preguntas que **tus datos no responden**: normas, definiciones, metodología, recomendaciones, contexto. Ideas:

- **La metodología de tus datos:** el documento que explica cómo se recogieron, qué significa cada columna y qué no incluyen. Suele estar en el mismo portal que tu CSV y es el que más preguntas responde sobre tu proyecto.
- Un informe anual o una guía de un organismo público de tu tema.
- Una normativa o una guía de buenas prácticas de tu sector.
- Las preguntas frecuentes de un servicio público relacionado.

Cuatro condiciones:

1. **De 10 a 30 páginas.** Con menos, apenas hay dónde buscar; con más, la carga tarda y gastas cuota gratuita.
2. **Con texto de verdad.** Un PDF del que se puede copiar texto: ábrelo y selecciona una frase. Si no se deja, es un PDF escaneado (fotos de páginas) y no sirve. También valen `.txt` y `.md`: una página web copiada a un `.md` vale si su licencia lo permite.
3. **Con una licencia que lo permita**, y apúntala: CC BY o CC BY-SA, dominio público, o reutilización de información del sector público (en España, la mayoría de webs de la Administración lo dicen en su aviso legal; en `datos.gob.es` viene en cada conjunto). Si no encuentras la licencia, elige otro texto.
4. **Público y sin datos personales.** Con la clave gratuita de AI Studio, Google puede usar lo que le mandas para mejorar sus productos (lo dice su página de precios, https://aistudio.google.com/docs/pricing). Nada confidencial, nada de clientes, nada tuyo que no publicarías.

Gemini entiende más de 100 idiomas: el texto puede estar en español o en inglés. Si está en inglés y preguntas en español, apunta en el paso 7 si encuentra igual de bien (no está probado).

**Hecho:** en `decisiones.md`, una entrada con la fecha de hoy: título, quién lo publica, año, URL, licencia, número de páginas y dos preguntas de tu proyecto que ese texto responde y tus datos no.

---

## 3. La base de datos de vectores, en tu Supabase (10 a 15 minutos)

No necesitas otra base de datos: Postgres guarda vectores con la extensión **pgvector**, que en Supabase se llama `vector`. Supabase lo resume así en su guía de IA: "the best vector database is the database you already have" (https://supabase.com/docs/guides/ai).

Todo está en un archivo, [`extra-rag/trozos.sql`](extra-rag/trozos.sql), que sigue la documentación actual de Supabase (vector columns, semantic search, HNSW indexes y securing your API). Hace cinco cosas:

| # | Qué | Para qué |
|---|---|---|
| 1 | Activa `vector` en el esquema `extensions` | Es lo mismo que Database, Extensions, buscar "vector" y activarla |
| 2 | Crea la tabla `trozos`: `fuente`, `pagina`, `posicion`, `url`, `licencia`, `texto` y `embedding vector(768)` | Un trozo por fila, con lo necesario para citarlo |
| 3 | Un índice HNSW con distancia coseno | Que la búsqueda siga siendo rápida si un día tienes miles de trozos |
| 4 | RLS: leer, cualquiera (con la clave publicable o con login); escribir, solo una clave secreta | Los textos son públicos (por eso elegiste uno con licencia). Escribir solo puede tu carga del paso 5 |
| 5 | La función `buscar_trozos(pregunta_embedding, cuantos)` | Devuelve los trozos más parecidos a un vector, con su `parecido` (más cerca de 1, más se parece). La API de Supabase no sabe comparar vectores: por eso se busca con una función |

Pasos:

1. En el panel de tu proyecto de Supabase: **SQL Editor, New query**.
2. Abre [`trozos.sql`](https://github.com/inesdi-m10-ia-2026-11/curso/blob/main/sesion-04/extra-rag/trozos.sql), cópialo entero, pégalo y pulsa **Run**. Se puede ejecutar más de una vez sin romper nada.
3. Comprueba, en otra query:

```sql
select count(*) from trozos;
```

Tiene que dar `0`, sin error. Y en **Database, Functions** aparece `buscar_trozos`.

**La regla de las 768.** El vector de cada trozo y el de cada pregunta tienen que salir del **mismo modelo** y con el **mismo número de dimensiones**: 768. Está escrito en tres sitios (`trozos.sql`, `cargar_textos.py` y tu MCP). Si cambias uno, cambias los tres y vuelves a cargar todo.

**Hecho:** `select count(*) from trozos;` da 0 y `buscar_trozos` aparece en Database, Functions.

---

## 4. Embeddings: tu clave de Gemini (5 a 10 minutos)

**Qué modelo y por qué.** Supabase trae un modelo de embeddings sin clave dentro de sus Edge Functions, `gte-small` (`new Supabase.ai.Session('gte-small')`, en https://supabase.com/docs/guides/ai/quickstarts/generate-text-embeddings). Sigue en su documentación, pero no lo usamos por dos razones: su ficha dice que "exclusively caters to English texts" y corta los textos largos a 512 tokens (https://huggingface.co/thenlper/gte-small), y además te obligaría a publicar una Edge Function solo para calcular vectores, también los de cada pregunta de tu MCP de Render.

Usamos **`gemini-embedding-2`**, el modelo de embeddings actual de la API de Gemini (https://aistudio.google.com/docs/embeddings): más de 100 idiomas, gratis con la clave de AI Studio que necesitas para el lunes, y 768 dimensiones que Gemini ya devuelve normalizadas. Dos detalles que los archivos de apoyo ya resuelven (y por eso tu agente no los debe "arreglar"):

- `gemini-embedding-2` **no acepta `task_type`**. Lo que es un documento y lo que es una pregunta va escrito dentro del texto: `title: <fuente> | text: <trozo>` para los trozos y `task: question answering | query: <pregunta>` para las preguntas.
- Si le pasas varios textos en una sola petición `embedContent`, devuelve **un** vector para todos juntos. La carga usa `batchEmbedContents`: un vector por trozo.

**Tu clave:**

1. Entra en https://aistudio.google.com/apikey con tu cuenta de Google y pulsa **Create API key** (si ya la tienes para el lunes, usa esa).
2. Guárdala en tu gestor de contraseñas como "clave de AI Studio". No va a ningún archivo, a ningún repo ni a ningún chat, tampoco al de tu agente.

**Compruébala** en una terminal (déjala abierta: la usas en el paso 5). Tiene que escribir `768`.

**Mac, Linux o Git Bash** (en Git Bash, `py` en lugar de `python3`):

```bash
read -s -p "Pega tu clave de AI Studio y pulsa Enter (no se verá): " GEMINI_API_KEY; echo; export GEMINI_API_KEY
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" -H "Content-Type: application/json" \
  -d '{"content":{"parts":[{"text":"hola"}]},"output_dimensionality":768}' \
  | python3 -c "import sys, json; print(len(json.load(sys.stdin)['embedding']['values']))"
```

**Windows PowerShell** (la clave se ve al pegarla: que nadie mire tu pantalla):

```powershell
$env:GEMINI_API_KEY = Read-Host "Pega tu clave de AI Studio"
$cuerpo = '{"content":{"parts":[{"text":"hola"}]},"output_dimensionality":768}'
$r = Invoke-RestMethod -Method Post -Uri "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent" -Headers @{ "x-goog-api-key" = $env:GEMINI_API_KEY } -ContentType "application/json" -Body $cuerpo
$r.embedding.values.Count
```

Si sale un error en lugar de `768`, mira "Si algo falla" al final.

**Hecho:** la terminal escribe `768`.

---

## 5. Trocear y cargar, con tu agente (20 a 25 minutos)

**Trocear** es cortar el texto en pedazos que se buscan por separado. Las decisiones de `cargar_textos.py`, y por qué:

- **Unos 800 caracteres por trozo** (uno o dos párrafos). Más pequeños, cada trozo pierde contexto; más grandes, mezclan temas y el parecido con una pregunta concreta se diluye.
- **150 caracteres de solape:** el final de un trozo se repite al principio del siguiente. Una frase que cae en el borde sale entera en uno de los dos.
- **Corta donde menos duele:** primero en un final de párrafo, si no en un final de frase, y solo en último caso en un espacio. Nunca en mitad de una palabra.
- **Cada trozo de un PDF sabe su página**, y todos llevan su fuente: así tu agente puede citar "(Informe X, página 12)" y tú comprobarlo.

Tu agente organiza el trabajo: descarga el script, lo adapta a tu texto, lo ejecuta en **modo prueba** (trocea y enseña cifras, sin claves ni llamadas) y te enseña trozos para que decidas si están bien. **La carga de verdad la lanzas tú**, en tu terminal: así ninguna clave pasa por el chat ni por la terminal de tu agente.

Todo va en una carpeta nueva del repo de tu app, `apps/<tu-app>/rag/`, fuera de `modelo/` (Render no la necesita). Copia tu PDF a `apps/<tu-app>/rag/textos/` y pega esto en tu agente, abierto en la carpeta de tu cuaderno, como siempre:

```text
Lee arquitectura.md y la entrada de hoy en decisiones.md (mi texto para el
RAG). Vamos a cargar mi texto en Supabase para buscar en él por parecido.
Trabaja en apps/<mi-app>/rag/.

1. Descarga cargar_textos.py y trozos.sql de
   https://github.com/inesdi-m10-ia-2026-11/curso/tree/main/sesion-04/extra-rag
   (las versiones raw) y léelos enteros. Explícame en cinco frases cómo
   trocea cargar_textos.py: tamaño, solape, dónde corta y qué guarda de
   cada trozo.
2. Mi texto está en apps/<mi-app>/rag/textos/. Rellena DOCUMENTOS con su
   fuente (título, quién lo publica y año), su URL y su licencia, sacadas
   de decisiones.md.
3. Reglas: no cambies MODELO, DIMENSIONES ni la forma de llamar a Gemini
   (batchEmbedContents, sin task_type): el propio archivo explica por qué.
   Ninguna clave en ningún archivo ni en este chat. Añade rag/textos/ y
   rag/.venv/ al .gitignore del repo de mi app.
4. Crea un entorno .venv en rag/, instala httpx==0.28.1 y pypdf y ejecuta
   python cargar_textos.py --probar. Si estoy en Windows, dame los comandos
   en PowerShell. Enséñame cuántos trozos salen y de qué tamaño, y tres
   trozos enteros: uno del principio, uno del medio y uno del final.
5. Si algún trozo sale roto (palabras pegadas, tablas deshechas, la misma
   cabecera de página repetida en todos), proponme un arreglo en limpiar()
   y repite el punto 4. No cambies TAMANO ni SOLAPE sin preguntarme.
6. No ejecutes la carga de verdad: la lanzo yo en mi terminal, con las
   claves. Dime los comandos exactos para mi sistema.
7. Commit en el repo de mi app. Todavía no hagas push.
```

**Mira tú los tres trozos.** ¿Se entienden solos? ¿Sabrías decir de qué habla cada uno? Si tú no lo sabes, la búsqueda tampoco. Un PDF a dos columnas o con muchas tablas puede salir desordenado: si es tu caso, busca la versión web del mismo texto y guárdala como `.md`.

### La carga, en tu terminal

**1. Una clave secreta solo para esta carga.** Escribir en `trozos` necesita una clave secreta: la RLS no deja escribir con la publicable, y está bien que no deje. En Supabase: **Project Settings, API Keys**. En el apartado de las claves secretas, crea una nueva (**New secret key**) con el nombre `carga-rag` y cópiala: empieza por `sb_secret_`. La borras en cuanto termines.

**2. Los comandos** (los mismos que te ha dado tu agente; si no coinciden, pregúntale por qué). La URL de tu proyecto está en tu `urls.md`.

**Mac, Linux o Git Bash:**

```bash
cd apps/<tu-app>/rag
source .venv/bin/activate
read -s -p "Clave de AI Studio: " GEMINI_API_KEY; echo; export GEMINI_API_KEY
read -s -p "Clave secreta de Supabase (sb_secret_...): " SUPABASE_SECRET_KEY; echo; export SUPABASE_SECRET_KEY
export SUPABASE_URL="https://<ref de tu proyecto>.supabase.co"
python cargar_textos.py
```

En Git Bash en Windows, el entorno se activa con `source .venv/Scripts/activate`.

**Windows PowerShell** (las claves se ven al pegarlas):

```powershell
cd apps\<tu-app>\rag
.venv\Scripts\Activate.ps1
$env:GEMINI_API_KEY = Read-Host "Clave de AI Studio"
$env:SUPABASE_SECRET_KEY = Read-Host "Clave secreta de Supabase (sb_secret_...)"
$env:SUPABASE_URL = "https://<ref de tu proyecto>.supabase.co"
python cargar_textos.py
```

Verás una línea por cada 20 trozos (`vectores: 40 de 120`) y, al final, **Todo bien: N trozos en la tabla trozos**. Si Gemini dice 429 (demasiadas peticiones), el script espera y repite solo. Si vuelves a ejecutarlo, primero borra los trozos viejos de cada documento: nunca hay duplicados.

**3. Compruébalo** en el SQL Editor, una query cada vez:

```sql
select fuente, count(*) as trozos, min(pagina), max(pagina) from trozos group by fuente;
```

```sql
select vector_dims(embedding) from trozos limit 1;
```

La primera tiene que dar el mismo número de trozos que el modo prueba; la segunda, `768`.

**4. Borra la clave `carga-rag`** en Project Settings, API Keys, y cierra esa terminal (las variables se van con ella). Si un día vuelves a cargar, creas otra.

**Hecho:** en el SQL Editor, tu fuente con sus N trozos y `vector_dims` igual a 768; la clave `carga-rag` ya no está en Project Settings, API Keys; y en el repo de tu app, el commit con `rag/cargar_textos.py` y sin el PDF.

---

## 6. `buscar_en_textos` en tu MCP (20 a 25 minutos)

La herramienta hace tres cosas: calcula el vector de la pregunta con el mismo modelo y las mismas 768 dimensiones; llama a `buscar_trozos` con la clave **publicable** (la misma de siempre: los textos se pueden leer sin login); y devuelve los trozos con su fuente, su página y su parecido.

Lo más importante es, otra vez, **la descripción**: tiene que decir qué documento hay detrás y cuándo usar esta herramienta en lugar de las de datos. Si dice "Busca en documentos", tu agente no sabrá cuándo llamarla.

### Camino A: tu MCP de Render (el de las partes 3 a 5)

Pega esto en tu agente:

```text
Lee modelo/servidor_mcp.py del repo de mi app y la entrada de hoy en
decisiones.md (mi texto). Vamos a añadir a mi MCP una tercera herramienta,
buscar_en_textos, que busca en los trozos de mi texto que ya están en
Supabase (tabla trozos, función buscar_trozos).

1. Descarga herramienta_textos.py de
   https://github.com/inesdi-m10-ia-2026-11/curso/tree/main/sesion-04/extra-rag
   (la versión raw) y léelo entero. Pega su bloque en modelo/servidor_mcp.py
   donde el propio archivo dice.
2. Rellena lo marcado con CAMBIA: en el docstring, qué documento es
   (título, quién lo publica, año) y para qué preguntas sirve; el ejemplo
   de pregunta; y los nombres reales de mis otras herramientas. Añade una
   frase a las instructions de MCPServer: qué texto hay y cuándo usar
   buscar_en_textos y cuándo mis herramientas de datos. Enséñame las
   descripciones antes de seguir y espera a que te diga que sí.
3. Reglas: mcp==2.3.0 y MCPServer, no FastMCP. La clave de Supabase sigue
   siendo la PUBLICABLE. GEMINI_API_KEY solo como variable de entorno: ni
   en el código ni en un .env del repo.
4. En PRUEBAS de probar_mcp.py, una llamada a buscar_en_textos con una
   pregunta que mi texto responde.
5. Dime los comandos para probarlo en local con GEMINI_API_KEY en mi
   terminal (no me pidas la clave). Si estoy en Windows, en PowerShell.
6. Commit en el repo de mi app. Todavía no hagas push.
```

**Pruébalo en local**, en dos terminales, en `modelo/` de tu app.

**Mac, Linux o Git Bash.** Terminal 1:

```bash
source .venv/bin/activate
export MCP_TOKEN=prueba-local
read -s -p "Clave de AI Studio: " GEMINI_API_KEY; echo; export GEMINI_API_KEY
uvicorn main:app --reload
```

Terminal 2:

```bash
source .venv/bin/activate
MCP_URL=http://localhost:8000/mcp MCP_TOKEN=prueba-local python probar_mcp.py
```

En Git Bash en Windows: `source .venv/Scripts/activate`.

**Windows PowerShell.** Terminal 1:

```powershell
.venv\Scripts\Activate.ps1
$env:MCP_TOKEN = "prueba-local"
$env:GEMINI_API_KEY = Read-Host "Clave de AI Studio"
uvicorn main:app --reload
```

Terminal 2:

```powershell
.venv\Scripts\Activate.ps1
$env:MCP_URL = "http://localhost:8000/mcp"
$env:MCP_TOKEN = "prueba-local"
python probar_mcp.py
```

`probar_mcp.py` enseña la descripción de `buscar_en_textos` tal como la leerá la IA y la llama: tienen que salir trozos con `fuente`, `pagina`, `texto` y `parecido`, y la última línea, **Todo bien**.

**A Render:**

1. En tu servicio del modelo: **Environment, Add Environment Variable**, `GEMINI_API_KEY` con tu clave de AI Studio. **Save.**
2. Push del repo de tu app (y del cuaderno, como siempre). Espera a que esté "live".
3. Abre tu `/health` (`{"ok":true}`) y tu `/mcp` (el `401` de siempre: vivo y protegido).
4. Cierra tu agente y ábrelo otra vez. Con `/mcp` (o la lista de tu agente) tienes que ver tres herramientas.

### Camino B: tu MCP en Supabase con login (si hiciste la parte 7)

La búsqueda va con el token de quien llama: `trozos.sql` deja leer también al rol `authenticated`, así que funciona igual.

1. **El secreto:** en el panel de Supabase, **Edge Functions, Secrets** (https://supabase.com/dashboard/project/_/functions/secrets), añade `GEMINI_API_KEY` con tu clave de AI Studio y **Save**. No hace falta volver a desplegar para que la función lo lea. No uses `supabase secrets set` con la clave en el comando: se quedaría en el historial de tu terminal.
2. **El código:** pega esto en tu agente:

```text
Lee apps/<mi-app>/supabase/functions/mcp/index.ts y la entrada de hoy en
decisiones.md (mi texto). Vamos a añadir a esa función la herramienta
buscar_en_textos, que busca en los trozos de mi texto (tabla trozos,
función buscar_trozos).

1. Descarga herramienta_textos.ts de
   https://github.com/inesdi-m10-ia-2026-11/curso/tree/main/sesion-04/extra-rag
   (la versión raw) y léelo entero. Tiene dos trozos: pega cada uno donde
   dice.
2. Rellena lo marcado con CAMBIA (qué documento es y para qué preguntas
   sirve, y el ejemplo de pregunta) y añade una frase a las instructions
   del McpServer. Enséñame la descripción y espera a que te diga que sí.
3. Reglas: las mismas importaciones y versiones que ya tiene el archivo.
   Usa la constante supabase de crearServidor (ctx.supabase), nunca la
   clave secreta. GEMINI_API_KEY se lee con Deno.env.get: ni en el código
   ni en un .env.
4. No despliegues nada. Commit en el repo de mi app, sin push.
```

3. **Publícala**, en `apps/<tu-app>` (igual en los dos sistemas):

```bash
supabase functions deploy mcp --use-api
```

4. **Pruébala** con el token del usuario A, como en la 7a (si ha caducado, vuelve a pedirlo con los mismos comandos). Cambia la pregunta por una que tu texto responde.

**Mac, Linux o Git Bash:**

```bash
curl -s -X POST "$MCP_URL" \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"buscar_en_textos","arguments":{"pregunta":"<una pregunta que tu texto responde>","cuantos":2}}}'
```

**Windows PowerShell** (con `charset=utf-8`, para que las tildes de la pregunta lleguen bien en Windows PowerShell 5.1):

```powershell
$pregunta = '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"buscar_en_textos","arguments":{"pregunta":"<una pregunta que tu texto responde>","cuantos":2}}}'
Invoke-RestMethod -Method Post -Uri $env:MCP_URL -Headers @{ Authorization = "Bearer $env:TOKEN_A"; Accept = "application/json, text/event-stream" } -ContentType "application/json; charset=utf-8" -Body $pregunta
```

Los trozos están dentro de `"text"`.

**Hecho (camino A o B):** `probar_mcp.py` (o la llamada con `curl`) devuelve trozos de tu texto con su fuente y su página, y tu agente ve `buscar_en_textos` junto a tus otras herramientas.

---

## 7. La prueba: ¿elige bien tu agente? (20 minutos)

Que la búsqueda funcione ya lo sabes. Lo que importa es si tu agente **elige** bien: texto cuando la respuesta está en el texto, datos cuando está en tus datos.

1. **Escribe tú diez preguntas** (no tu agente), en `decisiones.md`: cinco que solo responde el texto y cinco que solo responden tus datos o tu modelo. Para cada pregunta de texto, busca antes en el PDF dónde está la respuesta y apunta la página: así sabrás si cita el trozo correcto.
2. **Cada una en una conversación nueva** (en OpenCode y Codex, `/new`; en Claude Code, `/clear`), con esta coletilla:

```text
<tu pregunta>. Después dime qué herramientas has llamado, con qué
argumentos, y de qué fuente y página sale cada dato de tu respuesta.
```

3. **Apunta cada resultado** en la tabla (copia la plantilla):

```text
| # | Pregunta | Está en | Herramienta esperada | Herramienta llamada | Página esperada | Página citada | Acierto |
|---|---|---|---|---|---|---|---|
| 1 | ... | texto | buscar_en_textos | buscar_en_textos | 12 | 12 | sí |
| 6 | ... | datos | buscar_X | buscar_en_textos | no aplica | 4 | no |
```

Una pregunta de texto es acierto si llamó a `buscar_en_textos` y citó la página buena. Una de datos es acierto si llamó a tu herramienta de datos y no sacó la cifra de un trozo de texto.

4. **Si falla alguna**, antes de tocar código, mira las descripciones (es el escalón 1 de hoy): ¿dice `buscar_en_textos` qué documento hay detrás y que no sirve para cifras? ¿Dice `buscar_X` que es para filas y recuentos? Cambia, despliega y repite solo las que fallaron.
5. **Una pregunta que necesita las dos cosas**, en otra conversación nueva. Por ejemplo, con un texto de metodología: "según la metodología, ¿qué cuenta como X? ¿Cuántas filas de mis datos cumplen eso en 2024?". Apunta en tu bitácora las herramientas llamadas, en orden, y la respuesta.

**Si cita mal la página:** mira el `parecido` del primer trozo. Si es bajo comparado con el de tus otras preguntas, es probable que el texto no lo diga con esas palabras; si es alto y aun así cita otra página, el problema está en cómo responde: pide en la descripción "cita solo la fuente y la página del trozo que usas".

---

## 8. Hecho cuando

*Hecho cuando:* en `decisiones.md` está la tabla de las diez preguntas que escribiste tú, cada una en una conversación nueva (cinco de texto y cinco de datos), con la herramienta que eligió tu agente, si citó la página correcta y la nota (por ejemplo, 8 de 10); para cada fallo, por qué crees que se equivocó, qué cambiaste y la nota después del cambio. En tu bitácora, la pregunta que necesita las dos cosas, con las herramientas llamadas en orden y la respuesta citando fuente y página. Y tu decisión, con su razón:

```text
## 26/11/2026 · RAG en mi MCP
Texto: <título>, <quién lo publica> (<año>). <licencia>. <URL>. <N> trozos.
Nota: <x> de 10 (texto: <a> de 5; datos: <b> de 5). Tras los cambios: <y> de 10.
Qué cambié: <la descripción de ..., las instructions, ...>.
Decisión: <me quedo con buscar_en_textos / la quito>, porque <qué gana o pierde mi usuario>.
Lo que no resuelve: <por ejemplo, contar cuántas veces sale algo en el texto>.
```

Enséñale la pregunta de las dos cosas a un compañero en tu agente, en directo. Si te lo pide el docente, es la que se proyecta.

---

## 9. Si algo falla

| Qué ves | Qué pasa | Qué hacer |
|---|---|---|
| **En Supabase** | | |
| `type "vector" does not exist` | La extensión no está activada | Vuelve a ejecutar `trozos.sql` entero: el paso 1 la activa |
| `expected 768 dimensions, not 3072` o `different vector dimensions 3072 and 768` | Algún sitio pide el vector sin `output_dimensionality: 768` (Gemini da 3072 por defecto) | No cambies `DIMENSIONES` ni la llamada a Gemini. Si tu agente reescribió algo, que lo compare con los archivos del curso |
| `Could not find the table 'public.trozos'` o `Could not find the function public.buscar_trozos` | No has ejecutado `trozos.sql` en este proyecto, o la API aún no lo ha visto | Ejecuta `trozos.sql` otra vez (al final avisa a la API) y espera un minuto. Comprueba también que la URL es la de este proyecto |
| `permission denied for table trozos` (código `42501`) | Falta el permiso de leer o escribir | Al cargar: usas la clave publicable, usa una secreta. Al buscar: ejecuta otra vez `trozos.sql` (el paso 4 da los permisos) |
| Trozos repetidos de un mismo texto | Cambiaste la `fuente` en `DOCUMENTOS` entre dos cargas | En el SQL Editor: `delete from trozos where fuente = '<la fuente vieja>';` |
| **En la carga** | | |
| `--probar` dice "sin texto" | PDF escaneado: son fotos, no hay texto que leer | Otro texto, o su versión web guardada como `.md` |
| Trozos con palabras pegadas o desordenadas | PDF a dos columnas o con tablas | La versión web del texto, o pide a tu agente un arreglo en `limpiar()` |
| `Gemini ha dado un error 400` con "API key not valid" | Clave mal copiada (un espacio, falta un trozo) | Cópiala otra vez de tu gestor de contraseñas |
| `Gemini ha dado un error 400` que menciona `task_type` | Alguien añadió `task_type` | Quítalo: `gemini-embedding-2` no lo acepta; la tarea va en el texto |
| `Gemini ha dado un error 404` | El nombre del modelo está mal escrito | `gemini-embedding-2`, tal cual |
| `Gemini sigue diciendo 429` | Has llegado al límite gratuito por minuto o por día | Espera unos minutos y vuelve a ejecutar: no duplica nada. Tus límites, en https://aistudio.google.com/rate-limit |
| "SUPABASE_SECRET_KEY es la clave publicable" | Has pegado la publicable | Una secreta nueva (`sb_secret_...`), solo para la carga |
| **En tu MCP** | | |
| "El servidor no tiene GEMINI_API_KEY" | Falta la variable | En local, la línea de `GEMINI_API_KEY` de la terminal 1; en Render, Environment; en Supabase, Edge Functions, Secrets |
| `buscar_en_textos` devuelve 0 trozos y la tabla tiene filas | La RLS no deja leer | Ejecuta otra vez `trozos.sql` (paso 4: la política de lectura) |
| Siempre salen los mismos trozos, con un parecido casi igual para cualquier pregunta | Los trozos se cargaron con otro modelo, otras dimensiones o sin el formato `title: ... \| text: ...` | Vuelve a cargar con `cargar_textos.py` sin cambiar `MODELO` ni `como_documento` |
| Tu agente responde de memoria, sin llamar a `buscar_en_textos` | La descripción no dice qué documento hay detrás | Nombra el documento y sus temas en el docstring y en las `instructions`. Para salir del paso: "usa buscar_en_textos" |
| Tu agente usa `buscar_en_textos` para cifras de tus datos | Las descripciones no separan texto y datos | `buscar_en_textos`: "NO para cifras, filas o recuentos". `buscar_X`: "para filas y recuentos de <tus datos>" |
| Cita una página que no es | Responde con lo que recuerda, no con el trozo | En la descripción: "cita solo la fuente y la página del trozo que usas" |
| **En Windows** | | |
| "running scripts is disabled" | Windows no deja activar el entorno | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a activarlo |
| Tildes raras en la pregunta con `Invoke-RestMethod` | Windows PowerShell 5.1 manda el texto en otra codificación | Añade `; charset=utf-8` al `-ContentType`, como en el paso 6 |

Para cualquier otro error: copia las últimas líneas de la terminal (o de Logs en Render, o de Edge Functions, Logs en Supabase) y pégaselas a tu agente con "Mi RAG da este error. Lee extra-rag.md, rag/cargar_textos.py y modelo/servidor_mcp.py y dime qué cambio. No cambies el modelo ni las dimensiones." Y si no sale, pregunta al docente.

---

## Qué está probado

El 26/11/2026, en macOS con Python 3.12, `mcp==2.3.0` y `httpx==0.28.1`, en un Postgres 16 con pgvector 0.6 que imita los roles de Supabase (`anon`, `authenticated`, `service_role`) y con servicios falsos que imitan la API de Gemini y la de Supabase:

- `trozos.sql`: se ejecuta dos veces sin error, también en un proyecto que no da permisos automáticos a las tablas nuevas; `anon` no puede escribir; la búsqueda devuelve primero el trozo idéntico (parecido 1), respeta el tope de 20 y el valor por defecto de 5; con vectores de 3072 da los dos errores de la tabla; sin política, 0 trozos; sin permiso, `42501`.
- `cargar_textos.py`: el troceo con un PDF de 24 páginas y un `.md` de 90 KB (ningún trozo pasa de 800 caracteres, no se pierde texto, solape medio de unos 140 caracteres, los trozos del PDF llevan su página); la carga escribe con la clave secreta; volver a cargar no duplica; con dos 429 seguidos espera y termina; clave publicable (nueva o antigua) o mal copiada, y clave de Gemini mala: para con un mensaje claro; `--probar` no llama a nada.
- `buscar_en_textos` montada en la plantilla de hoy: aparece junto a `buscar_X` y `predecir_Y`; una pregunta sobre un tema del texto devuelve primero el trozo que habla de él, con fuente y página; busca con la clave publicable; manda la pregunta como `task: question answering | query: ...`; `cuantos` fuera de 1 a 10, sin `GEMINI_API_KEY`, sin política de lectura y sin permiso dan el mensaje que lee la IA; `probar_mcp.py` termina en "Todo bien".

**Sin probar:** contra Gemini y Supabase de verdad (incluidos la comprobación de la clave del paso 4 y el límite gratuito de peticiones), en Render, en Windows, la versión de la Edge Function (`herramienta_textos.ts`) y con un texto en inglés y preguntas en español. Si algo no cuadra con lo que ves, avisa al docente y apúntalo en tu bitácora: también es un resultado.

**Documentación seguida** (consultada el 26/11/2026): Supabase, https://supabase.com/docs/guides/ai, https://supabase.com/docs/guides/ai/vector-columns, https://supabase.com/docs/guides/ai/semantic-search, https://supabase.com/docs/guides/ai/vector-indexes/hnsw-indexes, https://supabase.com/docs/guides/api/securing-your-api y https://supabase.com/docs/guides/functions/secrets. Gemini (la documentación de la API se ha mudado a AI Studio), https://aistudio.google.com/docs/embeddings, https://aistudio.google.com/docs/pricing y https://aistudio.google.com/docs/api-key.
