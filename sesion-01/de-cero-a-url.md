# De cero a URL

Módulo 10 · Sesión 1 · lunes 23/11/2026

Los pasos y los prompts de la demo de las 19:00, para que los sigas a tu ritmo con tu propio proyecto. Al terminar tendrás:

- **tu repositorio en GitHub**, con una carpeta por pieza del proyecto (hoy `web/`; `api/`, `mcp/` y `agente/` llegan en las próximas sesiones) y un `AGENTS.md` que explica tu proyecto;
- **tu primera página publicada en Vercel**, con una URL que puedes abrir en el móvil.

Tiempo: unos 30 a 45 minutos la primera vez. Necesitas el setup hecho (`setup-paso-a-paso.md`). Si no puedes instalar nada, ve al final: "Camino sin instalar nada".

---

## Paso 0: tu idea en una frase

Tu proyecto necesita **datos reales** (que existan hoy y puedas descargar) y **algo que predecir** con ellos. Escríbela así:

> "Con **[mis datos, y de dónde salen]** quiero predecir **[qué]** para **[quién]**."

Ejemplos: "Con las ventas diarias de la panadería de mi familia (2023 a 2025) quiero predecir cuántas barras vender mañana para no tirar pan." "Con los resultados de LaLiga de las últimas diez temporadas quiero predecir el resultado de cada partido para mi peña."

Antes de publicarla, comprueba:
1. ¿Los datos existen y los puedes descargar **hoy**? (Un enlace o un archivo, no "los pediré".)
2. ¿Hay una columna con lo que quieres predecir?
3. ¿Hay suficientes filas? Cientos como mínimo, mejor miles.
4. ¿Los puedes usar? Datos abiertos, o de tu empresa sin datos personales y con permiso.

Sitios con datos abiertos: datos.gob.es, el portal de datos abiertos del Ayuntamiento de Madrid, INE, Eurostat, AEMET OpenData, Kaggle.

**¿Sin idea o sin datos? Paco (opcional).** Paco es tu sparring: no te da ideas, te saca las tuyas; te busca datos reales en Kaggle y en datos abiertos y te dice si sirven; y, si quieres, te dibuja un mapa aproximado de tu proyecto con un primer `AGENTS.md`. El prompt y cómo usarlo están en **`sparring-paco.md`** (vale cualquier chat gratis). Si se pone blando, dile: "no me aplaudas, rompe la idea".

**Cuando tengas la frase, publícala en el debate “Ideas y URLs” del aula virtual.** Te la apruebo ahí; si tengo dudas, paso por tu mesa. Mientras, sigue con el paso 1.

**Si a las 20:30 no tienes idea aprobada,** elige una de estas temáticas de ejemplo y sigue esta guía igual. Todas tienen datos abiertos que puedes usar citando la fuente. Pisos Madrid no está en la lista: es el proyecto de mis demos y lo vas a ver entero.

