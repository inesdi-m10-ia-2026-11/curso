# Puesta al día: lo de ayer, en tu portátil

Módulo 10 · Sesión 2 · martes 24/11/2026

Hoy tus datos van a Supabase y tu app gana login. Para eso, lo de ayer tiene que estar en su sitio. Repasa esta lista con tu pareja de apoyo: cada punto dice cómo comprobarlo y qué hacer si no está.

**Orden de ayuda:** esta lista, quien ya tiene su URL (que ayude a quien no la tiene), yo.

¿Llegas más tarde por trabajo? Esta lista se hace sola: síguela con tu pareja de apoyo y, si a las 18:25 sigues atascado, búscame.

---

## Antes de nada: dos repos, cada uno con su papel

```
alumno-tu-nombre/            tu CUADERNO
│                            organización del curso · privado · solo tú y el docente
├── idea.md, datos.md, decisiones.md, bitacora/, prompts/, urls.md
└── apps/
    └── tu-proyecto/         tu APP
                             tu cuenta de GitHub · privado · la publica Vercel
        ├── web/             la página (Vercel: Root Directory = web)
        ├── datos/           tu CSV (si tus datos se pueden subir)
        ├── sql/             desde hoy: el SQL de Supabase
        └── AGENTS.md
```

- **El cuaderno** guarda lo que decides y lo que aprendes. Vercel no lo puede publicar: es un repo privado de una organización, y el plan gratis de Vercel no publica esos.
- **La app** es el código que se publica. Vive en tu cuenta y va enlazada dentro del cuaderno, en `apps/`, como submódulo.
- **Abre tu agente siempre en la carpeta de tu cuaderno.** El código de tu app está en `apps/tu-proyecto` y va a su propio repo: al subir, primero la app y después el cuaderno.

---

## La lista

| | Qué | Cómo lo compruebo | Si no está |
|---|---|---|---|
| [ ] 1 | Aceptadas las dos invitaciones de GitHub | En github.com/inesdi-m10-ia-2026-11 veo mi repo `alumno-...` | Busca en tu email "invited you", o entra en github.com/inesdi-m10-ia-2026-11 y acepta |
| [ ] 2 | Mi cuaderno clonado en mi portátil | Tengo la carpeta `alumno-...` y dentro `idea.md` | `git clone https://github.com/inesdi-m10-ia-2026-11/alumno-TU-NOMBRE.git` |
| [ ] 3 | Mi app en un repo **de mi cuenta**, enlazada en `apps/`, con `sergio-inesdi` invitado | Dentro del cuaderno hay `apps/tu-proyecto/web/index.html`; en el repo de la app, Settings, Collaborators, sale `sergio-inesdi` | Si tu `web/` está suelta en el cuaderno, o no tienes repo de app: prompt de `tu-app-en-tu-cuenta.md` (repo `curso`, sesión 1). Si falta la invitación: Settings, Collaborators, Add people, `sergio-inesdi` |
| [ ] 4 | Vercel publica **el repo de la app** | La URL que sale en mi proyecto de Vercel (Domains) abre en el móvil | Vercel, Add New, Project, el repo de tu app, Root Directory `web`, Framework Other, Deploy |
| [ ] 5 | Mi URL en `urls.md` y en el debate "Ideas y URLs" | La veo en los dos sitios (ayer el debate se quedó vacío) | Pídele a tu agente (en el cuaderno): "Apunta esta URL en urls.md, haz commit y push". En el debate: `Tu nombre · tu URL · tu idea en una frase` |
| [ ] 6 | Mi idea aprobada y mi CSV descargado | "Aprobada" en el debate; el CSV en mi portátil | Sin idea a las 17:30: una de las temáticas de ejemplo (`de-cero-a-url.md`, paso 0) con sus datos |

Con los seis, ayuda a tu pareja. Después, mira cuántas filas tiene tu CSV: si pasa de 100.000 filas o de 20 MB, pídele a tu agente una muestra (por ejemplo, las 5.000 filas más recientes) con un script.

---

## ¿No sube? La comprobación en cuatro pasos

Antes de llamarme, en la terminal, dentro de la carpeta que no sube:

1. `gh auth status`: tiene que decir `Logged in to github.com` con **tu** usuario.
2. `git config user.email`: tiene que ser el email **personal** de tu cuenta de GitHub. Si sale vacío, el de tu empresa o algo como `tu-nombre@MacBook.local`, tus commits no se enlazan a tu cuenta. Arréglalo con `git config --global user.email "tu-email@ejemplo.com"`.
3. `git push`: si pide usuario y contraseña, no la escribas: `gh auth login` y **Yes** a "Authenticate Git with your GitHub credentials".
4. Vercel: abre tu proyecto y mira el último despliegue. Si no hay ninguno nuevo, el push no llegó al repo de la app.

---

## Si algo falla

| Síntoma | Causa típica | Arreglo |
|---|---|---|
| `git push` pide usuario y contraseña | Git no usa tu sesión de `gh` | `gh auth login` y responde **Yes** a "Authenticate Git with your GitHub credentials" |
| `git push` dice "Permission denied" o "403" en el cuaderno | Invitación sin aceptar, o has entrado con otra cuenta | Acepta la invitación; `gh auth status` tiene que mostrar tu usuario |
| Vercel da 404 | Root Directory distinto de `web`, o el archivo no se llama `index.html` | Settings, Build and Deployment, Root Directory = `web`, y Redeploy |
| Vercel pide un código al conectar GitHub | GitHub confirma el permiso por email | El código llega a tu email. Da acceso solo al repo de tu app |
| Tu URL abre la web de otra persona | Has escrito la URL a mano con el nombre del repo | Tu URL es la que sale en tu proyecto de Vercel, en Domains |
| El repo de tu app solo tiene el README | El prompt de `tu-app-en-tu-cuenta.md` se quedó a medias | Síguelo desde el paso 3 |
| Tu agente ha montado Next.js, npm o un build que falla | Le has pedido "una app" sin decir cómo | Lo de ayer es un `index.html` en `web/`, HTML y CSS, sin frameworks. Pídeselo así |
| Vercel no ve tu repo | La app de Vercel no tiene permiso | En el import: Adjust GitHub App Permissions y da acceso al repo de tu app |
| Importaste el cuaderno en Vercel | Es el repo equivocado: privado y de la organización | Importa el repo de tu app. El proyecto del cuaderno lo puedes dejar, no molesta |
| `git submodule add` dice que el repo está vacío | El repo de la app se creó sin README | En github.com, Add a README, y repite |
| La carpeta `apps/tu-proyecto` está vacía | Clonaste el cuaderno sin submódulos | En el cuaderno: `git submodule update --init` |
| Tienes la app clonada dos veces (en `apps/` y en otra carpeta) | Ayer la clonaste aparte | Trabaja solo en `apps/tu-proyecto`. Antes de empezar, dentro: `git pull` |
| No puedes instalar nada (portátil de empresa) | Política de tu empresa | Edita en github.com (botón "." o Add file) y pide el código a un chat. Avísame al empezar |
