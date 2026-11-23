# Tu proyecto, en documentos

Módulo 10 · Sesión 2 · martes 24/11/2026

Hasta ahora tienes una idea y, quizá, una página. Antes de construir más, tu proyecto se escribe: qué es, cómo se monta y dónde está. Tu agente lo lee cada vez que le pides algo, así que lo que escribas aquí es lo que hará bien.

Abre tu agente **en la carpeta de tu cuaderno** (`alumno-tu-nombre`). Desde hoy, es el sitio desde el que trabajas siempre: los documentos están en la raíz y el código de tu app, en `apps/tu-proyecto`.

---

## Qué hay en tu cuaderno

| Archivo | Para qué sirve |
|---|---|
| `idea.md` | Tu idea en una frase y cuándo se aprobó |
| **`brief.md`** (nuevo) | El proyecto en una página: problema, usuarios, objetivo, alcance, criterios de éxito, restricciones e hitos |
| `datos.md` | Tus datos: fuente, licencia y columnas |
| `mapa.md` o `esquema.md` | Solo si te lo hizo Paco en la sesión 1. Se queda como está |
| **`arquitectura.md`** (nuevo) | Las piezas, cómo se conectan, dónde vive cada una, y la pieza en la que estás, en detalle |
| **`estado.yaml`** (nuevo) | Dónde está cada pieza: pendiente, en curso, hecho o bloqueado, con su URL. El docente lo lee para ver cómo va la clase |
| **`todo.md`** (nuevo) | Las tareas de la sesión de hoy. Tu agente las marca al terminarlas |
| `decisiones.md` | Cada decisión con su porqué. El 20 % de la nota es justificar decisiones: aquí están |
| `bitacora/` | Una nota por sesión. De aquí sale la autoevaluación del 3/12 |
| `urls.md` | Tus URLs y tus repos |
| `apps/tu-proyecto/` | Tu app: el código, en su propio repo |

Cada archivo tiene un trabajo y solo uno: lo técnico va en `arquitectura.md`, lo que está hecho en `estado.yaml`, el porqué en `decisiones.md`.

---

## El prompt (cópialo entero)

Sirve aunque solo tengas la idea y nada construido: lo que no sepas, queda como "por decidir".

````
Lee AGENTS.md antes de nada. Vamos a poner mi proyecto en documentos, en
este cuaderno.

1. Lee idea.md, datos.md, decisiones.md, urls.md, la bitácora y, si
   existen, mapa.md y esquema.md (no los cambies). Si hay una carpeta en
   apps/, mira qué hay construido (web/, datos/, sql/) sin cambiar nada.
2. Hazme, una a una, las preguntas que falten para rellenar los cuatro
   archivos de abajo. Si no sé algo, escribe "por decidir" y sigue. No
   inventes datos, cifras ni URLs.
