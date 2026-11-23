# Tu app con datos: Supabase y login

Módulo 10 · Sesión 2 · martes 24/11/2026

Al terminar tendrás:
- **tus datos en una tabla de Supabase**, con seguridad a nivel de fila (RLS);
- **tu app en Vercel leyendo esos datos**, con filtros, login y algo que cada usuario guarda solo para él (por ejemplo, favoritos).

Necesitas lo de ayer en su sitio (si no, empieza por `puesta-al-dia-s1.md`) y tu proyecto en documentos (`tu-proyecto-en-documentos.md`, a las 18:30): la app se construye a partir de `brief.md` y `arquitectura.md`.

---

## Qué va en cada sitio

Ayer el lío fue este. Cada cosa tiene un sitio, y solo uno:

| Qué | Dónde |
|---|---|
| `web/index.html`, el SQL (`sql/`), tu CSV si se puede publicar | **Tu app**: `apps/tu-proyecto`, repo de tu cuenta |
| La idea, el brief, la arquitectura, el estado, las tareas, la bitácora, la URL de tu proyecto de Supabase | **Tu cuaderno**: `idea.md`, `brief.md`, `arquitectura.md`, `estado.yaml`, `todo.md`, `bitacora/`, `urls.md` |
| Tus datos, tus usuarios, sus favoritos | **Supabase**, en tu proyecto |
| La contraseña de la base de datos, la clave secreta | **Tu gestor de contraseñas.** En ningún repo, en ningún chat, en ninguna captura |

**Abre tu agente siempre en la carpeta de tu cuaderno.** Los documentos están en la raíz y el código de tu app, en `apps/tu-proyecto`. El agente escribe el código ahí y, al subir, hace commit y push primero en la app y después en el cuaderno.

---

## Paso 1: crea tu proyecto de Supabase

1. En https://supabase.com, entra con GitHub y pulsa **New project**. ¿Sin cuenta todavía? **Start your project** y **Continue with GitHub** (paso 7 del setup).
2. **Organization:** la tuya (plan Free). **Name:** el de tu proyecto.
3. **Database password:** pulsa **Generate a password** y guárdala en tu gestor de contraseñas. No la pegues en ningún archivo. Hoy no la vas a necesitar.
4. **Region:** deja "Europe" (Supabase lo pone en Zúrich; está bien).
5. **Data access:** deja lo que viene marcado. La seguridad de tu tabla la activas en el paso 2.
6. **Create new project.** Tarda unos segundos.

¿"Has llegado al límite de proyectos gratis"? El plan Free deja dos proyectos activos. Pausa uno que no uses (Project Settings, General, Pause project).

**Ya lo tengo si:** veo el panel de mi proyecto.

---

## Paso 2: sube tus datos

Tu CSV está en `datos/` de tu app (si se puede publicar) o solo en tu portátil (si es de tu empresa). Nunca en el cuaderno.

1. En el menú de la izquierda, **Table Editor** y **New table**.
2. **Name:** en minúsculas y sin espacios (por ejemplo, `ventas`). Deja marcado **Enable Row Level Security (RLS)** (viene marcado y pone "Recommended").
3. **Import data from CSV**, **Upload CSV**, y elige tu archivo. Revisa la vista previa: los nombres de columna son los de la primera línea del CSV.
4. **La clave primaria.** El import cambia las columnas que traía la tabla (`id` y `created_at`) por las de tu CSV y **no crea ningún id**: verás el aviso "No primary keys selected". Marca como **Primary** la columna de tu CSV que no se repite nunca (un id, un código). Sin clave primaria no podrás editar ni borrar filas. ¿Tu CSV no tiene ninguna? Mira "Si el import falla", abajo.
5. **Save.** Tarda unos segundos.

**Ya lo tengo si:** la tabla muestra mis filas y el contador de abajo dice cuántas hay. Compáralo con tu CSV.

**Lo que hace el import solo:** deduce los tipos (texto, enteros, decimales, sí o no, fechas) y los valores vacíos quedan vacíos (NULL), sin errores.

**Si el import falla:**
- **Nombres de columna con tildes, espacios o símbolos:** Supabase solo admite letras, números, guiones y guiones bajos.
- **Fechas en un formato raro:** Supabase quiere `AAAA-MM-DD HH:mm:ss` (también acepta el formato ISO con zona horaria).
- **Sin columna que no se repita:** hace falta una para la clave primaria.