| # | Temática | Qué predecir | Datos (licencia) |
|---|---|---|---|
| 2 | Aire de Madrid | El NO2 de mañana en cada estación | [Calidad del aire, datos horarios desde 2001](https://datos.madrid.es/dataset/201200-0-calidad-aire-horario), Ayuntamiento de Madrid (CC BY 4.0) |
| 3 | BiciMAD | Los usos de mañana | [BiciMAD: altas de usuarios y usos por día](https://datos.madrid.es/dataset/213155-0-bicimad-usos-usuarios), Ayuntamiento de Madrid (CC BY 4.0) |
| 4 | Tienda online | Las unidades de cada producto la semana que viene | [Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii), UCI, 1.067.371 filas (CC BY 4.0) |
| 5 | Campaña de un banco | Si un cliente contratará el depósito | [Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing), UCI, 45.211 filas (CC BY 4.0) |
| 6 | Luz de casa | El consumo de mañana | [Individual Household Electric Power Consumption](https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption), UCI, 2.075.259 filas (CC BY 4.0) |

Tu frase queda así, por ejemplo: "Con las medidas horarias de calidad del aire del Ayuntamiento de Madrid quiero predecir el NO2 de mañana para avisar a quien vive en mi barrio."

---

## Paso 1: crea tu repositorio en GitHub

1. En https://github.com, pulsa **+** (arriba a la derecha) y **New repository**.
2. **Repository name:** el nombre de tu proyecto, en minúsculas y con guiones (por ejemplo, `demanda-panaderia`). Aparecerá en tu URL.
3. **Description:** tu idea en una frase.
4. **Public** o **Private**:
   - **Public** si tus datos son abiertos. Cualquiera podrá ver tu código y tus datos (es tu portfolio).
   - **Private** si tus datos son de tu empresa o tienen datos personales. Vercel publica igual repos privados de tu cuenta personal. Más adelante tendrás que darme acceso.
5. Marca **Add a README file**.
6. **Create repository.**

---

## Paso 2: clónalo y crea la estructura

En la terminal (Mac: Terminal · Windows: Git Bash). Cambia `TU-USUARIO` y `TU-PROYECTO` por los tuyos:

```bash
cd ~
git clone https://github.com/TU-USUARIO/TU-PROYECTO.git
cd TU-PROYECTO
mkdir web datos
```

Ya tienes en tu portátil una carpeta `TU-PROYECTO` conectada a GitHub, con dos carpetas dentro:

```
TU-PROYECTO/
├── AGENTS.md      (lo creas en el paso 3)
├── README.md
├── datos/         tu CSV, si ya lo tienes
└── web/           tu página (hoy)
```

Más adelante añadirás `api/` (tu modelo, sesión 3), `mcp/` (tu servidor MCP, sesión 4) y `agente/` (sesión 5). Un repo, una carpeta por pieza.

**Si ya tienes tu CSV,** cópialo a `datos/` con el Finder o el Explorador.
**Si tus datos son privados,** que no suban a GitHub:

```bash
echo "datos/" >> .gitignore
```

Abre OpenCode **en la carpeta del proyecto** (en la app: abrir carpeta; en la terminal: `opencode` dentro de la carpeta).

---

## Paso 3: `AGENTS.md`, lo que el agente sabe de tu proyecto

`AGENTS.md` es un archivo en la raíz del repo que el agente lee antes de hacer nada: de qué va tu proyecto, tus datos, la estructura y tus reglas. Te ahorra repetirlo en cada prompt, y crecerá contigo durante el módulo.

Pídele a OpenCode que lo cree:

```
Crea AGENTS.md en la raíz del proyecto con la plantilla de abajo. Antes de
escribirlo, hazme una a una las preguntas que necesites para rellenar lo que
va entre corchetes. Si hay un CSV en datos/, míralo tú para contar las filas
y ver las columnas.

# [Nombre de tu proyecto]

[Tu idea en una frase: "Con ... quiero predecir ... para ..."]

## Datos
- Fuente: [de dónde salen, con enlace]
- Licencia: [la que tengan, o "privados, no publicar"]
- Archivo: datos/[archivo].csv, [número de filas] filas
- Lo que quiero predecir: la columna [columna]

## Estructura
- web/: la página pública, publicada en Vercel con Root Directory web.
  Por ahora, HTML estático.
- Vendrán: api/ (modelo, sesión 3), mcp/ (servidor MCP, sesión 4)
  y agente/ (sesión 5).

## Reglas para el agente
- Habla en español.
- Las cifras se calculan con código, nunca de memoria. Guarda el script
  en scripts/ y enséñame el resultado antes de usarlo.
- Pasos pequeños: dime el plan antes de crear o cambiar archivos.
- Ninguna clave ni contraseña en el código.
- En web/, sin frameworks por ahora: un archivo HTML con el CSS dentro.
```

Léelo cuando termine. Si algo no es verdad, corrígelo tú: es tu proyecto.

> **Si usas Claude Code en lugar de OpenCode:** crea también un archivo `CLAUDE.md` con una sola línea, `@AGENTS.md`, para que lo lea.

---

## Paso 4: pide tu página a OpenCode

**Si ya tienes tus datos en `datos/`:**

```
Lee AGENTS.md antes de nada.

Quiero la primera página de mi proyecto en web/index.html. Debe contar:
1. mi idea en una frase (está en AGENTS.md), como titular;
2. de dónde salen mis datos, con su enlace y su licencia;
3. dos o tres cifras clave de mis datos, en grande (por ejemplo: cuántas
   filas hay, la media o la mediana de lo que quiero predecir, y algún
   máximo o mínimo interesante).

Las cifras no las adivines: calcúlalas con un script de Python que use solo
la librería estándar (csv y statistics), guárdalo en scripts/ y ejecútalo.
Enséñame las cifras ANTES de escribir la página.

La página: un solo archivo HTML con el CSS dentro, sin librerías, en español
y que se vea bien en el móvil.
```

**Si todavía no tienes los datos, o OpenCode dice que no encuentra Python:**

```
Lee AGENTS.md antes de nada.

Quiero la primera página de mi proyecto en web/index.html: mi idea en una
frase como titular, de dónde saldrán mis datos y qué quiero predecir, y una
sección "Próximamente" con las cuatro piezas que voy a construir (app con
datos, modelo, servidor MCP y agente). No inventes cifras.

Un solo archivo HTML con el CSS dentro, sin librerías, en español y que se
vea bien en el móvil.
```

Las cifras pueden esperar: mañana tus datos estarán en Supabase.

**El truco del día:** el agente no adivina cifras, las calcula. Si te da un número sin un script detrás, no te lo creas: pídele el script y que lo ejecute.

---

## Paso 5: mírala en local y compruébala

1. Abre `web/index.html` con doble clic (o pídele a OpenCode: "ábrela en el navegador").
2. Comprueba: ¿las cifras son las que imprimió el script? ¿Están la fuente y la licencia de tus datos? ¿Se lee bien estrechando la ventana, como en un móvil?
3. ¿Quieres cambiar algo? **Un cambio por prompt:** "haz el titular más grande", "pon las cifras en tarjetas". Nada de "rehazlo todo".

---

## Paso 6: commit y push

En la terminal, dentro de la carpeta del proyecto:

```bash
git add .
git status
git commit -m "Primera página"
git push
```

Antes del `commit`, lee lo que dice `git status`: ¿se va a subir algo que no debería (una clave, datos privados)? Si es así, para y pregúntame.

También puedes pedírselo a OpenCode ("Haz commit con el mensaje 'Primera página' y push"), pero **lee los comandos que propone antes de aprobarlos**.

Recarga tu repo en github.com: tienen que aparecer `AGENTS.md` y `web/index.html`.

---

## Paso 7: publícala en Vercel

1. En https://vercel.com, pulsa **Add New...** y **Project**.
2. En "Import Git Repository", busca tu repo y pulsa **Import**.
   ¿No aparece? Pulsa **Adjust GitHub App Permissions**, da acceso a ese repo y vuelve.
3. **Root Directory:** pulsa **Edit**, elige la carpeta **`web`** y continúa. Es lo único que verá Vercel.
4. **Framework Preset:** **Other**. No toques nada más.
5. **Deploy.** Tarda unos segundos.
6. Abre tu URL (`https://tu-proyecto.vercel.app` o parecida) en el móvil.

A partir de ahora, **cada `git push` vuelve a publicar tu página sola.** No hace falta volver a Vercel.

---

## Paso 8: publica tu URL

En el debate “Ideas y URLs” del aula virtual, una línea:

> Tu nombre · https://tu-proyecto.vercel.app · Con [datos] quiero predecir [qué].

¿No has llegado a la URL? Publica tu idea y dónde te has quedado. Lo terminas en casa con esta guía.

---

## Camino sin instalar nada

Si tu portátil no te deja instalar programas, puedes llegar al hito de hoy solo con el navegador:

1. Crea el repo en github.com (paso 1).
2. Pide la página a cualquier chat de IA (ChatGPT, Gemini o Claude) con el segundo prompt del paso 4, añadiendo tu idea y de dónde salen tus datos. Copia el HTML que te dé.
3. En tu repo, pulsa **Add file** y **Create new file**. Como nombre escribe `web/index.html` (la barra crea la carpeta). Pega el HTML y pulsa **Commit changes**.
4. Haz lo mismo con `AGENTS.md` (plantilla del paso 3, rellenada a mano).
5. Publica en Vercel (paso 7).

Por este camino no hay cifras calculadas: un chat no puede leer tu archivo completo de forma fiable. Llegarán cuando tengas el setup completo.

---

## Si algo falla

| Síntoma | Causa típica | Arreglo |
|---|---|---|
| Vercel da `404: NOT_FOUND` | El Root Directory no es `web`, o el archivo no se llama `index.html` | En Vercel: Settings del proyecto, Root Directory = `web`, y vuelve a desplegar. Comprueba el nombre del archivo en GitHub |
| Tu repo no aparece en Vercel | La app de Vercel no tiene permiso en ese repo | **Adjust GitHub App Permissions** y dale acceso |
| `git push` pide usuario y contraseña | Git no está conectado a GitHub | `gh auth login` (paso 4 del setup) |
| `git push` dice "Updates were rejected" | Cambiaste algo en la web de GitHub | `git pull` y después `git push` |
| Vercel enseña la versión antigua | El despliegue aún no ha terminado | Mira la pestaña Deployments y recarga la página |
| Una cifra no cuadra | El agente la estimó en vez de calcularla | "Ejecuta el script de scripts/ y usa exactamente lo que imprima" |
| GitHub rechaza tu CSV | Pesa más de 100 MB | No lo subas: usa una muestra, o deja `datos/` fuera del repo |
| Has subido algo privado (datos o una clave) | Faltaba en `.gitignore` | Avísame. Pon el repo en Private y, si era una clave, cámbiala |

---

## Lo que te llevas

- **Un repo tuyo, con una carpeta por pieza.** Hoy `web/`; el proyecto entero crecerá aquí.
- **`AGENTS.md`:** el agente sabe de qué va tu proyecto antes de que le pidas nada.
- **Cifras calculadas con código**, nunca inventadas.
- **Repo, Vercel, URL:** cada `git push` publica. Si no tiene URL, no existe.