3. Escribe estos cuatro archivos, en español y cortos:
   - brief.md: problema, usuarios, objetivo, alcance (qué entra y qué
     no), criterios de éxito, restricciones (todo en planes gratuitos;
     presentación el 9/12; para aprobar, la app con datos, el modelo como
     API y el MCP funcionando; el agente suma nota) e hitos por sesión:
     S1 lun 23/11 idea y página en Vercel · S2 mar 24/11 datos en
     Supabase y app con login · S3 mié 25/11 modelo como API en Render ·
     S4 jue 26/11 servidor MCP · S5 lun 30/11 agente que avisa por
     Telegram · S6 mar 01/12 el agente usa el MCP · S7 mié 02/12
     seguridad · S8 jue 03/12 autoevaluación · S9 mié 09/12 presentación.
   - arquitectura.md: las piezas y cómo se conectan (navegador, web/ en
     Vercel, tablas de Supabase, modelo como API en Render en la S3,
     servidor MCP en la S4, agente en la S5 y la S6), con la tecnología
     de cada una y en qué repo y carpeta vive. Después, una sección
     "Pieza actual: la app con login (S2)": tablas y columnas, pantallas,
     quién entra, qué guarda cada usuario y la seguridad (RLS) en una
     línea. Si existe mapa.md o esquema.md, úsalo.
   - estado.yaml: con exactamente este esquema. Cambia solo los valores,
     con lo que hay de verdad:

     version: 1
     proyecto: ""
     actualizado: ""      # AAAA-MM-DD
     sesion: 2
     idea_aprobada: false
     piezas:
       web:       {estado: pendiente, sesion: 1, url: "", repo: "", nota: ""}
       datos:     {estado: pendiente, sesion: 2, url: "", repo: "", nota: ""}
       app_login: {estado: pendiente, sesion: 2, url: "", repo: "", nota: ""}
       modelo:    {estado: pendiente, sesion: 3, url: "", repo: "", nota: ""}
       mcp:       {estado: pendiente, sesion: 4, url: "", repo: "", nota: ""}
       agente:    {estado: pendiente, sesion: 5, url: "", repo: "", nota: ""}
       seguridad: {estado: pendiente, sesion: 7, url: "", repo: "", nota: ""}
     bloqueos: []
     siguiente: ""

     estado es pendiente, en_curso, hecho o bloqueado. repo es
     usuario/repo/carpeta (por ejemplo "ana/ventas/web"). En url, nunca
     una clave. Escríbelo en bloques, una clave por línea, con un
     comentario en español que explique cada una.
   - todo.md: las tareas de hoy, sesión 2, sacadas de estado.yaml y del
     hito de hoy (mis datos en Supabase y mi app con login en Vercel).
     Si me falta lo de la sesión 1 (repo de la app, Vercel, URL), eso va
     primero. Tareas concretas, que se puedan comprobar.
4. Enséñame un resumen de cada archivo en tres líneas y espera mi OK.
5. Con mi OK: commit con el mensaje "Mi proyecto en documentos" y push.
   Dime los comandos antes de ejecutarlos.
````

Léelos cuando termine. Si algo no es verdad, corrígelo tú: es tu proyecto.

---

## Al final de cada sesión (5 minutos)

Desde hoy, el cuaderno se cierra así cada tarde. Abre tu agente en la carpeta del cuaderno y pega (cambia `N` por la sesión de hoy):

```
Lee AGENTS.md. Hoy ha sido la sesión N.
1. Mira qué ha cambiado hoy en apps/ y pregúntame lo que no sepas.
2. Si el código de apps/ tiene cambios sin subir, haz commit y push
   ahí primero.
3. Actualiza estado.yaml: solo los valores (estado, url, nota,
   actualizado, sesion, bloqueos y siguiente), sin tocar el esquema.
4. En todo.md, marca lo hecho y deja la lista de la próxima sesión.
5. Escribe bitacora/sesion-0N.md preguntándome una a una: qué conseguí,
   qué le pedí a la IA, qué falló y cómo lo arreglé.
6. Si hoy decidí algo importante, añádelo a decisiones.md con su porqué.
7. Commit en el cuaderno con el mensaje "Sesión N: estado y bitácora" y
   push. Dime los comandos antes de ejecutarlos.
```

---

## Si algo falla

| Síntoma | Arreglo |
|---|---|
| El agente inventa cosas (URLs, cifras, usuarios) | "No inventes: pregúntame". Y corrige el archivo tú |
| `estado.yaml` sale con otras claves o en otro orden | "Usa exactamente el esquema del prompt; cambia solo los valores". El docente lo lee con un programa: si cambian las claves, no lo encuentra |
| No sabes qué poner en el alcance o en la arquitectura | "Por decidir" vale hoy. Lo importante es que esté escrito lo que sí sabes |
| El agente quiere cambiar `mapa.md` o `esquema.md` | No: se leen, no se tocan |
| `git push` del cuaderno falla porque el submódulo tiene cambios | Haz primero commit y push dentro de `apps/tu-proyecto` |