En los tres casos, pídele a tu agente: "Este CSV da este error al importarlo en Supabase: [pega el error, o "no tiene columna única"]. Arréglalo en una copia, `datos/para-supabase.csv`: nombres de columna sin tildes ni espacios, fechas como AAAA-MM-DD HH:mm:ss y, si hace falta, una primera columna `id` numerada. Sin cambiar los datos." Y vuelve a importar esa copia.

---

## Paso 3: el truco del día, dale a tu agente la forma de tus datos

Tu agente no necesita tus datos: le basta su forma. Las cinco primeras líneas de tu CSV dicen las columnas y cómo son los valores.

En la terminal, en la carpeta de tu cuaderno (Mac o Git Bash):

```bash
head -5 apps/tu-proyecto/datos/tu-archivo.csv
```

(En PowerShell: `Get-Content apps\tu-proyecto\datos\tu-archivo.csv -TotalCount 5`.)

Copia lo que sale. Si tus datos son de tu empresa o tienen datos personales, cambia los valores por otros inventados antes de pegarlos: al agente le basta con los nombres de columna y el tipo de valor.

---

## Paso 4: la seguridad, con SQL que escribe tu agente y ejecutas tú

Pega en tu agente, con tus datos:

```
Lee AGENTS.md y arquitectura.md antes de nada.

Mi tabla en Supabase se llama [nombre-de-tu-tabla] y su clave primaria es
[tu columna primaria]. Estas son las cinco primeras líneas del CSV que
importé:

[pega aquí las cinco líneas]

Escribe apps/[tu-proyecto]/sql/01_seguridad.sql para Supabase con:
1. Lectura de [nombre-de-tu-tabla] para todo el mundo (roles anon y
   authenticated). [Si tus datos son privados, cambia esta línea por:
   "Lectura de [nombre-de-tu-tabla] solo para usuarios con login".]
2. La tabla de lo que guarda cada usuario, según arquitectura.md (si no
   lo dice, favoritos): id, user_id uuid con valor por defecto
   auth.uid(), la clave primaria de [nombre-de-tu-tabla] y fecha, con
   RLS: cada usuario ve, guarda y quita solo lo suyo.
3. Los grant que hagan falta para anon y authenticated.

No lo ejecutes: lo ejecuto yo en el SQL Editor de Supabase. Explícame
cada bloque en una frase.
```

Después, en Supabase: **SQL Editor**, **New query**, pega el contenido de `apps/tu-proyecto/sql/01_seguridad.sql` y pulsa **Run**. Tiene que decir "Success".

**Ya lo tengo si:** en **Authentication, Policies** veo las políticas de mis dos tablas.

**Ojo:** hasta que ejecutes este SQL, tu tabla tiene la RLS activada y ninguna política, así que nadie puede leerla desde fuera: tu app recibirá una lista vacía (`[]`). Es lo esperado. Si después del paso 6 ves "0 filas", vuelve aquí.

---

## Paso 5: activa el login

1. **Authentication, Sign In / Providers.** "Allow new users to sign up" ya viene activado.
2. **Confirm email viene activado: desactívalo y pulsa Save changes.** El email que trae Supabase solo manda unos pocos mensajes por hora: con toda la clase registrándose a la vez, os quedaríais atascados. En un proyecto real lo dejarías activado.
3. **Authentication, URL Configuration, Site URL:** tu URL de Vercel.

---

## Paso 6: la app, con tu agente

Necesitas dos datos del panel: **Project Settings, API Keys** (o el botón **Connect**):
- la **URL del proyecto** (`https://xxxx.supabase.co`);
- la **clave publicable** (`sb_publishable_...`; en proyectos antiguos se llama `anon`).

Estas dos sí pueden ir en tu web: cualquiera las puede ver, y lo que protege tus datos es la RLS del paso 4. **La clave secreta (`sb_secret_...` o `service_role`) no va nunca en el código.**

```
Lee brief.md y arquitectura.md antes de nada, y construye la pieza
actual (la app con login) en apps/[tu-proyecto]/web/index.html.

- URL del proyecto: [tu URL]
- Clave publicable: [tu clave publicable]. Se puede publicar: la protege
  la RLS. No uses nunca una clave secreta.
- Tablas: las de arquitectura.md, con el SQL de
  apps/[tu-proyecto]/sql/01_seguridad.sql.

Si arquitectura.md no lo concreta, la app:
1. Lista las filas de la tabla, 50 como mucho, con 2 o 3 filtros útiles
   para mi idea (propónmelos antes de escribir nada).
2. Login con email y contraseña: registrarse, entrar y salir.
3. Con sesión iniciada: guardar y quitar lo suyo (favoritos), y una
   sección para verlo.
4. Pie con la fuente y la licencia de mis datos.

Un solo archivo HTML con el CSS y el JavaScript dentro. La librería de
Supabase, desde https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm.
Pasos pequeños: dime el plan antes de escribir. Al terminar, marca en
todo.md lo que esté hecho.
```

Si `arquitectura.md` y lo que te propone el agente no coinciden, decide tú y corrige el documento: es el plano de tu proyecto.

---

## Paso 7: pruébala en local, con dos usuarios

1. Si tienes Python, en la carpeta del cuaderno: `python3 -m http.server 8000 --directory apps/tu-proyecto/web` y abre http://localhost:8000 (en Windows, `python` en vez de `python3`). Si no, haz el paso 8 y pruébala en tu URL de Vercel.
2. Regístrate con un email y guarda dos favoritos.
3. Abre una ventana de incógnito, regístrate con **otro** email: no tienes que ver los favoritos del primero.

Eso es la RLS funcionando: los datos son públicos, los favoritos de cada uno no.

**¿La lista sale vacía?** Mira la consola del navegador (clic derecho, Inspeccionar, Console). "permission denied" o una lista vacía sin error: falta la política de lectura del paso 4.

---

## Paso 8: commit y push de tu app

Pídeselo a tu agente:

```
Haz commit en apps/[tu-proyecto] con el mensaje "S2: app con datos de
Supabase y login" y push. Enséñame el git status y los comandos antes.
```

O a mano, en la terminal: `cd apps/tu-proyecto`, `git add .`, `git status`, `git commit -m "S2: app con datos de Supabase y login"` y `git push`.

Lee el `git status` antes del commit: ¿se va a subir algo que no debería (una clave secreta, datos privados)? Si es así, para y pregúntame.

Vercel publica solo. Abre tu URL en el móvil y entra con tu usuario.

---

## Paso 9: cierra el día en tu cuaderno

El prompt "Al final de cada sesión" de `tu-proyecto-en-documentos.md`, con `N` = 2. Antes del último punto, añade uno:

```
Apunta en urls.md la URL de mi proyecto de Supabase
([https://xxxx.supabase.co]) y la de Vercel. Ninguna clave.
```

Así quedan al día `estado.yaml`, `todo.md`, la bitácora de hoy y `urls.md`.

---

## Si algo falla

| Síntoma | Arreglo |
|---|---|
| El import del CSV da error | Paso 2, "Si el import falla" |
| La lista sale vacía (`[]`, "0 filas") | Es lo normal hasta el paso 4: RLS activada y ninguna política. Ejecuta el SQL. Si ya lo ejecutaste, la tabla tiene otro nombre en el código |
| "No primary keys selected" al importar | Marca como Primary la columna que no se repite (paso 2) |
| El import no acepta tus columnas | Nombres sin tildes ni espacios (paso 2, "Si el import falla") |
| "Invalid login credentials" | Te registraste con otro email, o con "Confirm email" activado y sin confirmar (paso 5) |
| "Email rate limit exceeded" o el registro no llega | "Confirm email" sigue activado: desactívalo, Save changes (paso 5), y regístrate con otro email |
| En local funciona y en Vercel no | ¿Has hecho push? ¿Vercel publica el repo de tu app, con Root Directory `web`? |
| El otro usuario ve mis favoritos | La política de favoritos no filtra por `auth.uid()`: enséñale el error a tu agente y vuelve a ejecutar el SQL |
| Te pide la contraseña de la base de datos | Para lo de hoy no hace falta. Si la perdiste: Project Settings, Database, Reset password |

## Sin datos todavía

Elige una de las temáticas de ejemplo (`de-cero-a-url.md`, paso 0) y descarga su CSV. Si es enorme (Tienda online o Luz de casa), pide a tu agente una muestra de 5.000 filas antes del paso 2.

## Si no puedes instalar nada

Haz los pasos 1, 2, 4 y 5 en el panel de Supabase. Para el SQL del paso 4 y la app del paso 6, usa los mismos prompts en un chat gratis (pega también tu `brief.md` y tu `arquitectura.md`) y pega el resultado en github.com, en el repo de tu app: **Add file, Create new file**, `sql/01_seguridad.sql` o `web/index.html`.
